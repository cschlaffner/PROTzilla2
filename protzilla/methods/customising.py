from __future__ import annotations

from protzilla.steps import Step, StepManager

from protzilla.customising.accessibility import color_choice_method, enhanced_reading_method


class CustomisingStep(Step):
    section = "customising"

    def method(self, inputs):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class ChangeColor(CustomisingStep):
    display_name = "Color"
    operation = "Color"
    method_description = "Change the color scheme of visualizations, helpful for colorblind and low vision users"
    input_keys = ["colors", "custom_colors"]
    output_keys = ["colors"]

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        if inputs["custom_colors"] == "":
            inputs["custom_colors"] = None
        return inputs

    def method(self, inputs):
        return color_choice_method(**inputs)


class EnhancedReading(CustomisingStep):
    display_name = "Enhanced Reading"
    operation = "Reading"
    method_description = "Enhance reading experience by changing size and spacing of text"
    input_keys = ["enhanced_reading"]
    output_keys = ["enhanced_reading"]

    def method(self, inputs):
        return enhanced_reading_method(**inputs)
