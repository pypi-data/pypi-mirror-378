import inspect
import logging
import pandas as pd
import json

from biomatools.utils.abs import AbstractBioMATable
from biomatools.utils.formats import (
    is_bioma_location,
    is_bioma_table,
    is_bioma_weather,
    prepare_df,
)
from biomatools.utils.naming import (
    BIOMA_LOCATION_COLUMNS,
    BIOMA_LOCATION_NAME,
    BIOMA_WEATHER_COLUMNS,
    BIOMA_WEATHER_NAME,
)


class InvalidWeatherDictionaryError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class InvalidLocationDictionaryError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class BioMATable(AbstractBioMATable):
    """A Data Table in the BioMA application"""

    def __init__(self, Name: str, Rows, ColumnNames, NotNullFields = None):

        self.Name = Name
        self.Rows = Rows
        self.ColumnNames = ColumnNames
        self.NotNullFields = NotNullFields # this is apparently nullable

    @classmethod
    def from_dict(cls, env):
        """This is mostly used to build the object from the output returned by Web Services"""
        if is_bioma_table(env):
            return cls(
                **{
                    k: v
                    for k, v in env.items()
                    if k in inspect.signature(cls).parameters
                }
            )

    @classmethod
    def from_series(cls, name, **kwargs):
        """Builds the table concatenating multiple named series passed as argument"""
        cols = [label for label, _ in kwargs.items()]
        data = [value for _, value in kwargs.items()]
        df = pd.concat(data, axis=1).reset_index()
        df.columns = cols
        return cls.from_df(name, df)

    @classmethod
    def from_df(cls, Name: str, env: pd.DataFrame, include_index=False):
        """This is mostly used to build the object from the data included in your beloved Excel files"""
        columns = env.columns
        # here columns that have at least one value
        not_null_columns = [
            colname for colname in columns if any(pd.not_na(env[colname]))
        ]
        data = env.to_records(index=include_index)
        return cls(Name, Rows=data, ColunNames=columns, NotNullFields=not_null_columns)

    def to_df(self):
        return pd.DataFrame.from_records(self.Rows, columns=self.ColumnNames)

    def toJSON(self):
        return json.dumps(self, default=lambda o: vars(o), sort_keys=True)

    def json_serialize(self):
        """Tables have to be formatted as a JSON *string* to be
        digested by the BioMA web services, as weird as it sounds!"""
        return self.toJSON()


class BioMAWeatherTable(BioMATable):

    def __init__(self, Rows, NotNullFields=[]):
        super().__init__(
            BIOMA_WEATHER_NAME,
            Rows,
            ColumnNames=BIOMA_WEATHER_COLUMNS,
            NotNullFields=NotNullFields,
        )

    @classmethod
    def from_dict(cls, env):
        """This is mostly used to build the object from the output returned by Web Services"""
        if is_bioma_weather(env):
            return cls(
                **{
                    k: v
                    for k, v in env.items()
                    if k in inspect.signature(cls).parameters
                }
            )
        else:
            raise InvalidWeatherDictionaryError(
                "input dictionary is not a valid BioMA weather object"
            )

    @classmethod
    def from_df(cls, env, include_index=False, renaming=None):
        w = prepare_df(df=env, col_list=BIOMA_WEATHER_COLUMNS, renaming=renaming)
        return super().from_df(BIOMA_WEATHER_NAME, w, include_index)

    @classmethod
    def from_series(
        cls,
        AtmosphericPressure=[],
        CO2concentration=[],
        WaterTemperatureMinimum=[],
        WaterTemperatureMaximum=[],
        IsEvapotrPresent=[],
        IsVpdPresent=[],
        IsHumidityPresent=[],
        AirRelativeHumidityMinimum=[],
        Windspeed=[],
        VapourPressureDeficit=[],
        SnowDepth=[],
        AirTemperatureMinimum=[],
        AirTemperatureMaximum=[],
        SoilEvaporation=[],
        ReferenceEvapotranspiration=[],
        SurfaceOzoneConcentration=[],
        GlobalSolarRadiation=[],
        IsCO2Present=[],
        Date=[],
        Average_temperature=[],
        Precipitation=[],
        AirRelativeHumidityMaximum=[],
        LeafWetnessDuration=[],
        Grid_no=[],
    ):
        print(locals())
        return super().from_series(BIOMA_WEATHER_NAME, **locals())


class BioMALocationTable(BioMATable):

    def __init__(self, Rows, NotNullFields=[]):
        super().__init__(
            BIOMA_LOCATION_NAME,
            Rows,
            ColumnNames=BIOMA_LOCATION_COLUMNS,
            NotNullFields=NotNullFields,
        )

    @classmethod
    def from_dict(cls, env):
        """This is mostly used to build the object from the output returned by Web Services"""
        if is_bioma_location(env):
            return cls(
                **{
                    k: v
                    for k, v in env.items()
                    if k in inspect.signature(cls).parameters
                }
            )
        else:
            raise InvalidLocationDictionaryError(
                "input dictionary is not a valid BioMA location object"
            )

    @classmethod
    def from_df(cls, env, include_index=False, renaming=None):
        w = prepare_df(df=env, col_list=BIOMA_LOCATION_COLUMNS, renaming=renaming)
        return super().from_df(BIOMA_LOCATION_NAME, env, include_index)
