from __future__ import annotations

from protzilla.steps import Step


class StepFactory:
    @staticmethod
    def create_step(step_type: str) -> Step:
        from ui.runs_v2.form_mapping import (
            get_all_methods,
        )  # to avoid a circular import

        for method in get_all_methods():
            if (
                    method.__name__ == step_type or method().method_id == step_type
            ):  # TODO make names consistent
                return method()
        raise ValueError(f"Unknown step type {step_type}")
