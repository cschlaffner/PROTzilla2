import logging
import traceback

from django.forms import Form
from django.urls import reverse

from protzilla.run import Run
from protzilla.utilities import get_file_name_from_upload_path
from ui.runs.forms.custom_fields import CustomCharField, CustomFileField


class MethodForm(Form):
    is_dynamic = False

    def __init__(
        self,
        run: Run,
        readonly: bool = False,
        pretty_file_names: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.initial_fields = self.fields.copy()

        if readonly:
            self.replace_file_fields_with_paths(pretty_file_names)
            self.make_readonly()
        else:
            try:
                self.fill_form(run)
                for field_name, field in self.fields.items():
                    if hasattr(field, "choices"):
                        self.fields[field_name].choices = field.choices
            except Exception as e:
                logging.error(f"Error while filling form {e}: {traceback.format_exc()}")

        if self.is_dynamic:
            for field in self.fields.values():
                if not hasattr(field, "widget"):
                    continue
                if not hasattr(field.widget, "attrs"):
                    continue
                field.widget.attrs.update(
                    {
                        "hx-post": reverse(
                            "runs:fill_form", kwargs={"run_name": run.run_name}
                        ),
                        "hx-target": "#method-form",
                    }
                )

    def get_field(self, field_name: str):
        if field_name not in self.fields:
            raise ValueError(f"Field {field_name} not found in form.")
        if self.data.get(field_name):
            return self.data[field_name]
        if hasattr(self.fields[field_name], "default_value"):
            return self.fields[field_name].default_value
        return None

    def toggle_visibility(self, field_name: str, visible: bool) -> None:
        if field_name not in self.fields and not visible:
            logging.warning(f"Field {field_name} not found in form.")
            return
        if not visible:
            self.fields.pop(field_name)
        else:
            self.fields[field_name] = self.initial_fields[field_name]

    def fill_form(self, run: Run) -> None:
        pass

    def make_readonly(self) -> None:
        for field in self.fields.values():
            field.disabled = True

    def replace_file_fields_with_paths(self, pretty_file_names: bool) -> None:
        for field_name, field in self.fields.items():
            if not isinstance(field, CustomFileField):
                continue
            if field_name not in self.data:
                self.fields[field_name] = CustomCharField(
                    label=field.label, initial=None
                )
                continue
            file_name_to_show = self.data[field_name]
            if pretty_file_names:
                file_name_to_show = get_file_name_from_upload_path(file_name_to_show)
            self.fields[field_name] = CustomCharField(
                label=field.label, initial=file_name_to_show
            )

    def submit(self, run: Run) -> None:
        # add the missing fields to the form
        for field_name, field in self.initial_fields.items():
            if field_name not in self.fields:
                self.fields[field_name] = field
                self.cleaned_data[field_name] = None
        run.step_calculate(self.cleaned_data)
