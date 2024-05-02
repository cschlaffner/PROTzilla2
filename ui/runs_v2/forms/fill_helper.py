from protzilla.run_v2 import Run
from protzilla.steps import Step


def to_choices(choices: list[str]) -> list[tuple[str, str]]:
    return [(el, el) for el in choices]


def get_choices_for_protein_df_steps(run: Run) -> list[tuple[str, str]]:
    return to_choices(run.steps.get_instance_identifiers(Step, "protein_df"))


def get_choices_for_metadata_non_sample_columns(run: Run) -> list[tuple[str, str]]:
    return to_choices(
        run.steps.metadata_df.columns[
            run.steps.metadata_df.columns != "Sample"
        ].unique()
    )
