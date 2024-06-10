from __future__ import annotations

from protzilla.steps import Step, StepManager

from protzilla.customising.colorways import customise


class CustomisingStep(Step):
    section = "customising"

    def method(self, inputs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class ChangeColor(CustomisingStep):
    display_name = "Color"
    operation = "Color"
    method_description = "Change the colors of visualizations"
    input_keys = ["colors"]
    output_keys = ["colors"]
    #todo: naming needs more creativity

    def method(self, inputs):
        return customise(**inputs)
