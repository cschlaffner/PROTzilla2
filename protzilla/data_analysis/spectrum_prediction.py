import json
from typing import Optional

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

AVAILABLE_MODELS = {
    "PrositIntensityHCD": {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_HCD/infer",
        "required_keys": [
            "peptide_sequences",
            "precursor_charges",
            "collision_energies",
        ],
    },
    "PrositIntensityCID": {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_CID/infer",
        "required_keys": ["peptide_sequences", "precursor_charges"],
    },
    "PrositIntensityXL_CMS3": {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2023_intensity_XL_CMS3/infer",
        "required_keys": ["peptide_sequences", "precursor_charges"],
    },
    # "PrositIntensityXL_CMS2": {
    #     "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2023_intensity_XL_CMS2/infer",
    #     "required_keys": ["peptide_sequences", "precursor_charges"]
    # },
}


class SpectrumPredictor:
    def __init__(self, prediction_df: pd.DataFrame, dissociation_method: str = "HCD"):
        self._verify_input(prediction_df)
        self.prediction_df = prediction_df
        self.dissociation_method = dissociation_method

    @staticmethod
    def create_prediction_df(
        peptide_sequences, charge: list[int] | range, nce: int = 30
    ):
        # Create a dataframe with the peptide sequences
        prediction_df = pd.DataFrame(peptide_sequences, columns=["Sequence"])
        if type(charge) == int:
            prediction_df["Charge"] = charge
        else:
            for c in charge:
                prediction_df = pd.concat(
                    [prediction_df, pd.DataFrame({"Charge": [c] * len(prediction_df)})],
                    ignore_index=True,
                )
        prediction_df["NCE"] = nce
        prediction_df.drop_duplicates(inplace=True)
        return prediction_df

    def predict(self):
        raise NotImplementedError(
            "This method should be implemented in the child class"
        )

    def _verify_input(self, prediction_df: pd.DataFrame | None = None):
        if prediction_df is None:
            prediction_df = self.prediction_df
        # Check if the input dataframe has the required columns
        if "Sequence" not in prediction_df.columns:
            raise ValueError("The input dataframe should have a 'Sequence' column")
        if "Charge" not in prediction_df.columns:
            raise ValueError("The input dataframe should have a 'Charge' column")
        if "NCE" not in prediction_df.columns:
            raise ValueError("The input dataframe should have a 'nce' column")


class KoinaModel(SpectrumPredictor):
    def __init__(
        self,
        prediction_df: pd.DataFrame,
        required_keys: list[str],
        dissociation_method: str = "HCD",
        url: str = None,
    ):
        super().__init__(prediction_df, dissociation_method)
        self.required_keys = required_keys
        self.KOINA_URL = (
            url
            if url
            else "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_HCD/infer"
        )

    def predict(self):
        predicted_spectra = []
        for i in range(0, len(self.prediction_df), 1000):
            to_predict = self.prediction_df[i : i + 1000]
            formatted_data = self.format_for_request(to_predict)
            response = requests.post(self.KOINA_URL, data=formatted_data)
            if response.status_code == 200:
                predicted_spectra.extend(
                    self.process_response(to_predict, response.json())
                )

            else:
                raise ValueError(f"Error in the request: {response.status_code}")
        return predicted_spectra

    def format_for_request(self, to_predict: pd.DataFrame) -> dict:
        inputs = []
        if (
            "peptide_sequences" in self.required_keys
            and "Sequence" in to_predict.columns
        ):
            inputs.append(
                {
                    "name": "peptide_sequences",
                    "shape": [len(to_predict), 1],
                    "datatype": "BYTES",
                    "data": to_predict["Sequence"].to_list(),
                }
            )
        if "precursor_charges" in self.required_keys and "Charge" in to_predict.columns:
            inputs.append(
                {
                    "name": "precursor_charges",
                    "shape": [len(to_predict), 1],
                    "datatype": "INT32",
                    "data": to_predict["Charge"].to_list(),
                }
            )
        if "collision_energies" in self.required_keys and "NCE" in to_predict.columns:
            inputs.append(
                {
                    "name": "collision_energies",
                    "shape": [len(to_predict), 1],
                    "datatype": "FP32",
                    "data": to_predict["NCE"].to_list(),
                }
            )
        return json.dumps(
            {
                "id": "0",
                "inputs": inputs,
            }
        )

    @staticmethod
    def process_response(request: pd.DataFrame, response: dict) -> pd.DataFrame:
        mz_index, intensity_index = 1, 2
        shape_mz = response["outputs"][mz_index]["shape"]
        shape_intensity = response["outputs"][intensity_index]["shape"]
        mz_values = np.reshape(response["outputs"][mz_index]["data"], shape_mz)
        intensity_values = np.reshape(
            response["outputs"][intensity_index]["data"], shape_intensity
        )
        # create Spectrum instances for each peptide
        spectra = []
        for i, (_, row) in tqdm(enumerate(request.iterrows()), total=len(request)):
            spectra.append(
                Spectrum(
                    row["Sequence"],
                    mz_values[i],
                    intensity_values[i],
                    {"Charge": row["Charge"]},
                )
            )
        return spectra


class SpectrumPredictorFactory:
    @staticmethod
    def create_predictor(model_name: str, prediction_df: pd.DataFrame):
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model '{model_name}' is not available.")
        return KoinaModel(prediction_df, **AVAILABLE_MODELS[model_name])


def predict(model_name: str, peptide_df: pd.DataFrame):
    prediction_df = SpectrumPredictor.create_prediction_df(
        peptide_df["Sequence"][::10], 2, 30
    )
    predictor = SpectrumPredictorFactory.create_predictor(model_name, prediction_df)
    predicted_spectra = predictor.predict()
    # merge df's into big df
    export_path = "/home/henning/test.msp"
    SpectrumExporter.export_to_msp(predicted_spectra, export_path)
    return {"export_path": export_path}


class Spectrum:
    def __init__(
        self,
        peptide_sequence: str,
        mz_values: np.array,
        intensity_values: np.array,
        metadata: Optional[dict] = None,
        sanitize: bool = True,
    ):
        self.peptide_sequence = peptide_sequence
        self.metadata = metadata if metadata else {}
        self.spectrum = pd.DataFrame(
            zip(mz_values, intensity_values), columns=["m/z", "Intensity"]
        )
        if sanitize:
            self._sanitize_spectrum()

    def __repr__(self):
        return f"{self.peptide_sequence}: {self.charge}, {self.spectrum.shape[0]} peaks"

    def _sanitize_spectrum(self):
        self.spectrum = self.spectrum.drop_duplicates(subset="m/z")
        self.spectrum = self.spectrum[self.spectrum["Intensity"] > 0]

    def to_mergeable_df(self):
        return self.spectrum.assign(Sequence=self.peptide_sequence, Charge=self.charge)


class SpectrumExporter:
    @staticmethod
    def export_to_msp(spectra: list[Spectrum], path: str):
        with open(path, "w") as f:
            for spectrum in spectra:
                header_dict = {
                    "Name": spectrum.peptide_sequence,
                    "Comment": "".join(
                        [f"{k}={v} " for k, v in spectrum.metadata.items()]
                    ),
                    "Num Peaks": len(spectrum.spectrum),
                }
                header = "\n".join([f"{k}: {v}" for k, v in header_dict.items()])
                peaks = "\n".join(
                    [f"{mz}\t{intensity}" for mz, intensity in spectrum.spectrum.values]
                )
                f.write(f"{header}\n{peaks}\n\n")

    @staticmethod
    def export_to_mgf(spectra: list[Spectrum], path: str):
        with open(path, "w") as f:
            for spectrum in spectra:
                header_dict = {
                    "Name": spectrum.peptide_sequence,
                    "Comment": "".join(
                        [f"{k}={v} " for k, v in spectrum.metadata.items()]
                    ),
                    "Num Peaks": len(spectrum.spectrum),
                }
                header = "\n".join([f"{k}: {v}" for k, v in header_dict.items()])
                peaks = "\n".join(
                    [f"{mz}\t{intensity}" for mz, intensity in spectrum.spectrum.values]
                )
                f.write(f"{header}\n{peaks}\n\n")
