from django.forms import Form

from protzilla.run import Run


class MethodForm(Form):
    def __init__(self, run: Run, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fill_form(run)

    @property
    def description(self) -> str:
        raise NotImplementedError

    def fill_form(self, run: Run):
        pass

    def submit(self, run: Run):
        raise NotImplementedError
