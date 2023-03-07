from django import forms


class MSImportForm(forms.Form):
    intensity_file = forms.FileField(
        label="Upload Intensity File",
    )
    intensity_name = forms.CharField(
        label="Select Intensity Name",
        widget=forms.Select(
            [
                ("Intensity", "Intensity"),
                ("iBAQ", "iBAQ"),
                ("LFQ intensity", "LFQ intensity"),
            ]
        ),
    )
    ms_data_type = forms.CharField(
        label="Select MS Data Type",
        widget=forms.Select([("ms_fragger", "MS Fragger"), ("max_quant", "Max Quant")]),
    )

    metadata_file = forms.FileField(
        label="Upload Intensity File",
    )
