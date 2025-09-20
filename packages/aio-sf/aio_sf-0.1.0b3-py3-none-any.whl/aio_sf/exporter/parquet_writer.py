"""
Parquet writer module for converting Salesforce QueryResult to Parquet format.
"""

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import pyarrow as pa
import pandas as pd
import pyarrow.parquet as pq

from ..api.describe.types import FieldInfo

from .bulk_export import QueryResult, batch_records_async


def salesforce_to_arrow_type(sf_type: str) -> pa.DataType:
    """Convert Salesforce data types to Arrow data types."""
    type_mapping = {
        "string": pa.string(),
        "boolean": pa.bool_(),
        "int": pa.int64(),
        "double": pa.float64(),
        "date": pa.string(),  # Store as string since SF returns ISO format
        "datetime": pa.string(),  # Store as string since SF returns ISO format
        "currency": pa.float64(),
        "reference": pa.string(),
        "picklist": pa.string(),
        "multipicklist": pa.string(),
        "textarea": pa.string(),
        "phone": pa.string(),
        "url": pa.string(),
        "email": pa.string(),
        "combobox": pa.string(),
        "percent": pa.float64(),
        "id": pa.string(),
        "base64": pa.string(),
        "anyType": pa.string(),
    }
    return type_mapping.get(sf_type.lower(), pa.string())


def create_schema_from_metadata(fields_metadata: List[FieldInfo]) -> pa.Schema:
    """
    Create a PyArrow schema from Salesforce field metadata.

    :param fields_metadata: List of field metadata dictionaries from Salesforce
    :returns: PyArrow schema
    """
    arrow_fields = []
    for field in fields_metadata:
        field_name = field.get("name", "").lower()  # Normalize to lowercase
        sf_type = field.get("type", "string")
        arrow_type = salesforce_to_arrow_type(sf_type)
        # All fields are nullable since Salesforce can return empty values
        arrow_fields.append(pa.field(field_name, arrow_type, nullable=True))

    return pa.schema(arrow_fields)


class ParquetWriter:
    """
    Writer class for converting Salesforce QueryResult to Parquet format.
    Supports streaming writes and optional schema from field metadata.
    """

    def __init__(
        self,
        file_path: str,
        schema: Optional[pa.Schema] = None,
        batch_size: int = 10000,
        convert_empty_to_null: bool = True,
    ):
        """
        Initialize ParquetWriter.

        :param file_path: Path to output parquet file
        :param schema: Optional PyArrow schema. If None, will be inferred from first batch
        :param batch_size: Number of records to process in each batch
        :param convert_empty_to_null: Convert empty strings to null values
        """
        self.file_path = file_path
        self.schema = schema
        self.batch_size = batch_size
        self.convert_empty_to_null = convert_empty_to_null
        self._writer = None
        self._schema_finalized = False

        # Ensure parent directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    async def write_query_result(self, query_result: QueryResult) -> None:
        """
        Write all records from a QueryResult to the parquet file (async version).

        :param query_result: QueryResult to write
        """
        try:
            async for batch in batch_records_async(query_result, self.batch_size):
                self._write_batch(batch)
        finally:
            self.close()

    def _write_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Write a batch of records to the parquet file."""
        if not batch:
            return

        # Convert field names to lowercase for consistency
        converted_batch = []
        for record in batch:
            converted_record = {k.lower(): v for k, v in record.items()}
            converted_batch.append(converted_record)

        # Create DataFrame
        df = pd.DataFrame(converted_batch)

        # If schema not finalized, create it from first batch
        if not self._schema_finalized:
            if self.schema is None:
                self.schema = self._infer_schema_from_dataframe(df)
            else:
                # Filter schema to only include fields that are actually in the data
                self.schema = self._filter_schema_to_data(self.schema, df.columns)
            self._schema_finalized = True

        # Apply data type conversions based on schema
        self._convert_dataframe_types(df)

        # Create Arrow table
        table = pa.Table.from_pandas(df, schema=self.schema)

        # Initialize writer if needed
        if self._writer is None:
            self._writer = pq.ParquetWriter(self.file_path, self.schema)

        # Write the table
        self._writer.write_table(table)

    def _infer_schema_from_dataframe(self, df: pd.DataFrame) -> pa.Schema:
        """Infer schema from the first DataFrame."""
        fields = []
        for col_name, dtype in df.dtypes.items():
            if dtype == "object":
                arrow_type = pa.string()
            elif dtype == "bool":
                arrow_type = pa.bool_()
            elif dtype in ["int64", "int32"]:
                arrow_type = pa.int64()
            elif dtype in ["float64", "float32"]:
                arrow_type = pa.float64()
            else:
                arrow_type = pa.string()

            fields.append(pa.field(col_name, arrow_type, nullable=True))

        return pa.schema(fields)

    def _filter_schema_to_data(
        self, schema: pa.Schema, data_columns: List[str]
    ) -> pa.Schema:
        """Filter schema to only include fields that are present in the data."""
        # Convert data columns to set for faster lookup
        data_columns_set = set(data_columns)

        # Filter schema fields to only those present in data
        filtered_fields = []
        for field in schema:
            if field.name in data_columns_set:
                filtered_fields.append(field)

        if len(filtered_fields) != len(data_columns_set):
            # Log fields that are in data but not in schema (shouldn't happen normally)
            missing_in_schema = data_columns_set - {f.name for f in filtered_fields}
            if missing_in_schema:
                logging.warning(
                    f"Fields in data but not in schema: {missing_in_schema}"
                )

        return pa.schema(filtered_fields)

    def _convert_dataframe_types(self, df: pd.DataFrame) -> None:
        """Convert DataFrame types based on the schema."""
        for field in self.schema:
            field_name = field.name
            if field_name not in df.columns:
                continue

            # Convert empty strings to null if requested
            if self.convert_empty_to_null:
                df[field_name] = df[field_name].replace({"": None})

            # Apply type-specific conversions
            if pa.types.is_boolean(field.type):
                # Convert string 'true'/'false' to boolean
                df[field_name] = (
                    df[field_name]
                    .map({"true": True, "false": False, None: None})
                    .fillna(df[field_name])
                )  # Keep original values for non-string booleans
            elif pa.types.is_integer(field.type):
                df[field_name] = pd.to_numeric(df[field_name], errors="coerce").astype(
                    "Int64"
                )  # Nullable integer
            elif pa.types.is_floating(field.type):
                df[field_name] = pd.to_numeric(df[field_name], errors="coerce")

            # Replace empty strings with None for non-string fields
            if not pa.types.is_string(field.type):
                df[field_name] = df[field_name].replace("", pd.NA)

    def close(self) -> None:
        """Close the parquet writer."""
        if self._writer:
            self._writer.close()
            self._writer = None


async def write_query_to_parquet(
    query_result: QueryResult,
    file_path: str,
    fields_metadata: Optional[List[FieldInfo]] = None,
    schema: Optional[pa.Schema] = None,
    batch_size: int = 10000,
    convert_empty_to_null: bool = True,
) -> None:
    """
    Convenience function to write a QueryResult to a parquet file (async version).

    :param query_result: QueryResult to write
    :param file_path: Path to output parquet file
    :param fields_metadata: Optional Salesforce field metadata for schema creation
    :param schema: Optional pre-created PyArrow schema (takes precedence over fields_metadata)
    :param batch_size: Number of records to process in each batch
    :param convert_empty_to_null: Convert empty strings to null values
    """
    effective_schema = None
    if schema:
        effective_schema = schema
    elif fields_metadata:
        effective_schema = create_schema_from_metadata(fields_metadata)

    writer = ParquetWriter(
        file_path=file_path,
        schema=effective_schema,
        batch_size=batch_size,
        convert_empty_to_null=convert_empty_to_null,
    )

    await writer.write_query_result(query_result)
