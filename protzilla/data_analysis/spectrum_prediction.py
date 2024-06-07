import json

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm


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


class PrositPredictor(SpectrumPredictor):
    KOINA_URL = "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_HCD/infer"

    def __init__(self, prediction_df: pd.DataFrame, dissociation_method: str = "HCD"):
        super().__init__(prediction_df, dissociation_method)

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

    @staticmethod
    def format_for_request(to_predict: pd.DataFrame) -> dict:
        return json.dumps(
            {
                "id": "0",
                "inputs": [
                    {
                        "name": "peptide_sequences",
                        "shape": [len(to_predict), 1],
                        "datatype": "BYTES",
                        "data": to_predict["Sequence"].to_list(),
                    },
                    {
                        "name": "precursor_charges",
                        "shape": [len(to_predict), 1],
                        "datatype": "INT32",
                        "data": to_predict["Charge"].to_list(),
                    },
                    {
                        "name": "collision_energies",
                        "shape": [len(to_predict), 1],
                        "datatype": "FP32",
                        "data": to_predict["NCE"].to_list(),
                    },
                ],
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
                    row["Sequence"], row["Charge"], mz_values[i], intensity_values[i]
                )
            )
        return spectra


def predict_with_prosit(peptide_df: pd.DataFrame):
    prediction_df = PrositPredictor.create_prediction_df(peptide_df["Sequence"], 2, 30)
    predictor = PrositPredictor(prediction_df)
    predictor.predict()
    return dict(predicted_spectra=predictor.prediction_df)


class Spectrum:
    def __init__(
        self,
        peptide_sequence: str,
        charge: int,
        mz_values: np.array,
        intensity_values: np.array,
        sanitize: bool = True,
    ):
        self.peptide_sequence = peptide_sequence
        self.charge = charge
        self.spectrum = pd.DataFrame(
            zip(mz_values, intensity_values), columns=["m/z", "Intensity"]
        )
        if sanitize:
            self._sanitize_spectrum()

    def _sanitize_spectrum(self):
        self.spectrum = self.spectrum.drop_duplicates(subset="m/z")
        self.spectrum = self.spectrum[self.spectrum["Intensity"] > 0]
