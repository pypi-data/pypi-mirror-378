from biomatools.utils import formats

false= False
weather_table_example = {
			"ColumnNames": [
				"AtmosphericPressure",
				"CO2concentration",
				"WaterTemperatureMinimum",
				"WaterTemperatureMaximum",
				"LeafWetnessDuration",
				"IsEvapotrPresent",
				"IsVpdPresent",
				"IsHumidityPresent",
				"AirRelativeHumidityMinimum",
				"AirRelativeHumidityMaximum",
				"Windspeed",
				"VapourPressureDeficit",
				"SnowDepth",
				"Precipitation",
				"Average_temperature",
				"AirTemperatureMinimum",
				"AirTemperatureMaximum",
				"Grid_no",
				"SoilEvaporation",
				"ReferenceEvapotranspiration",
				"Date",
				"SurfaceOzoneConcentration",
				"GlobalSolarRadiation",
				"IsCO2Present"
			],
			"Name": "weather",
			"Rows": [
				[
					"NaN",
					"NaN",
					"NaN",
					"NaN",
					0,
					false,
					false,
					false,
					"NaN",
					70.6,
					"NaN",
					"NaN",
					"NaN",
					0.0,
					6.4,
					"NaN",
					6.4,
					"50",
					"NaN",
					"NaN",
					"2021-03-02T00:00:00Z",
					"NaN",
					"NaN",
					false
				],
				[
					"NaN",
					"NaN",
					"NaN",
					"NaN",
					0,
					false,
					false,
					false,
					"NaN",
					70.5,
					"NaN",
					"NaN",
					"NaN",
					0.0,
					6.3,
					"NaN",
					6.3,
					"50",
					"NaN",
					"NaN",
					"2021-03-02T01:00:00Z",
					"NaN",
					"NaN",
					false
				]
            ]
    }

location_table_example = {
			"ColumnNames": [
				"Grid_no",
				"Altitude",
				"Latitude",
				"Longitude",
				"Distance_to_coast"
			],
			"Name": "locations",
			"Rows": [
				[
					"50",
					-1000,
					"NaN",
					"NaN",
					"NaN"
				]
			]
		}

def test_bioma_table():
    assert formats.is_bioma_table(location_table_example)
'''
def test_bioma_location_table():
    assert formats.is_bioma_location(location_table_example)

def test_bioma_weather_table():
    assert formats.is_bioma_weather(weather_table_example)
'''