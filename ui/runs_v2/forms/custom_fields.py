from enum import Enum

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


# Custom Fields


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


class CustomMultipleChoiceField(MultipleChoiceField):
    def __init__(self, choices: Enum, initial=None, *args, **kwargs):
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
        return cleaned.file.file.name


class CustomBooleanField(BooleanField):
    def __init__(self, label: str, *args, **kwargs):
        super().__init__(label="", *args, **kwargs)
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
