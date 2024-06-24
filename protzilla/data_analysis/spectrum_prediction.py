import asyncio
import json
import logging
import re
from enum import StrEnum
from typing import Optional

import aiohttp
import numpy as np
import pandas as pd
from pyteomics.mass import mass
from tqdm import tqdm

from protzilla.constants.protzilla_logging import logger
from protzilla.disk_operator import FileOutput


class FRAGMENTATION_TYPE(StrEnum):
    HCD = "HCD"
    CID = "CID"


class DATA_KEYS(StrEnum):
    PEPTIDE_SEQUENCE = "peptide_sequences"
    PRECURSOR_CHARGES = "precursor_charges"
    COLLISION_ENERGIES = "collision_energies"
    FRAGMENTATION_TYPES = "fragmentation_types"


class OUTPUT_KEYS(StrEnum):
    MZ_VALUES = "mz"
    INTENSITY_VALUES = "intensities"
    ANNOTATIONS = "annotation"
    FRAGMENT_TYPE = "fragment_type"
    FRAGMENT_CHARGE = "fragment_charge"


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
    # "PrositIntensityXL_CMS3": {
    #    "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2023_intensity_XL_CMS3/infer",
    #    "required_keys": ["peptide_sequences", "precursor_charges"],
    # },
    # "PrositIntensityXL_CMS2": {
    #     "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2023_intensity_XL_CMS2/infer",
    #     "required_keys": ["peptide_sequences", "precursor_charges"]
    # },
    "PrositIntensityTimsTOF": {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2023_intensity_timsTOF/infer",
        "required_keys": [
            "peptide_sequences",
            "precursor_charges",
            "collision_energies",
        ],
    },
    "PrositIntensityTMT": {
        "url": "https://koina.wilhelmlab.org/v2/models/Prosit_2020_intensity_TMT/infer",
        "required_keys": [
            DATA_KEYS.PEPTIDE_SEQUENCE,
            DATA_KEYS.PRECURSOR_CHARGES,
            DATA_KEYS.COLLISION_ENERGIES,
            DATA_KEYS.FRAGMENTATION_TYPES,
        ],
    },
}

AVAILABLE_FORMATS = ["msp", "csv"]


class SpectrumPredictor:
    def __init__(self, prediction_df: pd.DataFrame):
        self.prediction_df = prediction_df

    # TODO this can be cleaned up, using the peptide_df directly
    @staticmethod
    def create_prediction_df(
        peptide_sequences,
        charge: list[int] | range,
        nce: int = 30,
        fragmentation_types: list[str] = None,
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
        if fragmentation_types:
            for ft in fragmentation_types:
                prediction_df = pd.concat(
                    [
                        prediction_df,
                        pd.DataFrame({"FragmentType": [ft] * len(prediction_df)}),
                    ],
                    ignore_index=True,
                )
        prediction_df.drop_duplicates(inplace=True)
        return prediction_df

    def predict(self):
        raise NotImplementedError(
            "This method should be implemented in the child class"
        )

    def _verify_input(self, prediction_df: Optional[pd.DataFrame] = None):
        raise NotImplementedError(
            "This method should be implemented in the child class"
        )


class KoinaModel(SpectrumPredictor):
    def __init__(
        self,
        required_keys: list[str],
        url: str,
        prediction_df: Optional[pd.DataFrame] = None,
    ):
        super().__init__(prediction_df)
        self.required_keys = required_keys
        self.KOINA_URL = url
        if prediction_df is not None:
            self._load_prediction_df(prediction_df)

    def _load_prediction_df(self, prediction_df: pd.DataFrame):
        self.prediction_df = prediction_df
        self.preprocess()
        self._verify_input(prediction_df)

    def _verify_input(self, prediction_df: Optional[pd.DataFrame] = None):
        for key in self.required_keys:
            if key not in prediction_df.columns:
                raise ValueError(f"Required key '{key}' not found in input DataFrame.")

    def preprocess(self):
        self.prediction_df.rename(
            columns={
                "Sequence": DATA_KEYS.PEPTIDE_SEQUENCE,
                "Charge": DATA_KEYS.PRECURSOR_CHARGES,
                "NCE": DATA_KEYS.COLLISION_ENERGIES,
                "FragmentationType": DATA_KEYS.FRAGMENTATION_TYPES,
            },
            inplace=True,
        )
        self.prediction_df = self.prediction_df[self.required_keys]
        self.prediction_df = self.prediction_df[
            self.prediction_df[DATA_KEYS.PRECURSOR_CHARGES] <= 5
        ]

    annotation_regex = re.compile(r"((y|b)\d+)\+(\d+)")

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
        if DATA_KEYS.PEPTIDE_SEQUENCE in to_predict.columns:
            inputs.append(
                {
                    "name": str(DATA_KEYS.PEPTIDE_SEQUENCE),
                    "shape": [len(to_predict), 1],
                    "datatype": "BYTES",
                    "data": to_predict[DATA_KEYS.PEPTIDE_SEQUENCE].to_list(),
                }
            )
        if DATA_KEYS.PRECURSOR_CHARGES in to_predict.columns:
            inputs.append(
                {
                    "name": str(DATA_KEYS.PRECURSOR_CHARGES),
                    "shape": [len(to_predict), 1],
                    "datatype": "INT32",
                    "data": to_predict[DATA_KEYS.PRECURSOR_CHARGES].to_list(),
                }
            )
        if DATA_KEYS.COLLISION_ENERGIES in to_predict.columns:
            inputs.append(
                {
                    "name": str(DATA_KEYS.COLLISION_ENERGIES),
                    "shape": [len(to_predict), 1],
                    "datatype": "FP32",
                    "data": to_predict[DATA_KEYS.COLLISION_ENERGIES].to_list(),
                }
            )
        if DATA_KEYS.FRAGMENTATION_TYPES in to_predict.columns:
            inputs.append(
                {
                    "name": str(DATA_KEYS.FRAGMENTATION_TYPES),
                    "shape": [len(to_predict), 1],
                    "datatype": "BYTES",
                    "data": to_predict[DATA_KEYS.FRAGMENTATION_TYPES].to_list(),
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
        # convert the response to a DataFrame
        results = {}
        for output in response["outputs"]:
            results[output["name"]] = np.reshape(output["data"], output["shape"])

        # Prosit returns the annotations for charge and fragment type in a single string
        def get_annotations(annotations):
            if match := KoinaModel.annotation_regex.match(annotations):
                return match.group(1), match.group(3)
            return None, None

        vectorized_extract_annotations = np.vectorize(get_annotations)
        fragment_types, fragment_charges = vectorized_extract_annotations(
            results.get(OUTPUT_KEYS.ANNOTATIONS)
        )
        results[OUTPUT_KEYS.FRAGMENT_TYPE] = fragment_types
        results[OUTPUT_KEYS.FRAGMENT_CHARGE] = fragment_charges

        spectra = []
        for i, (_, row) in enumerate(request.iterrows()):
            spectra.append(
                Spectrum(
                    row[DATA_KEYS.PEPTIDE_SEQUENCE],
                    row[DATA_KEYS.PRECURSOR_CHARGES],
                    results.get(OUTPUT_KEYS.MZ_VALUES)[i],
                    results.get(OUTPUT_KEYS.INTENSITY_VALUES)[i],
                    annotations={
                        OUTPUT_KEYS.FRAGMENT_TYPE: results.get(
                            OUTPUT_KEYS.FRAGMENT_TYPE
                        )[i],
                        OUTPUT_KEYS.FRAGMENT_CHARGE: results.get(
                            OUTPUT_KEYS.FRAGMENT_CHARGE
                        )[i],
                    },
                )
            )
        return spectra


class SpectrumPredictorFactory:
    @staticmethod
    def create_predictor(model_name: str) -> KoinaModel:
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model '{model_name}' is not available.")
        return KoinaModel(**AVAILABLE_MODELS[model_name])


def predict(
    model_name: str,
    peptide_df: pd.DataFrame,
    output_format: str,
    csv_seperator: str = ",",
):
    predictor = SpectrumPredictorFactory.create_predictor(model_name)
    prediction_df = peptide_df[["Sequence", "Charge"]].copy().drop_duplicates()[::10]
    # TODO how to extract that data from the input?
    if DATA_KEYS.COLLISION_ENERGIES in predictor.required_keys:
        prediction_df["NCE"] = 30
    if DATA_KEYS.FRAGMENTATION_TYPES in predictor.required_keys:
        prediction_df["FragmentationType"] = FRAGMENTATION_TYPE.HCD

    predictor._load_prediction_df(prediction_df)
    predicted_spectra = predictor.predict()
    # merge df's into big df
    base_name = "predicted_spectra"
    if output_format == "csv":
        output = SpectrumExporter.export_to_csv(predicted_spectra, base_name)
    elif output_format == "msp":
        output = SpectrumExporter.export_to_msp(predicted_spectra, base_name)
    return {
        "predicted_spectra": output,
        "predicted_spectra_df": pd.concat(
            [spectrum.to_mergeable_df() for spectrum in predicted_spectra]
        ),
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
        return self.spectrum.assign(
            Sequence=self.peptide_sequence, Charge=self.metadata["Charge"]
        )


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
            peaks = SpectrumExporter._annotate_peak_strs_v2(spectrum.spectrum)
            peaks = "".join(peaks)
            lines.append(f"{header}\n{peaks}\n")

        logger.info(
            f"Exported {len(spectra)} spectra to MSP format, now combining them"
        )
        content = "\n".join(lines)
        logger.info("Export finished!")
        return FileOutput(base_file_name, "msp", content)

    @staticmethod
    def _annotate_peak_strs_v2(
        spectrum_df: pd.DataFrame,
        prefix='"',
        seperator=" ",
        suffix='"',
        add_newline=True,
    ):
        peaks = [
            f"{mz}\t{intensity}"
            for mz, intensity in spectrum_df[["m/z", "Intensity"]].values
        ]
        annotations = [f"{prefix}" for _ in spectrum_df.values]
        if len(spectrum_df.columns) > 2:
            for column in spectrum_df.columns[2:]:
                if column == OUTPUT_KEYS.FRAGMENT_CHARGE:
                    annotations = [
                        current_annotation_str[:-1] + f"^{fragment_charge}{seperator}"
                        for current_annotation_str, fragment_charge in zip(
                            annotations, spectrum_df[column]
                        )
                    ]
                    continue

                annotations = [
                    current_annotation_str + str(annotation) + seperator
                    for current_annotation_str, annotation in zip(
                        annotations, spectrum_df[column]
                    )
                ]
            annotations = [
                current_annotation_str[:-1] for current_annotation_str in annotations
            ]
            peaks = [
                f"{peak}\t{annotation}{suffix}\n"
                for peak, annotation in zip(peaks, annotations)
            ]

        return peaks

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
            # preprocess annotations
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
