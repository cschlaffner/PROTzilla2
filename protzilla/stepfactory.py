from __future__ import annotations

from protzilla.steps import Step, StepManager


class StepFactory:
    @staticmethod
    def create_step(step_type: str, steps: StepManager) -> Step:
        """
        Returns a step instance of the a step of the given type.
        :param step_type: The type of step to create. Is the name of the step class.
        :param steps: The StepManager instance to which the step should be added.
        :return: The created step instance.
        """
        from ui.runs_v2.form_mapping import (
            get_all_methods,
        )  # to avoid a circular import

        for method in get_all_methods():
            if method.__name__ == step_type:
                instance_count = len(
                    [
                        instance
                        for instance in steps.all_steps
                        if isinstance(instance, method)
                    ]
                )
                return method(instance_identifier=f"{step_type}_{instance_count + 1}")
        raise ValueError(f"Unknown step type {step_type}")
