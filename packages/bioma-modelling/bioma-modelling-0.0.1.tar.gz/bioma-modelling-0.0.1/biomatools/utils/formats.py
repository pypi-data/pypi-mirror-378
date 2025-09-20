import logging
import numpy as np
import pandas as pd

from biomatools.utils.abs import (
    AbstractBioMAClient,
    AbstractBioMAComponent,
    AbstractBioMAObject,
)
from biomatools.utils.naming import (
    BIOMA_LOCATION_NAME,
    BIOMA_WEATHER_COLUMNS,
    BIOMA_WEATHER_NAME,
)


def bioma_table_to_dataframe(table):
    """converts a BioMA data table into a pandas DataFrame object indexed by datetime"""
    # telling pandas which are the fields containing column names and actual rows
    data_pd = pd.DataFrame(table["Rows"], columns=table["ColumnNames"])
    # parsing dates...
    data_pd["Date"] = pd.to_datetime(data_pd["Date"])
    # ... and setting them as rows index
    data_pd = data_pd.set_index("Date")
    return data_pd


def weather_table_to_dataframe(weather_table):
    """converts a BioMA weather data table into a pandas DataFrame object indexed by datetime"""
    # telling pandas which are the fields containing column names and actual rows
    weather_data_pd = bioma_table_to_dataframe(weather_table)
    # telling pandas the correct column type
    weather_data_pd["Average_temperature"] = weather_data_pd.Average_temperature.astype(
        "float"
    )
    return weather_data_pd


def prepare_df(df: pd.DataFrame, col_list, renaming=None) -> dict:
    """As BioMA tables are expected to have a fixed number of columns
    with fixed labels, we'd better format dataframes before using them
    to build Weather and/or Location objects.

    Parameters
    ----------
    df: pd.DataFrame
        the dataframe you wish to prepare for BioMA ingestion

    col_list: list
        the list of column labels the BioMA object should have

    renaming: dict
        a dictionary that desribes a renaming operation, in the form
        {"old name A": "new name A", "old name B": "new name B"}.
        Defailt: None
    """
    if renaming:
        df = df.rename(columns=renaming)
    # first let's remove columns that should not be there
    df = df.drop([c for c in df.columns if c not in col_list], axis=1)
    # than add NA columns
    for c in col_list:
        if c not in df.columns:
            df[c] = np.nan
    return df


def is_bioma_table(data: dict, expected_columns=None) -> bool:
    """Tells if a dictionary is an acceptable BioMA data table"""
    # the following is not true anymore
    # if not isinstance(data.get("NotNullFields"), list):
    #    return False
    if not isinstance(data.get("ColumnNames"), list):
        return False
    if isinstance(data.get("NotNullFields"), list):
        if len(data.get("NotNullFields")) > len(data.get("ColumnNames")):
            # how can not null fields be more than the total number of fields?
            return False
    else:
        if expected_columns is not None:
            if any([i not in expected_columns for i in data.get("ColumnNames")]):
                # this means we fire a "False" if we find some column name we would not expect
                return False
    if not isinstance(data.get("Rows"), list):
        return False
    # we did not find anything compromising here
    return True


def is_bioma_weather(data: dict) -> bool:
    if data.get("Name") == BIOMA_WEATHER_NAME:
        return is_bioma_table(data, expected_columns=BIOMA_WEATHER_COLUMNS)
    else:
        return False


def is_bioma_location(data: dict) -> bool:
    if data.get("Name") == BIOMA_LOCATION_NAME:
        return is_bioma_table(data, expected_columns=BIOMA_WEATHER_COLUMNS)
    else:
        return False


def json_serialize_component(c):
    if isinstance(c, AbstractBioMAObject):
        return c.json_serialize()
    else:
        return vars(c)


def check_bioma_type(
    expected_obj: AbstractBioMAComponent,
    found_obj: AbstractBioMAComponent,
    client: AbstractBioMAClient,
):
    """Checks if a BioMACOnfiguration belongs to the correct type"""
    if expected_obj.BioMAtype == found_obj.BioMAtype:
        return True
    if len(expected_obj.subtypes) == 0:
        try:
            expected_obj.load_subtypes(client)
        except:
            logging.info(f"Object {expected_obj.BioMAtype} has no subtypes")
    return found_obj.BioMAtype in [a.BioMAtype for a in expected_obj.subtypes]
