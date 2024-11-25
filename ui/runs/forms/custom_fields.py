import logging
from enum import Enum

from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    DecimalField,
    FileField,
    FloatField,
    MultipleChoiceField,
    Select
)
from django.forms.widgets import CheckboxInput, SelectMultiple
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe
from django.template.loader import render_to_string

# Custom widgets


class CustomCheckBoxInput(CheckboxInput):
    def __init__(self, label: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

    def render(self, name, value, attrs=None, renderer=None) -> SafeText:
        input_html = super().render(name, value, attrs, renderer)
        label_html = format_html(
            '<label for="{id}"> {text} </label>', id=attrs["id"], text=self.label
        )
        return format_html('<div class="mb-2">{} {}</div>', input_html, label_html)


class CustomSelectMultiple(SelectMultiple):
    # This is a workaround to add a hidden option to the select multiple widget that is always selected.
    # Otherwise the dynamic filling does not work properly.
    def render(self, name, value, attrs=None, renderer=None) -> SafeText:
        input_html = super().render(name, value, attrs, renderer)
        hidden_option_html = mark_safe(
            "<option value='hidden' style='display: none;' selected>Hidden option</option>"
        )
        idx = input_html.find(">") + 1
        return mark_safe(f"{input_html[:idx]}{hidden_option_html}{input_html[idx:]}")


class CustomChoiceField(ChoiceField):
    def __init__(self, choices: Enum | list, initial=None, *args, **kwargs):
        if isinstance(choices, list):
            super().__init__(choices=choices, initial=initial, *args, **kwargs)
        else:
            super().__init__(
                choices=[(el.value, el.value) for el in choices],
                initial=initial,
                *args,
                **kwargs,
            )

        if not self.required:
            self.choices += [(None, "---------")]

        self.widget.attrs.update({"class": "form-select mb-2"})

    @property
    def default_value(self):
        if len(self.choices) > 0:
            # we need to unpack the tuple, thats why we need to use [0][0]
            if isinstance(self.choices[0], tuple):
                return self.choices[0][0]
            return self.choices[0]
        logging.warning("Attempted to get default value of empty choice field.")
        return None


class CustomMultipleChoiceField(MultipleChoiceField):
    def __init__(self, choices: Enum | list, initial=None, *args, **kwargs):
        if isinstance(choices, list):
            super().__init__(choices=choices, initial=initial, *args, **kwargs)
        else:
            super().__init__(
                choices=[(el.value, el.value) for el in choices],
                initial=initial,
                *args,
                **kwargs,
            )
        self.widget = CustomSelectMultiple()
        self.widget.attrs.update({"class": "form-select mb-2"})

    def clean(self, value: list[str] | None):
        return [el for el in value if el != "hidden"] if value else None

class CustomCheckboxMultipleChoiceField(MultipleChoiceField):
    def __init__(self, choices: Enum | list, initial=None, *args, **kwargs):
        if isinstance(choices, list):
            super().__init__(choices=choices, initial=initial, *args, **kwargs)
        else:
            super().__init__(
                choices=[(el.value, el.value) for el in choices],
                initial=initial,
                *args,
                **kwargs,
            )

        self.color_selectors = {
            choice_value: CustomColorSelectField()
            for choice_value, _ in self.choices
        }

        self.widget = CustomCheckboxSelectMultipleWidget(color_selectors=self.color_selectors)
        self.widget.attrs.update({"class": "form-select mb-2"})

    def clean(self, value: list[str] | None):
        return [el for el in value if el != "hidden"] if value else None

# Widget
class CustomCheckboxSelectMultipleWidget(SelectMultiple):
    def __init__(self, *args, color_selectors=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_selectors = color_selectors or {}

    def render(self, name, value, attrs=None, renderer=None) -> SafeText:
        output = ['<div class="checkbox-container border p-3 rounded">']
        value = value or []

        if self.color_selectors == {}:
            self.color_selectors = { choice_value: CustomColorSelectField(choice_value=choice_value) for choice_value, _ in self.choices }

        for i, (option_value, option_label) in enumerate(self.choices):
            id = f"{name}_{option_label}"

            color_selector = self.color_selectors.get(option_value, CustomColorSelectField())

            output.append(
                render_to_string(
                    "runs/field_component_color_selection.html",
                    context=dict(
                        id=f"{id}_checkbox",
                        option_label=option_label,
                        option_value=option_value,
                        name=name,
                        color_selector_render=color_selector.widget.render(name, f"{id}_color_selector" )
                        ),
                    ),
                )
            
        output.append('</div>') 
        return mark_safe("\n".join(output))
    
class CustomColorSelectField(ChoiceField):
    def __init__(self, choice_value=None, *args, **kwargs):
        kwargs["widget"] = CustomColorSelectWidget()
        super().__init__(*args, **kwargs)
        self.widget = CustomColorSelectWidget(choice_value=choice_value)

class CustomColorSelectWidget(Select):
    def __init__(self, choice_value=None, *args, **kwargs):
        options = kwargs.pop("options", [
            (f"color_{choice_value}_red", "Red"),
            (f"color_{choice_value}_blue", "Blue"),
        ])
        super().__init__(*args, choices=options, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs["class"] = "form-select"
        return super().render(name, value, attrs=attrs, renderer=renderer)





class CustomFileField(FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs.update({"class": "form-control mb-2"})

    def clean(self, data, initial=None):
        cleaned = super().clean(data, initial)
        if cleaned is not None:
            return cleaned.file.file.name
        return ""


class CustomBooleanField(BooleanField):
    def __init__(self, label: str, required=False, *args, **kwargs):
        super().__init__(label="", required=required, *args, **kwargs)
        self.widget = CustomCheckBoxInput(label=label)


class CustomNumberField(DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs.update({"class": "form-control mb-2"})

    def clean(self, data, initial=None):
        cleaned = super().clean(data)
        return int(cleaned)  # we cannot work with type Decimal


class CustomCharField(CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs.update({"class": "form-control mb-2"})


class CustomFloatField(FloatField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs.update({"class": "form-control mb-2"})
