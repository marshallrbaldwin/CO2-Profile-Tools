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
For this reason, there are a number of "get" methods 