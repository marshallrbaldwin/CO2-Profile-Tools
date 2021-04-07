# CO2-Profile-Tools

This repository contains two python scripts: FlightData.py and mavlogdump.py.
The mavlogdump.py script does not need to be used by the user.
It does however need to be in the same directory (folder) as the FlightData.py if .BIN files will be converted.

## Flight Data class

This class reads in raw data from an ALL csv file and stores it in a Pandas dataframe. 
There are also two class variables for the sensor offsets that are applied prior to any post-processing.

### Helper Methods for Generating ALL CSV

For each of these methods, the filename is assumed to be "0000000X.\{filetype\}" with X being the flight number.
Call these methods by calling
```python
FlightData.methodName(argument)
```

#### convert_BIN_to_CSV(flightNum)

This method will extract CO<sub>2</sub>, RH/temperature, and altitude/pressure data from the BIN files into separate CSV files.

#### generate_ALL_CSV(flightNum)

This method will use the 3 CSVs generated from the BIN coversion and assembles them into a single CSV.
This data is indexed by second, and the higher frequency data from the raw CSVs is averaged over those 1 second intervals.

#### trim_ALL_CSV(flightNum, start_time, end_time)

This method is used to generated a trimmed version of the ALL csv (so that you only have the ascending portion of the flight). 
In addition to the flight number, supply integer timestamps from the CSV where you want the file to be trimmed.
These timestamps are non-inclusive.

### Flight Data Objects

A Flight Data object is a pandas dataframe that reads in data from the ALL csv. 
Note that all of the data in the dataframe is of type str. 
For this reason, there are a number of "get" methods that return a list of a column of data in the Flight Data object in the correct format. 
The timestamps will be converted into datetime objects in UTC time with
```python
data.get_UTC_times()
```
CO<sub>2</sub> data should be accessed with
```python
data.get_avgCO2_with_Offset()
```
which will return the average CO2 reading between the two sensors after the offsets have been applied to them.
Pressure data will be converted into Pascals when accessed with
```python
data.get_pressures()
```
The other getter methods
```python
data.get_altitudes()
data.get_temperatures()
```
just convert the data to floats.

Use these getter methods if you want to do your own post-processing.

## Profile Class

This class takes data from a FlightData object and processes it, applying a sensor correction and averaging data at user-supplied steps of altitude.

### Initializing a Profile Object

A profile object can be constructed with
```python
Profile(flightNum)
```
with optional arguments for correction and userHeightInput.
The correction parameter is set to "Linear" by default but will also accept "Li" and "None" as arguments.
The userHeightInput is set to a False boolean value by default.
This parameter controls whether the user needs to supply each "step" in the flight manually or lets the code generate steps will constant distance in between.
The user will be prompted for information when needed.












