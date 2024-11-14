import asyncio
import concurrent.futures
import hashlib
import json
import multiprocessing
import re
from typing import Dict, List, Optional

import aiohttp
import numpy as np
import pandas as pd
from tqdm import tqdm

from protzilla.constants.ms_constants import DataKeys
from protzilla.constants.protzilla_logging import logger
from protzilla.data_analysis.spectrum_prediction.spectrum_prediction_utils import (
    CSV_COLUMNS,
    GenericTextKeys,
    OutputKeys,
    PredictionModelMetadata,
    calculate_peptide_mass,
)
from protzilla.disk_operator import FileOutput


class Spectrum:
    def __init__(
        self,
        peptide_sequence: str,
        charge: int,
        peptide_mz: float,
        mz_values: np.array,
        intensity_values: np.array,
        metadata: Optional[dict] = None,
        annotations: Optional[dict] = None,
        sanitize: bool = True,
    ):
        """
        Create a new Spectrum object.
        :param peptide_sequence: the peptide sequence of the precursor peptide of the spectrum
        :param charge: the charge of the peptide precursor
        :param metadata: dictionary containing spectrum metadata, e.g. collision energy, fragmentation type
        :param annotations: a dictionary containing additional peak annotations
        :param sanitize: if True, the spectrum will be sanitized by removing duplicates and negative intensities
        """
        self.peptide_sequence = peptide_sequence
        self.peptide_mz = peptide_mz
        self.precursor_charge = charge
        self.metadata = metadata if metadata else {}
        self._initialize_metadata()
        self.unique_id = self._generate_hash()

        self.spectrum = pd.DataFrame(
            zip(mz_values, intensity_values),
            columns=[DataKeys.MZ, DataKeys.INTENSITY],
        )
        if annotations:
            for key, value in annotations.items():
                self.spectrum[key] = value

        if sanitize:
            self._sanitize_spectrum()

    def __str__(self):
        return f"{self.peptide_sequence}: {self.precursor_charge}, {self.spectrum.shape[0]} peaks"

    def _sanitize_spectrum(self):
        """Remove duplicates and invalid / dropped peaks from the spectrum.
        Negative intensities are removed."""
        self.spectrum = self.spectrum.drop_duplicates(subset=DataKeys.MZ)
        self.spectrum = self.spectrum[self.spectrum[DataKeys.INTENSITY] > 0]

    def _generate_hash(self) -> str:
        """Generate a unique hash based on all metadata of the spectrum."""
        metadata_str = "".join(f"{k}={v}" for k, v in sorted(self.metadata.items()))
        return hashlib.md5(metadata_str.encode()).hexdigest()

    def _initialize_metadata(self):
        self.metadata.setdefault(DataKeys.PEPTIDE_SEQUENCE, self.peptide_sequence)
        self.metadata.setdefault(DataKeys.PRECURSOR_CHARGE, self.precursor_charge)
        self.metadata.setdefault(DataKeys.PRECURSOR_MZ, self.peptide_mz)
        # self.metadata.setdefault(DATA_KEYS.COLLISION_ENERGY, None) # TODO delete if not necessary
        # self.metadata.setdefault(DATA_KEYS.FRAGMENTATION_TYPE, None)

    def __str__(self):
        return f"{self.peptide_sequence}: {self.charge}, {self.spectrum.shape[0]} peaks"

    def _sanitize_spectrum(self):
        self.spectrum = self.spectrum.drop_duplicates(subset=DataKeys.MZ)
        self.spectrum = self.spectrum[self.spectrum[DataKeys.INTENSITY] > 0]

    def to_mergeable_df(self):
        """Convert the spectrum to two DataFrames: one for metadata and one for spectrum peaks."""
        # Create the spectrum peaks DataFrame
        peaks_df = self.spectrum.copy()
        peaks_df["unique_id"] = self.unique_id

        # Ensure 'm/z' and 'intensity' are the first columns after 'unique_id'
        column_order = ["unique_id", DataKeys.MZ, DataKeys.INTENSITY]
        annotation_columns = [
            col for col in peaks_df.columns if col not in column_order
        ]
        column_order.extend(annotation_columns)
        peaks_df = peaks_df[column_order]

        # Create the metadata DataFrame
        metadata_df = pd.DataFrame(
            {
                "unique_id": [self.unique_id],
                **{k: [v] for k, v in self.metadata.items()},
            }
        )
        # set index to unique_id as to hide it in the output and not confuse biologists
        metadata_df.set_index("unique_id", inplace=True)
        peaks_df.set_index("unique_id", inplace=True)
        return metadata_df, peaks_df

    @property
    def peptide_mass(self):
        return calculate_peptide_mass(self.peptide_mz, self.precursor_charge)


class SpectrumPredictor:
    def __init__(self, prediction_df: Optional[pd.DataFrame]):
        if prediction_df is not None:
            self.load_prediction_df(prediction_df)

    def predict(self):
        raise NotImplementedError(
            "This method should be implemented in the child class"
        )

    def preprocess(self):
        raise NotImplementedError(
            "This method should be implemented in the child class"
        )

    def verify_dataframe(self, prediction_df: Optional[pd.DataFrame] = None):
        raise NotImplementedError(
            "This method should be implemented in the child class"
        )

    def load_prediction_df(self, prediction_df: pd.DataFrame):
        self.prediction_df = prediction_df
        self.preprocess()
        self.verify_dataframe()


class KoinaModel(SpectrumPredictor):
    ptm_regex = re.compile(r"[\[\(]")
    FRAGMENT_ANNOTATION_PATTERN = re.compile(r"([a-zA-Z]\d+)\+(\d+)")

    def __init__(
        self,
        required_keys: list[str],
        url: str,
        prediction_df: Optional[pd.DataFrame] = None,
        **kwargs,
    ):
        super().__init__(prediction_df)
        self.required_keys = required_keys
        self.KOINA_URL = url
        self.preprocess_args = kwargs.get("preprocess_args", {})

    def load_prediction_df(self, prediction_df: pd.DataFrame):
        self.prediction_df = prediction_df
        self.preprocess()
        self.verify_dataframe()
        return self.prediction_df

    def verify_dataframe(self, prediction_df: Optional[pd.DataFrame] = None):
        if prediction_df is None:
            prediction_df = self.prediction_df
        for key in self.required_keys:
            if key not in prediction_df.columns:
                raise ValueError(f"Required key '{key}' not found in input DataFrame.")

    def preprocess(self):
        self.prediction_df = (
            self.prediction_df[self.required_keys + [DataKeys.PRECURSOR_MZ]]
            .drop_duplicates(
                subset=[DataKeys.PEPTIDE_SEQUENCE, DataKeys.PRECURSOR_CHARGE]
            )
            .reset_index(drop=True)
        )

        self.prediction_df = self.prediction_df[
            self.prediction_df[DataKeys.PRECURSOR_CHARGE]
            <= self.preprocess_args.get("max_charge", 5)
        ]
        if self.preprocess_args.get("filter_ptms", True):
            self.filter_ptms()

        if self.preprocess_args.get("replace_J_with_L", False):
            self.prediction_df[DataKeys.PEPTIDE_SEQUENCE] = self.prediction_df[
                DataKeys.PEPTIDE_SEQUENCE
            ].str.replace("J", "L")

    def filter_ptms(self):
        self.prediction_df = self.prediction_df[
            ~self.prediction_df[DataKeys.PEPTIDE_SEQUENCE].str.contains(
                self.ptm_regex, regex=True
            )
        ]

    def predict(self):
        predicted_spectra = []
        slice_indices = self.slice_dataframe()
        formatted_data = self.format_dataframes(slice_indices)
        response_data = asyncio.run(self.make_request(formatted_data, slice_indices))

        num_processes = min(multiprocessing.cpu_count() // 2, len(response_data))

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=num_processes
        ) as executor:
            futures = []
            for response, indices in response_data:
                future = executor.submit(
                    self.process_response_batch,
                    self.prediction_df.loc[indices],
                    response,
                )
                futures.append(future)

            for future in tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Processing predictions",
            ):
                predicted_spectra.extend(future.result())

        return predicted_spectra

    def format_dataframes(self, slice_indices):
        """Format a list of slices of the prediction DataFrame for the request."""
        return [
            self.format_for_request(self.prediction_df.loc[slice])
            for slice in slice_indices
        ]

    def slice_dataframe(self, chunk_size: int = 1000):
        """Slice the prediction DataFrame into chunks of size chunk_size."""
        return [
            self.prediction_df[i : i + chunk_size].index
            for i in range(0, len(self.prediction_df), chunk_size)
        ]

    def format_for_request(self, to_predict: pd.DataFrame) -> dict:
        """Format the DataFrame for the request to the Koina API. Returns the formatted data as a JSON string."""
        inputs = []
        if DataKeys.PEPTIDE_SEQUENCE in to_predict.columns:
            inputs.append(
                {
                    "name": str(DataKeys.PEPTIDE_SEQUENCE),
                    "shape": [len(to_predict), 1],
                    "datatype": "BYTES",
                    "data": to_predict[DataKeys.PEPTIDE_SEQUENCE].to_list(),
                }
            )
        if DataKeys.PRECURSOR_CHARGE in to_predict.columns:
            inputs.append(
                {
                    "name": str(DataKeys.PRECURSOR_CHARGE),
                    "shape": [len(to_predict), 1],
                    "datatype": "INT32",
                    "data": to_predict[DataKeys.PRECURSOR_CHARGE].to_list(),
                }
            )
        if DataKeys.COLLISION_ENERGY in to_predict.columns:
            inputs.append(
                {
                    "name": str(DataKeys.COLLISION_ENERGY),
                    "shape": [len(to_predict), 1],
                    "datatype": "FP32",
                    "data": to_predict[DataKeys.COLLISION_ENERGY].to_list(),
                }
            )
        if DataKeys.FRAGMENTATION_TYPE in to_predict.columns:
            inputs.append(
                {
                    "name": str(DataKeys.FRAGMENTATION_TYPE),
                    "shape": [len(to_predict), 1],
                    "datatype": "BYTES",
                    "data": to_predict[DataKeys.FRAGMENTATION_TYPE].to_list(),
                }
            )

        if DataKeys.INSTRUMENT_TYPE in to_predict.columns:
            inputs.append(
                {
                    "name": str(DataKeys.INSTRUMENT_TYPE),
                    "shape": [len(to_predict), 1],
                    "datatype": "BYTES",
                    "data": to_predict[DataKeys.INSTRUMENT_TYPE].to_list(),
                }
            )
        return {"id": "0", "inputs": inputs}

    async def make_request(
        self, formatted_data: list[dict], slice_indices: list
    ) -> list[dict]:
        """Asynchronously make a POST request to the Koina API. Returns the response data as a list of dictionaries.
        In the case of an error, we will recursively divide and conquer the data until we get a successful response.
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for data, indices in zip(formatted_data, slice_indices):
                tasks.append(
                    (session.post(self.KOINA_URL, data=json.dumps(data)), indices)
                )
                logger.info(
                    f"Requesting {len(indices)} spectra {indices[0]}-{indices[-1]}..."
                )
            responses = []
            for task, indices in tasks:
                response = await task
                if response.status != 200:
                    if len(indices) > 1:
                        mid = len(indices) // 2
                        a, b = indices[:mid], indices[mid:]
                        logger.warning(
                            f"Error response received for {indices[0]}-{indices[-1]}, splitting data: {a[0]}-{a[-1]} and {b[0]}-{b[-1]}..."
                        )
                        formatted_data = self.format_dataframes([a, b])
                        responses.extend(
                            await self.make_request(formatted_data, [a, b])
                        )
                    else:
                        logger.error(
                            f"Skipping peptide {self.prediction_df.loc[indices[0]][DataKeys.PEPTIDE_SEQUENCE]} with charge {self.prediction_df.loc[indices[0]][DataKeys.PRECURSOR_CHARGE]}."
                        )
                        logger.debug(f"Error in response: {await response.text()}")
                else:
                    responses.append((await response.json(), indices))
        return responses

    @staticmethod
    def process_response_batch(request: pd.DataFrame, response: dict) -> List[Spectrum]:
        prepared_data = KoinaModel.prepare_data(response)
        return [
            KoinaModel.create_spectrum(row, prepared_data, i)
            for i, (_, row) in enumerate(request.iterrows())
        ]

    @staticmethod
    def prepare_data(response: dict) -> dict:
        results = KoinaModel.extract_data_from_response(response)
        fragment_charges, fragment_types = KoinaModel.extract_fragment_information(
            results[OutputKeys.ANNOTATIONS]
        )
        results[OutputKeys.FRAGMENT_TYPE] = fragment_types
        results[OutputKeys.FRAGMENT_CHARGE] = fragment_charges
        return results

    @staticmethod
    def create_spectrum(
        row: pd.Series, prepared_data: Dict[str, np.ndarray], index: int
    ) -> Spectrum:
        try:
            peptide_sequence = row.get(DataKeys.PEPTIDE_SEQUENCE)
            precursor_charge = row.get(DataKeys.PRECURSOR_CHARGE)
            peptide_mz = row.get(DataKeys.PRECURSOR_MZ)
            collision_energy = row.get(DataKeys.COLLISION_ENERGY)
            fragmentation_type = row.get(DataKeys.FRAGMENTATION_TYPE)
            mz_values = prepared_data.get(OutputKeys.MZ_VALUES)[index]
            intensity_values = prepared_data.get(OutputKeys.INTENSITY_VALUES)[index]
            peak_annotations = {
                OutputKeys.FRAGMENT_TYPE: prepared_data.get(OutputKeys.FRAGMENT_TYPE)[
                    index
                ],
                OutputKeys.FRAGMENT_CHARGE: prepared_data.get(
                    OutputKeys.FRAGMENT_CHARGE
                )[index],
            }
            metadata = {}
            if collision_energy:
                metadata[DataKeys.COLLISION_ENERGY] = collision_energy
            if fragmentation_type:
                metadata[DataKeys.FRAGMENTATION_TYPE] = fragmentation_type

            return Spectrum(
                peptide_sequence=peptide_sequence,
                charge=precursor_charge,
                peptide_mz=peptide_mz,
                mz_values=mz_values,
                intensity_values=intensity_values,
                annotations=peak_annotations,
                metadata=metadata,
            )
        except (KeyError, TypeError) as e:
            raise ValueError(f"Error while creating spectrum: {e}")

    @staticmethod
    def extract_fragment_information(fragment_annotations: np.array):
        def extract_annotation_information(annotation_str: str):
            if match := KoinaModel.FRAGMENT_ANNOTATION_PATTERN.match(annotation_str):
                return match.group(1), match.group(2)
            return None, None

        vectorized_annotation_extraction = np.vectorize(extract_annotation_information)
        fragment_types, fragment_charges = vectorized_annotation_extraction(
            fragment_annotations
        )
        # TODO find a way to make the None values always represented as ""
        fragment_types, fragment_charges = fragment_types.astype(
            str
        ), fragment_charges.astype(str)
        fragment_types[fragment_types == "None"] = ""
        fragment_charges[fragment_charges == "None"] = ""
        return fragment_charges, fragment_types

    @staticmethod
    def extract_data_from_response(response: dict):
        results = {}
        for output in response["outputs"]:
            results[output["name"]] = np.reshape(output["data"], output["shape"])
        return results


class SpectrumPredictorFactory:
    @staticmethod
    def create_predictor(model_name: str) -> KoinaModel:
        if model_name not in PredictionModelMetadata:
            raise ValueError(f"Model '{model_name}' is not available.")
        return KoinaModel(**PredictionModelMetadata[model_name])


class SpectrumExporter:
    msp_metadata_mapping = {
        DataKeys.PRECURSOR_CHARGE: "Charge",
        DataKeys.PRECURSOR_MZ: "Parent",
        DataKeys.COLLISION_ENERGY: "Collision Energy",
    }

    @staticmethod
    def export_to_msp(spectra: list[Spectrum], base_file_name: str):
        lines = []
        for spectrum in tqdm(
            spectra, desc="Exporting spectra to .msp format", total=len(spectra)
        ):
            renamed_metadata = {
                SpectrumExporter.msp_metadata_mapping.get(k): v
                for k, v in spectrum.metadata.items()
                if k in SpectrumExporter.msp_metadata_mapping
            }
            header = (
                f"Name: {spectrum.peptide_sequence}\n"
                f"Comment: {''.join([f'{k}={v} ' for k, v in renamed_metadata.items() if v])}\n"
                f"Num Peaks: {len(spectrum.spectrum)}"
            )
            peaks = "".join(SpectrumExporter._format_peaks_for_msp(spectrum.spectrum))
            lines.append(f"{header}\n{peaks}\n")

        logger.info(
            f"Exported {len(spectra)} spectra to MSP format, now combining them"
        )
        content = "\n".join(lines)
        logger.info("Export finished!")
        return FileOutput(base_file_name, "msp", content)

    @staticmethod
    def _format_peaks_for_msp(
        spectrum_df: pd.DataFrame,
        prefix='"',
        seperator=" ",
        suffix='"',
    ):
        peaks = [
            f"{mz}\t{intensity}"
            for mz, intensity in spectrum_df[[DataKeys.MZ, DataKeys.INTENSITY]].values
        ]
        annotations = [f"{prefix}" for _ in spectrum_df.values]
        if len(spectrum_df.columns) <= 2:
            pass
        else:
            for column in spectrum_df.columns[2:]:
                if column == OutputKeys.FRAGMENT_CHARGE:
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

    csv_fragment_pattern = re.compile(r"([yb])(\d+)")

    @staticmethod
    def export_to_generic_text(
        spectra: list[Spectrum], base_file_name: str, seperator: str = ","
    ):
        """Converts to generic text, see
        https://biognosys.com/content/uploads/2023/03/Spectronaut-17_UserManual.pdf
        for reference
        """
        if seperator not in [",", ";", "\t"]:
            raise ValueError(r"Invalid seperator, please use one of: ',' , ';' , '\t'")
        if seperator == "\t":
            file_extension = "tsv"
        else:
            file_extension = "csv"

        output_df = pd.DataFrame()
        spectrum_dfs = []
        for spectrum in tqdm(spectra, desc="Preparing spectra for export"):
            spectrum_df = spectrum.spectrum.copy()
            spectrum_df[GenericTextKeys.PEPTIDE_MZ] = spectrum.peptide_mz
            spectrum_df[GenericTextKeys.PEPTIDE_SEQUENCE] = spectrum.peptide_sequence
            spectrum_df[GenericTextKeys.PRECURSOR_CHARGE] = spectrum.precursor_charge
            spectrum_df[GenericTextKeys.FRAGMENT_NUMBER] = spectrum_df[
                OutputKeys.FRAGMENT_TYPE
            ].apply(lambda x: SpectrumExporter.csv_fragment_pattern.match(x).group(2))
            spectrum_df[GenericTextKeys.FRAGMENT_TYPE] = spectrum_df[
                OutputKeys.FRAGMENT_TYPE
            ].apply(lambda x: SpectrumExporter.csv_fragment_pattern.match(x).group(1))
            spectrum_df.rename(
                columns={
                    DataKeys.MZ: GenericTextKeys.MZ,
                    DataKeys.INTENSITY: GenericTextKeys.INTENSITY,
                    DataKeys.FRAGMENT_CHARGE: GenericTextKeys.FRAGMENT_CHARGE,
                },
                inplace=True,
            )

            spectrum_df = spectrum_df[CSV_COLUMNS]
            spectrum_dfs.append(spectrum_df)
        output_df = (
            pd.concat(spectrum_dfs, ignore_index=True)
            if spectrum_dfs
            else pd.DataFrame(columns=CSV_COLUMNS)
        )
        content = output_df.to_csv(sep=seperator, index=False)
        return FileOutput(base_file_name, file_extension, content)

    @staticmethod
    def _format_peaks_for_mgf(spectrum_df: pd.DataFrame):
        peaks = [
            f"{mz}\t{intensity}"
            for mz, intensity in spectrum_df[[DataKeys.MZ, DataKeys.INTENSITY]].values
        ]
        return peaks

    @staticmethod
    def export_to_mgf(spectra: list[Spectrum], base_file_name: str):
        lines = []
        for spectrum in tqdm(
            spectra, desc="Exporting spectra to .mgf format", total=len(spectra)
        ):
            if spectrum.precursor_charge is None or spectrum.precursor_charge == 0:
                raise ValueError(
                    f"Invalid precursor charge for spectrum {spectrum.peptide_sequence}, please provide a valid precursor charge."
                )
            header = (
                f"BEGIN IONS\n"
                f"TITLE={spectrum.peptide_sequence}\n"
                f"PEPMASS={spectrum.peptide_mass}\n"
                f"CHARGE={spectrum.precursor_charge}+\n"
            )
            peaks = "\n".join(SpectrumExporter._format_peaks_for_mgf(spectrum.spectrum))
            lines.append(f"{header}\n{peaks}\n\nEND IONS\n")

        logger.info(
            f"Exported {len(spectra)} spectra to MGF format, now combining them"
        )
        content = "\n".join(lines)
        logger.info("Export finished!")
        return FileOutput(base_file_name, "mgf", content)
