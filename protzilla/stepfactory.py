from __future__ import annotations

from protzilla.methods.data_preprocessing import ImputationMinPerProtein
from protzilla.methods.importing import MaxQuantImport, MetadataImport
from protzilla.steps import Step


class StepFactory:
    # TODO this could be done with the new mapping class, iterating and checking whether there exists a step with that specific name
    @staticmethod
    def create_step(step_type: str) -> Step:
        from ui.runs_v2.form_mapping import (
            get_all_methods,
        )  # to avoid a circular import

        for method in get_all_methods():
            if method.__name__ == step_type:
                return method
        raise ValueError(f"Unknown step type {step_type}")
        if step_type == "MaxQuantImport" or step_type == "max_quant_import":
            return MaxQuantImport()
        elif (
            step_type == "ImputationMinPerProtein" or step_type == "by_min_per_protein"
        ):
            return ImputationMinPerProtein()
        elif step_type == "MetadataImport" or step_type == "metadata_import_method":
            return MetadataImport()
        else:
            raise ValueError(f"Unknown step type {step_type}")
