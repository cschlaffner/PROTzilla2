from django.forms import Form
from django.urls import reverse

from protzilla.run_v2 import Run
from protzilla.utilities import get_file_name_from_upload_path
from ui.runs_v2.forms.custom_fields import CustomCharField, CustomFileField


class MethodForm(Form):
    is_dynamic = False

    def __init__(
        self,
        run: Run,
        readonly: bool = False,
        pretty_file_names: bool = True,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        if readonly:
            self.replace_file_fields_with_paths(pretty_file_names)
            self.make_readonly()
        else:
            self.fill_form(run)

        if self.is_dynamic:
            for field in self.fields.values():
                field.widget.attrs.update(
                    {
                        "hx-post": reverse(
                            "runs_v2:fill_form", kwargs={"run_name": run.run_name}
                        ),
                        "hx-target": "#method-form",
                    }
                )

    def fill_form(self, run: Run) -> None:
        pass

    def make_readonly(self) -> None:
        for field in self.fields.values():
            field.disabled = True

    def replace_file_fields_with_paths(self, pretty_file_names: bool) -> None:
        for field_name, field in self.fields.items():
            if type(field) == CustomFileField:
                file_name_to_show = self.data[field_name]
                if pretty_file_names:
                    file_name_to_show = get_file_name_from_upload_path(
                        file_name_to_show
                    )
                self.fields[field_name] = CustomCharField(
                    label=field.label, initial=file_name_to_show
                )

    def submit(self, run: Run) -> None:
        run.step_calculate(self.cleaned_data)
