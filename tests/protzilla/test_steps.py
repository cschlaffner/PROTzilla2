import pytest

from protzilla.disk_operator import DiskOperator
from protzilla.methods.data_preprocessing import ImputationByMinPerProtein
from protzilla.methods.importing import MaxQuantImport
from protzilla.steps import Section, Step, StepManager


class TestStepManager:
    @pytest.fixture
    def step_manager(self):
        disk_operator = DiskOperator("test_run", "test_workflow")
        return StepManager(disk_operator=disk_operator)

    def test_add_step(self, step_manager):
        assert len(step_manager.importing) == 0
        step = Step()
        step.section = Section.IMPORTING.value
        step_manager.add_step(step)
        assert len(step_manager.importing) == 1
        assert step_manager.current_step == step

    def test_remove_step(self, step_manager):
        step = MaxQuantImport()
        step_manager.add_step(step)
        assert len(step_manager.importing) == 1
        step_manager.remove_step(step)
        assert len(step_manager.importing) == 0
        assert step_manager.current_step is None

    def test_current_step(self, step_manager):
        assert step_manager.current_step is None
        step = Step()
        step.section = Section.IMPORTING.value
        step_manager.add_step(step)
        assert step_manager.current_step == step

    def test_next_step(self, step_manager):
        step1 = MaxQuantImport()
        step1.section = Section.IMPORTING.value
        step_manager.add_step(step1)

        step2 = ImputationByMinPerProtein()
        step2.section = Section.DATA_PREPROCESSING.value
        step_manager.add_step(step2)

        assert step_manager.current_step == step1
        step_manager.next_step()
        assert step_manager.current_step == step2

    def test_previous_step(self, step_manager):
        with pytest.raises(ValueError):
            step_manager.previous_step()

        step1 = Step()
        step1.section = Section.IMPORTING.value
        step_manager.add_step(step1)

        step2 = Step()
        step2.section = Section.DATA_PREPROCESSING.value
        step_manager.add_step(step2)

        assert step_manager.current_step == step1
        step_manager.next_step()
        assert step_manager.current_step == step2
        step_manager.previous_step()
        assert step_manager.current_step == step1

    def test_all_steps(self, step_manager):
        assert len(step_manager.all_steps) == 0
        step1 = Step()
        step1.section = Section.IMPORTING.value
        step_manager.add_step(step1)

        step2 = Step()
        step2.section = Section.DATA_PREPROCESSING.value
        step_manager.add_step(step2)

        assert len(step_manager.all_steps) == 2
        assert step_manager.all_steps[0] == step1
        assert step_manager.all_steps[1] == step2

    def test_all_steps_in_section(self, step_manager):
        assert len(step_manager.all_steps_in_section(Section.IMPORTING.value)) == 0
        step = MaxQuantImport()
        step_manager.add_step(step)
        assert len(step_manager.all_steps_in_section(Section.IMPORTING.value)) == 1
        assert step_manager.all_steps_in_section(Section.IMPORTING.value)[0] == step
        step_manager.remove_step(step)
        assert len(step_manager.all_steps_in_section(Section.IMPORTING.value)) == 0

    def test_goto_step(self, step_manager):
        step1 = Step()
        step1.section = Section.IMPORTING.value
        step_manager.add_step(step1)

        step2 = Step()
        step2.section = Section.DATA_PREPROCESSING.value
        step_manager.add_step(step2)

        step_manager.current_step_index = 1
        step_manager.goto_step(0, Section.IMPORTING.value)
        assert step_manager.current_step == step1

    def test_invalid_goto_step(self, step_manager):
        with pytest.raises(ValueError):
            step_manager.goto_step(0, "invalid_section")

        with pytest.raises(ValueError):
            step_manager.goto_step(0, Section.IMPORTING.value)

        with pytest.raises(ValueError):
            step_manager.goto_step(1, "invalid_section")

        with pytest.raises(ValueError):
            step_manager.goto_step(1, Section.DATA_PREPROCESSING.value)

        step1 = Step()
        step1.section = Section.IMPORTING.value
        step_manager.add_step(step1)

        step2 = Step()
        step2.section = Section.DATA_PREPROCESSING.value
        step_manager.add_step(step2)

        with pytest.raises(ValueError):
            step_manager.goto_step(0, "invalid_section")

        with pytest.raises(ValueError):
            step_manager.goto_step(2, Section.IMPORTING.value)
