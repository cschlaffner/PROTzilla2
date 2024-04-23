from django.forms import Form

from protzilla.run_v2 import Run
from ui.runs_v2.forms.custom_fields import CustomCharField, CustomFileField


class MethodForm(Form):
    def __init__(self, run: Run, readonly: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if readonly:
            self.replace_file_fields_with_paths()
            self.make_readonly()
        else:
            self.fill_form(run)

    def fill_form(self, run: Run) -> None:
        pass

    def make_readonly(self) -> None:
        for field in self.fields.values():
            field.disabled = True

    def replace_file_fields_with_paths(self) -> None:
        for field_name, field in self.fields.items():
            if type(field) == CustomFileField:
                self.fields[field_name] = CustomCharField(
                    label=field.label, initial=self.data[field_name]
                )

    def submit(self, run: Run) -> None:
        run.step_calculate(self.cleaned_data)
