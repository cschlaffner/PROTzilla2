from __future__ import annotations

from protzilla.steps import Step, StepManager


class StepFactory:
    @staticmethod
    def create_step(
        step_type: str, steps: StepManager, instance_identifier: str | None = None
    ) -> Step:
        """
        Returns an instance of a step of the given type.
        :param step_type: The type of step to create. Is the name of the step class.
        :param steps: The StepManager instance to which the step should be added.
        :param instance_identifier: The identifier of the step instance. Will be generated based on steps if not provided.
        :return: The created step instance.
        """
        from ui.runs.form_mapping import get_all_methods

        if not step_type:
            raise ValueError("No step type provided.")

        for method in get_all_methods():
            if method.__name__ == step_type:
                if instance_identifier:
                    return method(instance_identifier=instance_identifier)
                instance_count = len(
                    [
                        instance
                        for instance in steps.all_steps
                        if isinstance(instance, method)
                    ]
                )
                return method(instance_identifier=f"{step_type}_{instance_count + 1}")
        raise ValueError(f"Unknown step type {step_type}")
