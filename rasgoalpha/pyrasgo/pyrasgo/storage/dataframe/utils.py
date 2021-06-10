from enum import Enum
import pandas as pd
from typing import List, Optional

from pyrasgo.api.error import APIError
from pyrasgo.utils import naming


def build_schema(df: pd.DataFrame, include_index=False) -> dict:
    """
    Returns a dict representing the schema of a dataframe
    """
    from pandas.io.json import build_table_schema
    schema_list = build_table_schema(df)
    if not include_index:
        return {column['name']: column
                for column in schema_list['fields'] if column['name'] != 'index'}
    return {column['name']: column
            for column in schema_list['fields']}


def generate_ddl(df: pd.DataFrame,
                 table_name: str,
                 append: Optional[bool] = False):
    """
    Generates a SQL statement to create a table matching the schema of a dataframe
    """
    #default is overwrite
    create_statement = "CREATE TABLE IF NOT EXISTS" if append else "CREATE OR REPLACE TABLE"
    return pd.io.sql.get_schema(df, table_name) \
        .replace("CREATE TABLE", create_statement) \
        .replace('"', '')

def confirm_df_columns(df: pd.DataFrame, dimensions: List[str], features: List[str]):
    """
    Checks whether a list of dimensions and features are in a dataframe
    """
    confirm_list_columns(list(df.columns), dimensions, features)

def confirm_list_columns(columns: list, dimensions: List[str], features: List[str]):
    """
    Checks whether a list of dimensions and features are in a list of columns
    """
    missing_dims = []
    missing_features = []
    consider = []
    for dim in dimensions:
        if dim not in columns:
            missing_dims.append(dim)
            if naming._snowflakify_name(dim) in columns:
                consider.append(naming._snowflakify_name(dim))
    for ft in features:
        if ft not in columns:
            missing_features.append(ft)
            if naming._snowflakify_name(ft) in columns:
                consider.append(naming._snowflakify_name(ft))
    if missing_dims or missing_features:
        raise APIError(f"Specified columns do not exist in dataframe: "
                        f"Dimensions({missing_dims}) Features({missing_features}) "
                        f"Consider these: ({consider})?")

def generate_unique_id() -> str:
    """
    Calculates a unique 32 char string that can be used in secure urls 
    """
    import secrets
    return secrets.token_urlsafe(32)

def map_pandas_df_type(pandas_df_type: str) -> str:
    """For a given pandas dataframe type, return the equivalent python type.
    Default to input if no match"""
    if pandas_df_type.startswith('float'):
        return 'float'
    if pandas_df_type.startswith('datetime'):
        return 'datetime'
    if pandas_df_type.startswith('int'):
        return 'integer'
    return pandas_df_type

def set_df_id(df: pd.DataFrame, experiment_id: Optional[str]) -> int:
    """
    Checks whether a df is part of an ongoing experiment and tags it with 
    the experiment id or a new id
    """
    # If ID is set via experiment, use it
    if experiment_id:
        tag_dataframe(df, {"RasgoID": experiment_id})
        return experiment_id
    # If df is already marked with an ID, keep it    
    elif df.attrs.get("RasgoID"):
        return df.attrs["RasgoID"]
    # Else calcualte a new ID
    else:
        unique_id = generate_unique_id()
        tag_dataframe(df, {"RasgoID": unique_id})
        return unique_id

def tag_dataframe(df: pd.DataFrame, attribute: dict):
    """
    Tags a dataframe with a user-defined attribute
    """
    write_back_attrs = df.attrs or {}
    write_back_attrs.update(attribute)
    df.attrs = write_back_attrs

def _snowflakify_dataframe(df: pd.DataFrame):
    """
    Renames all columns in a pandas dataframe to Snowflake compliant names in place
    """
    df.rename(columns={r: naming._snowflakify_name(r) for r in build_schema(df)},
                inplace=True)

#TODO: currently the names in this enum are string representations of pandas
# dataframe types. Can we make the names actual type objects? If so, we could
# remove a lot of random error handling going on in evaluate.py
class DataframeDataTypes(Enum):
    INT64 = "number"
    INT32 = "number"
    INT16 = "number"
    INT8 = "number"
    FLOAT64 = "number"
    FLOAT32 = "number"
    FLOAT16 = "number"
    FLOAT8 = "number"
    UINT64 = "number"
    UINT32 = "number"
    UINT16 = "number"
    UINT8 = "number"
    DATETIME64 = "string"
    OBJECT = "string"
    STRING = "string"
    BOOL = "boolean"
