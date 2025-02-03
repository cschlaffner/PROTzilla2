import re

from protzilla.run import Run
from protzilla.steps import Step


def to_choices(choices: list[str], required: bool = True) -> list[tuple[str, str]]:
    return (
        [(el, el) for el in choices] + [(None, "---------")]
        if not required
        else [(el, el) for el in choices]
    )


def get_choices_for_protein_df_steps(run: Run) -> list[tuple[str, str]]:
    return reversed(to_choices(run.steps.get_instance_identifiers(Step, "protein_df")))


def get_choices(
    run: Run, output_key: str, step_type: type[Step] = Step
) -> list[tuple[str, str]]:
    """
    Returns the instance identifiers containing the passed output key.
    :param run: the run object
    :param output_key: the output key (e.g. "protein_df" or "enrichment_df"
    :return: a list of tuples containing the instance identifier and the instance identifier
    """
    return reversed(
        to_choices(run.steps.get_instance_identifiers(step_type, output_key))
    )


def get_choices_for_metadata_non_sample_columns(run: Run) -> list[tuple[str, str]]:
    return to_choices(
        run.steps.metadata_df.columns[
            run.steps.metadata_df.columns != "Sample"
        ].unique()
    )


def enclose_links_in_html(text):
    url_pattern = r"(https?://\S+|www\.\S+)"

    def replace_with_href(match):
        url = match.group(0)
        if url.startswith("www."):
            url = "http://" + url
        return f'<a href="{url}">{url}</a>'

    return re.sub(url_pattern, replace_with_href, text)
