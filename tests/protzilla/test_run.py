from pathlib import Path
from shutil import rmtree
import logging

import pytest

from protzilla.constants import paths
from protzilla.methods.data_preprocessing import ImputationByMinPerProtein
from protzilla.methods.importing import MaxQuantImport
from protzilla.run_v2 import Run


class TestRun:
    @pytest.fixture
    def run_standard(
            self,
    ):
        # delete the previous run
        run_path = Path(paths.RUNS_PATH) / "test_run"
        if run_path.exists():
            rmtree(run_path)
        yield Run(run_name="test_run", workflow_name="standard")
        rmtree(run_path)

    @pytest.fixture
    def run_empty(self):
        run_path = Path(paths.RUNS_PATH) / "test_run"
        if run_path.exists():
            rmtree(run_path)
        yield Run(run_name="test_run", workflow_name="test-run-empty")
        rmtree(run_path)

    @pytest.fixture
    def run(self, run_empty, maxquant_data_file):
        run_empty.step_add(MaxQuantImport())
        run_empty.step_calculate(
            {
                "file_path": str(maxquant_data_file),
                "intensity_name": "iBAQ",
                "map_to_uniprot": False,
            }
        )
        return run_empty

    @pytest.fixture
    def maxquant_data_file(self):
        return str(
            (
                    Path(paths.TEST_DATA_PATH) / "MaxQuant_data" / "proteinGroups.txt"
            ).absolute()
        )

    def test_init_standard(self, run_standard):
        assert run_standard.run_name == "test_run"
        assert run_standard.workflow_name == "standard"
        assert run_standard.steps is not None
        assert run_standard.current_step is not None
        assert run_standard.steps.current_step_index == 0
        assert run_standard.steps.current_section == "importing"

    def test_init_empty(self, run_empty):
        assert run_empty.run_name == "test_run"
        assert run_empty.workflow_name == "test-run-empty"
        assert run_empty.steps is not None
        assert len(run_empty.steps.all_steps) == 0
        assert run_empty.current_step is None
        assert run_empty.steps.current_step_index == 0

    def test_step_add(self, run):
        step = ImputationByMinPerProtein()
        length_before = len(run.steps.all_steps)
        run.step_add(step)
        assert len(run.steps.all_steps) == length_before + 1

    def test_step_remove(self, run):
        step = ImputationByMinPerProtein()
        run.step_add(step)
        length_before = len(run.steps.all_steps)
        run.step_remove(step)
        assert len(run.steps.all_steps) == length_before - 1

    def test_step_calculate(self, run, maxquant_data_file):
        run.step_calculate(inputs={"protein_df": maxquant_data_file})
        assert run.current_step.output["protein_df"] is not None

    def test_step_plot(self, run):
        step = ImputationByMinPerProtein()
        run.step_add(step)
        run.step_next()
        run.step_calculate(inputs={"shrinking_value": 0.5})
        assert run.current_step == step
        run.step_plot()  # TODO Plots are broken, waiting for fix
        assert not run.current_step.plots.empty

    def test_step_next(self, run):
        step = ImputationByMinPerProtein()
        run.step_add(step)
        assert run.current_step != step
        run.step_next()
        assert run.current_step == step

    def test_step_previous(self, run):
        step = ImputationByMinPerProtein()
        run.step_add(step)
        run.step_next()
        assert run.current_step == step
        run.step_previous()
        assert run.current_step != step

    def test_step_goto(self, caplog, run):
        step = ImputationByMinPerProtein()
        run.step_add(step)
        run.step_goto(0, "data_preprocessing")
        assert any(
            message["level"] == logging.ERROR and
            "ValueError" in message["msg"]
            for message in run.current_messages
        ), "No error messages found in run.current_messages"
        assert run.current_step != step
        run.step_next()
        assert run.current_step == step
        run.step_goto(0, "importing")
        assert run.current_step == run.steps.all_steps[0]

    def test_step_change_method(self, run):
        run.step_change_method("DiannImport")
        assert run.current_step.__class__.__name__ == "DiannImport"
