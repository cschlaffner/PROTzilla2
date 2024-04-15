from django.forms import Form

from protzilla.run import Run
from ui.runs_v2.forms.custom_fields import CustomCharField, CustomFileField


class MethodForm(Form):
    def __init__(self, run: Run, readonly: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fill_form(run)

        if readonly:
            self.replace_file_fields_with_paths()
            self.make_readonly()

    def fill_form(self, run: Run):
        pass

    def make_readonly(self):
        for field in self.fields.values():
            field.disabled = True

    def replace_file_fields_with_paths(self):
        for field_name, field in self.fields.items():
            if type(field) == CustomFileField:
                self.fields[field_name] = CustomCharField(
                    label=field.label, initial=self.data[field_name]
                )

    def submit(self, run: Run):
        raise NotImplementedError
