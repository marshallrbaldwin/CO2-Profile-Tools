# CO2-Profile-Tools

This repository contains two python scripts: FlightData.py and mavlogdump.py.
The mavlogdump.py script does not need to be used by the user.
It does however need to be in the same directory (folder) as the FlightData.py if .BIN files will be converted.

## Flight Data class

This class reads in raw data from an ALL csv file and stores it in a Pandas dataframe.

### Helper Methods for Generating ALL CSV

For each of these methods, the filename is assumed to be "0000000X.\{filetype\}" with X being the flight number.

#### convert_BIN_to_CSV(flightNum)

This method will extract CO<sub>2</sub>  