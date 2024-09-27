import json
import logging
from enum import Enum

import django.forms as forms
from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    DecimalField,
    FileField,
    FloatField,
    MultipleChoiceField,
)
from django.forms.widgets import CheckboxInput, SelectMultiple
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe

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


from django import forms
from django.utils.safestring import mark_safe


class TextDisplayWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update()

    def render(self, name, value, attrs=None, renderer=None):
        display_text = self.attrs.get("data-display-text", "")
        return mark_safe(f"<div class=form-control mb-2>{display_text}</div>")


class TextDisplayField(forms.Field):
    widget = TextDisplayWidget

    def __init__(self, *args, **kwargs):
        self.text = kwargs.pop("text", "")
        kwargs["required"] = False
        super().__init__(*args, **kwargs)
        self.update_text()

    def update_text(self, text=None):
        if text is not None:
            self.text = text
        self.widget.attrs["data-display-text"] = self.text
