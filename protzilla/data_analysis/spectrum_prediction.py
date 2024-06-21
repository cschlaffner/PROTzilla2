import asyncio
import json
import logging
from typing import Optional

import aiohttp
import numpy as np
import pandas as pd
from pyteomics.mass import mass
from tqdm import tqdm

from protzilla.constants.protzilla_logging import logger
from protzilla.disk_operator import FileOutput

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

AVAILABLE_FORMATS = ["msp", "csv"]


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
        self.preprocess()

    def preprocess(self):
        pass

    def predict(self):
        predicted_spectra = []
        slices_to_predict = [
            self.prediction_df[i : i + 1000].index
            for i in range(0, len(self.prediction_df), 1000)
        ]
        formatted_data = [
            self.format_for_request(self.prediction_df.loc[slice])
            for slice in slices_to_predict
        ]
        response_data = asyncio.run(self.make_request(formatted_data))
        for indices, response in tqdm(
            zip(slices_to_predict, response_data),
            desc="Processing predictions",
            total=len(slices_to_predict),
        ):
            predicted_spectra.extend(
                self.process_response(self.prediction_df.loc[indices], response)
            )
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

    async def make_request(self, formatted_data: list[dict]):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for data in formatted_data:
                tasks.append(session.post(self.KOINA_URL, data=data))
            responses = await asyncio.gather(*tasks)
            data = []
            for response in responses:
                if response.status != 200:
                    logging.error(f"Error in response: {response.status}")
                    logging.error(await response.text())
                    continue
                data.append(await response.json())
        return data

    @staticmethod
    def process_response(request: pd.DataFrame, response: dict) -> pd.DataFrame:
        mz_index, intensity_index, fragment_type_index = 1, 2, 0
        shape_mz = response["outputs"][mz_index]["shape"]
        shape_intensity = response["outputs"][intensity_index]["shape"]
        shape_fragment_type = response["outputs"][fragment_type_index]["shape"]
        mz_values = np.reshape(response["outputs"][mz_index]["data"], shape_mz)
        intensity_values = np.reshape(
            response["outputs"][intensity_index]["data"], shape_intensity
        )
        fragment_types = np.reshape(
            response["outputs"][fragment_type_index]["data"], shape_fragment_type
        )
        # create Spectrum instances for each peptide
        spectra = []
        for i, (_, row) in enumerate(request.iterrows()):
            spectra.append(
                Spectrum(
                    row["Sequence"],
                    row["Charge"],
                    mz_values[i],
                    intensity_values[i],
                    annotations={"FragmentType": fragment_types[i]},
                )
            )
        return spectra


class PrositIntensityHCD(KoinaModel):
    def preprocess(self):
        self.prediction_df = self.prediction_df[self.prediction_df["Charge"] <= 5]


class PrositIntensityCID(KoinaModel):
    def preprocess(self):
        self.prediction_df = self.prediction_df[self.prediction_df["Charge"] <= 5]


class PrositIntensityXL_CMS3(KoinaModel):
    pass


class SpectrumPredictorFactory:
    class_mapping = {
        "PrositIntensityHCD": PrositIntensityHCD,
        "PrositIntensityCID": PrositIntensityCID,
        "PrositIntensityXL_CMS3": PrositIntensityXL_CMS3,
    }

    @staticmethod
    def create_predictor(model_name: str, prediction_df: pd.DataFrame):
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model '{model_name}' is not available.")

        return SpectrumPredictorFactory.class_mapping[model_name](
            prediction_df, **AVAILABLE_MODELS[model_name]
        )


def predict(
    model_name: str,
    peptide_df: pd.DataFrame,
    output_format: str,
    csv_seperator: str = ",",
):
    if "Charge" in peptide_df.columns:
        prediction_df = (
            peptide_df[["Sequence", "Charge"]].copy().drop_duplicates()[::10]
        )
        prediction_df["NCE"] = 30
    else:
        logging.warning("No charge column found, assuming charge 2")
        prediction_df = SpectrumPredictor.create_prediction_df(
            peptide_df["Sequence"], peptide_df["Charge"], 30
        )
    predictor = SpectrumPredictorFactory.create_predictor(model_name, prediction_df)
    predicted_spectra = predictor.predict()
    # merge df's into big df
    base_name = "predicted_spectra"
    if output_format == "csv":
        output = SpectrumExporter.export_to_csv(predicted_spectra, base_name)
    elif output_format == "msp":
        output = SpectrumExporter.export_to_msp(predicted_spectra, base_name)
    elif output_format == "mgf":
        output = SpectrumExporter.export_to_mgf(predicted_spectra, base_name)
    return {
        "predicted_spectra": output,
        "messages": [
            {
                "level": logging.INFO,
                "msg": f"Successfully predicted {len(predicted_spectra)} spectra.",
            }
        ],
    }


class Spectrum:
    def __init__(
        self,
        peptide_sequence: str,
        charge: int,
        mz_values: np.array,
        intensity_values: np.array,
        metadata: Optional[dict] = None,
        annotations: Optional[dict] = None,
        sanitize: bool = True,
    ):
        self.peptide_sequence = peptide_sequence
        self.peptide_mz = mass.calculate_mass(
            sequence=peptide_sequence, charge=charge, ion_type="M"
        )
        self.metadata = metadata if metadata else {}
        self.metadata[
            "Charge"
        ] = charge  # TODO maybe this can be handled in the exporting functions instead

        self.spectrum = pd.DataFrame(
            zip(mz_values, intensity_values), columns=["m/z", "Intensity"]
        )
        if annotations:
            for key, value in annotations.items():
                self.spectrum[key] = value

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
    def export_to_msp(spectra: list[Spectrum], base_file_name: str):
        lines = []
        for spectrum in tqdm(
            spectra, desc="Exporting spectra to .msp format", total=len(spectra)
        ):
            header_dict = {
                "Name": spectrum.peptide_sequence,
                "Comment": "".join([f"{k}={v} " for k, v in spectrum.metadata.items()]),
                "Num Peaks": len(spectrum.spectrum),
            }
            header = "\n".join([f"{k}: {v}" for k, v in header_dict.items()])
            peaks = [
                f"{mz}\t{intensity}"
                for mz, intensity in spectrum.spectrum[["m/z", "Intensity"]].values
            ]
            if len(spectrum.spectrum.columns) > 2:
                peaks = SpectrumExporter._annotate_peak_strs(
                    peaks,
                    [
                        spectrum.spectrum[col].values
                        for col in spectrum.spectrum.columns[2:]
                    ],
                )
            peaks = "".join(peaks)
            lines.append(f"{header}\n{peaks}\n")

        logger.info(
            f"Exported {len(spectra)} spectra to MSP format, now combining them"
        )
        content = "\n".join(lines)
        logger.info("Export finished!")
        return FileOutput(base_file_name, "msp", content)

    @staticmethod
    def _annotate_peak_strs(
        peaks: list[str],
        annotations: list[list[str]],
        prefix='"',
        seperator=" ",
        suffix='"',
        add_newline=True,
    ):
        combined_annotations = [prefix for _ in range(len(peaks))]
        for annotation in annotations:
            combined_annotations = [
                current_annotation_str + peak_annotation + seperator
                for current_annotation_str, peak_annotation in zip(
                    combined_annotations, annotation
                )
            ]
        # remove last seperator
        combined_annotations = [
            current_annotation_str[:-1]
            for current_annotation_str in combined_annotations
        ]
        combined_annotations = [
            current_annotation_str + suffix
            for current_annotation_str in combined_annotations
        ]
        new_peaks = [
            f"{peak}\t{annotation}"
            for peak, annotation in zip(peaks, combined_annotations)
        ]
        if add_newline:
            new_peaks = [f"{peak}\n" for peak in new_peaks]
        return new_peaks

        return

    @staticmethod
    def export_to_csv(
        spectra: list[Spectrum], base_file_name: str, seperator: str = ","
    ):
        # required columns: PrecursorMz, FragmentMz
        # recommended columns: iRT (impossible), RelativeFragmentIntensity (maybe possible, @Chris),
        # - StrippedSequence (peptide sequence without modifications, easy)
        # - PrecursorCharge (maybe possible with evidence)
        # - FragmentType (b or y, maybe possible, depends on model)
        # - FragmentNumber (after which AA in the sequence the cut is, i think)
        #
        if seperator not in [",", ";", "\t"]:
            raise ValueError(r"Invalid seperator, please use one of: ',' , ';' , '\t'")
        if seperator == "\t":
            file_extension = "tsv"
        else:
            file_extension = "csv"

        output_df = pd.DataFrame()
        spectrum_dfs = []
        for spectrum in tqdm(spectra, desc="Preparing spectra"):
            spectrum_df = spectrum.spectrum
            spectrum_df["PrecursorMz"] = spectrum.peptide_mz
            spectrum_df["StrippedSequence"] = spectrum.peptide_sequence
            spectrum_df["PrecursorCharge"] = spectrum.metadata["Charge"]
            spectrum_df.rename(
                columns={"m/z": "FragmentMz", "Intensity": "RelativeFragmentIntensity"},
                inplace=True,
            )  #
            spectrum_dfs.append(spectrum_df)
        output_df = pd.concat(spectrum_dfs, ignore_index=True)
        content = output_df.to_csv(sep=seperator, index=False)
        return FileOutput(base_file_name, file_extension, content)
