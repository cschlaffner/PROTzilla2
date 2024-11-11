import logging

from protzilla.methods.data_preprocessing import ImputationByMinPerProtein
from protzilla.methods.importing import MaxQuantImport


class TestRun:
    def test_init_standard(self, run_standard):
        assert run_standard.workflow_name == "standard"
        assert run_standard.steps is not None
        assert run_standard.current_step is not None
        assert run_standard.steps.current_step_index == 0
        assert run_standard.steps.current_section == "importing"

    def test_init_empty(self, run_empty):
        assert run_empty.workflow_name == "test-run-empty"
        assert run_empty.steps is not None
        assert len(run_empty.steps.all_steps) == 0
        assert run_empty.current_step is None
        assert run_empty.steps.current_step_index == 0

    def test_init_imported(self, run_imported):
        assert run_imported.workflow_name == "test-run-empty"
        assert run_imported.steps is not None and len(run_imported.steps.all_steps) == 1
        assert (
            run_imported.current_step.output["protein_df"] is not None
            and not run_imported.current_step.output["protein_df"].empty
        )
        assert run_imported.steps.current_step_index == 0
        assert run_imported.steps.current_section == "importing"

    def test_step_add(self, run_imported):
        step = ImputationByMinPerProtein()
        length_before = len(run_imported.steps.all_steps)
        run_imported.step_add(step)
        assert len(run_imported.steps.all_steps) == length_before + 1

    def test_step_remove(self, run_imported):
        step = ImputationByMinPerProtein()
        run_imported.step_add(step)
        length_before = len(run_imported.steps.all_steps)
        run_imported.step_remove(step)
        assert len(run_imported.steps.all_steps) == length_before - 1

    def test_step_calculate(self, run_empty, maxquant_data_file):
        step = MaxQuantImport()
        run_empty.step_add(step)
        run_empty.step_calculate(
            inputs={
                "file_path": maxquant_data_file,
                "map_to_uniprot": False,
                "intensity_name": "Intensity",
                "aggregation_method": "Sum",
            }
        )
        assert run_empty.current_step.output["protein_df"] is not None
        assert not run_empty.current_step.output["protein_df"].empty

    def test_step_plot(self, run_imported):
        step = ImputationByMinPerProtein()
        run_imported.step_add(step)
        run_imported.step_next()
        run_imported.step_calculate(inputs={"shrinking_value": 0.5})
        assert run_imported.current_step == step
        run_imported.step_plot(
            inputs={
                "graph_type": "Boxplot",
                "graph_type_quantities": "Pie chart",
                "group_by": "None",
                "visual_transformation": "linear",
            }
        )
        print(run_imported.current_step.plots)
        assert not run_imported.current_step.plots.empty

    def test_step_next(self, run_imported):
        step = ImputationByMinPerProtein()
        run_imported.step_add(step)
        assert run_imported.current_step != step
        run_imported.step_next()
        assert run_imported.current_step == step

    def test_step_previous(self, run_imported):
        step = ImputationByMinPerProtein()
        run_imported.step_add(step)
        run_imported.step_next()
        assert run_imported.current_step == step
        run_imported.step_previous()
        assert run_imported.current_step != step

    def test_step_goto(self, caplog, run_imported):
        step = ImputationByMinPerProtein()
        run_imported.step_add(step)
        run_imported.step_goto(0, "data_preprocessing")
        assert any(
            message["level"] == logging.ERROR and "ValueError" in message["msg"]
            for message in run_imported.current_messages
        ), "No error messages found in run.current_messages"
        assert run_imported.current_step != step
        run_imported.step_next()
        assert run_imported.current_step == step
        run_imported.step_goto(0, "importing")
        assert run_imported.current_step == run_imported.steps.all_steps[0]

    def test_step_change_method(self, run_imported):
        run_imported.step_change_method("DiannImport")
        assert run_imported.current_step.__class__.__name__ == "DiannImport"
