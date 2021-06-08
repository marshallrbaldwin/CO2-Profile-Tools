# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 08:23:00 2021

@author: nimzodragonlord
"""
import sys
import pandas as pd
import csv
import os
import datetime
import statistics
from matplotlib import pyplot as plt

class FlightData():
    """ Reads in data from an ALL csv file and stores it in a Pandas dataframe along with providing static methods for file conversion
    
    :var double CO2_sensor1_offset: bench-calculated offset for CO2 sensor 1
    :var double CO2_sensor2_offset: bench-calculated offset for CO2 sensor 2
    
    
    """
    CO2_sensor1_offset = 27.69
    CO2_sensor2_offset = -16.11
    
    #Constructor that reads in data from the ALL csv file and creates a pandas dataframe
    def __init__(self, csvFilePath):
        
        """ Creates a FlightData object that is a Pandas dataframe containing the flight data
        
        :param str csvFilePath: file path to the ALL csv
        
        """
        #TODO: Add the other two temperature streams from the ALL csv
        self.dataframe = pd.read_csv(csvFilePath, skiprows=1, names=['TimeStampUTC (ms)',
                                                                     'Altitude (m)',
                                                                     'Pressure (hPa)',
                                                                     'CO2_1 (ppm)',
                                                                     'CO2_2 (ppm)',
                                                                     'TEMP1 (K)',
                                                                     'TEMP2 (K)'
                                                                     ])
    
    def get_UTC_times(self):
        """ Returns a list of datetime objects in UTC time from the\
            FlightData's unix timestamps

        """     
        
        unixTimes = [int(i) for i in self.dataframe['TimeStampUTC (ms)']]
        timesUTC = [datetime.datetime.utcfromtimestamp(i) for i in unixTimes]
        return timesUTC
    
    def get_altitudes(self):
        """ Returns a list of floats corresponding to the altitudes\
            (in meters) from the FlightData object

        """
        
        
        altitudes = [float(i) for i in self.dataframe['Altitude (m)']]
        return altitudes
    
    def get_CO2(self):
        """ Returns two lists of floats -- CO2_ppm1, CO2_ppm2 -- that\
            correspond to readings from CO2 sensors 1 and 2 in the\
            FlightData object

        """
        
        
        CO2_ppm1 = [float(i) for i in self.dataframe['CO2_1 (ppm)']]
        CO2_ppm2 = [float(i) for i in self.dataframe['CO2_2 (ppm)']]
        return CO2_ppm1, CO2_ppm2
    
    def get_avgCO2_with_Offset(self):
        """ Returns the average CO2 reading from the two sensors with the\
            sensor offsets applied

        """
        
        
        CO2_ppm1 = [float(i) for i in self.dataframe['CO2_1 (ppm)']]
        CO2_ppm2 = [float(i) for i in self.dataframe['CO2_2 (ppm)']]
        avgCO2 = [((i+self.CO2_sensor1_offset)+(j+self.CO2_sensor2_offset))/2 for i,j in zip(CO2_ppm1, CO2_ppm2)]
        return avgCO2
    
    #TODO: Determine which temperature sensors correspond to what temperature reading    
    def get_temperatures(self):
        """ Returns two lists of floats -- temperature1, temperature2 -- that\
            correspond to readings from temperature sensors in the\
            FlightData object 

        """
        temperature1 = [float(i) for i in self.dataframe['TEMP1 (K)']]
        temperature2 = [float(i) for i in self.dataframe['TEMP2 (K)']]
        return temperature1, temperature2
    
    def get_pressures(self):
        """ Returns a list of floats corresponding to the pressure readings\
            from the FlightData object in hectopascals

        """
        
        pressures = [float(i) / 100 for i in self.dataframe['Pressure (hPa)']]
        return pressures
    
    @staticmethod
    def convert_BIN_to_CSV(flightNum):
        """ Converts a BIN file to ALT, CO2, and RH CSV files 
        
        :param int flightNum: the flight number in the BIN file.\
                              Ex) 00000004.BIN -> flightNum = 4

        """

        lang = "python "
        script = "mavlogdump.py "
        keywords = ["--types ", "--format "]
        fileType = "csv "
        typelist = ["BAR2 ", "CO2 ", "RHUM "]
        typeNames = ["ALT", "CO2", "RH_TEMP"]
        
        
        for data,typeLabel in zip(typelist,typeNames):
            chunk1 = lang + script + keywords[0] + data + keywords[1] + fileType
            chunk2 = f"{str(flightNum).zfill(8)}.BIN > {str(flightNum).zfill(8)}" + typeLabel + ".csv"
            command = chunk1 + chunk2
            os.system(command)
            print(f"{str(flightNum).zfill(8)}" + typeLabel + ".csv has been generated")
        
    @staticmethod
    def generate_ALL_CSV(flightNum):
        """ Generates the ALL CSV file from the ALT, CO2, and RH CSV files

        :param int flightNum: the flight number in the BIN file.\
                              Ex) 00000004.BIN -> flightNum = 4
        """
        ALL_dataframe = pd.DataFrame(columns = ["Timestamp", "Altitude", "Pressure",
                                                "CO2 ppm 1", "CO2 ppm 2", "Temperature 1",
                                                "Temperature 2", "Temperature 3",
                                                "Temperature 4"])
        
        #these will be added to the all dataframe as columns
        timestamp_list = []
        CO2_ppm1_list = []
        CO2_ppm2_list = []
        temp1_list = []
        temp2_list = []
        temp3_list = []
        temp4_list = []
        altitude_list = []
        pressure_list = []
        
        #reading in the data
        ALT_filename = f'{str(flightNum).zfill(8)}ALT.csv'
        CO2_filename = f'{str(flightNum).zfill(8)}CO2.csv'
        RH_TEMP_filename = f'{str(flightNum).zfill(8)}RH_TEMP.csv'
        
        ALT_dataframe = pd.read_csv(ALT_filename)
        CO2_dataframe = pd.read_csv(CO2_filename)
        RH_TEMP_dataframe = pd.read_csv(RH_TEMP_filename)
        
        #setting up the time matching algorithm
        
        ALT_time = [int(round(float(i))) for i in ALT_dataframe["timestamp"]]
        CO2_time = [int(round(float(i))) for i in CO2_dataframe["timestamp"]] #doubles as RH_TEMP time too
        
        CO2_index = 0
        
        ENV_DATA_SIZE = min(len(RH_TEMP_dataframe["T1"]),len(ALT_dataframe["Alt"]))
        
        while (CO2_index<len(CO2_time)):
            
            time_bucket = [CO2_index]
            
            #our temporary data lists for each timestamp
            ppm1_temp = []
            ppm2_temp = []
            temp1_temp = [] #I know, I know... the naming scheme is sketch
            temp2_temp = []
            temp3_temp = []
            temp4_temp = []
            
            #check whether the next timestamp is the same as the current one
            while (CO2_index + 1 < len(CO2_time) and CO2_index + 1 < ENV_DATA_SIZE):
                if(CO2_time[CO2_index] == CO2_time[CO2_index+1]):
                    time_bucket.append(CO2_index + 1)
                    CO2_index += 1
                    
                
                #if it isn't the same, escape the loop and set up for the next outer one
                else:
                    CO2_index += 1
                    break
            
            bad_data_counter = 0
            
            for index in time_bucket:
                #this if statement checks for bad sensor readings
                if (CO2_dataframe["co2Val0"][index] != 0 and CO2_dataframe[" co2Val1"][index] != 0):
                    
                    ppm1_temp.append(CO2_dataframe["co2Val0"][index])
                    ppm2_temp.append(CO2_dataframe[" co2Val1"][index]) #note that this name has a random space in front >:(
                    temp1_temp.append(RH_TEMP_dataframe["T1"][index])
                    temp2_temp.append(RH_TEMP_dataframe["T2"][index])
                    temp3_temp.append(RH_TEMP_dataframe["T3"][index])
                    temp4_temp.append(RH_TEMP_dataframe["T4"][index])
                    
                else:
                    bad_data_counter += 1
                    
            #now we add the data to their respective lists
            if(bad_data_counter < len(time_bucket)):
                timestamp_list.append(CO2_time[time_bucket[0]])
                CO2_ppm1_list.append(sum(ppm1_temp)/len(ppm1_temp))
                CO2_ppm2_list.append(sum(ppm2_temp)/len(ppm2_temp))
                temp1_list.append(sum(temp1_temp)/len(temp1_temp))
                temp2_list.append(sum(temp2_temp)/len(temp2_temp))
                temp3_list.append(sum(temp3_temp)/len(temp3_temp))
                temp4_list.append(sum(temp4_temp)/len(temp4_temp))
            #emptying the bin
            time_bucket = []
            
            #escape the loop if there are no more future elements to compare
            if(CO2_index +1 >= len(CO2_time) or CO2_index + 1 == ENV_DATA_SIZE):
                break
        
        #add the lists as columns of the ALL dataframe
        ALL_dataframe["Timestamp"] = timestamp_list
        ALL_dataframe["CO2 ppm 1"] = CO2_ppm1_list
        ALL_dataframe["CO2 ppm 2"] = CO2_ppm2_list
        ALL_dataframe["Temperature 1"] = temp1_list
        ALL_dataframe["Temperature 2"] =  temp2_list
        ALL_dataframe["Temperature 3"] = temp3_list
        ALL_dataframe["Temperature 4"] =  temp4_list
        
        ALT_index = 0
        CO2_index = 0 #again, doubles for RH_TEMP index
        starting_index = 0
        
        for i in ALL_dataframe["Timestamp"]:
            
            matching_values_exist = False
            matching_time_pressures = []
            matching_time_altitudes = []
            
            while (ALT_index < len(ALT_time)):
                if(ALT_time[ALT_index] < i):
                    ALT_index += 1
                    continue
                elif (ALT_time[ALT_index] == i):
                    matching_values_exist = True
                    matching_time_pressures.append(ALT_dataframe["Press"][ALT_index])
                    matching_time_altitudes.append(ALT_dataframe["Alt"][ALT_index])
                    ALT_index += 1
                    continue
                else:
                    starting_index = ALT_index
                    break
                
            if (matching_values_exist):
                pressure_list.append(sum(matching_time_pressures)/len(matching_time_pressures))
                altitude_list.append(sum(matching_time_altitudes)/len(matching_time_altitudes))
                    
            ALT_index += 1
            CO2_index = starting_index
                
            
        ALL_dataframe["Altitude"] = altitude_list
        ALL_dataframe["Pressure"] = pressure_list
        
            
        ALL_dataframe.to_csv(f"{str(flightNum).zfill(8)}ALL.csv", index=False)
        print(f"ALL csv number {str(flightNum)} has been generated")        
    
    @staticmethod
    def trimArduPlaneCSV(base_filename, fixed_filename, start_time, end_time):
        """ Generates a trimmed CSV file without a header based on\
            supplied timestamps
            
            :param str base_filename: path to the initial CSV file
            :param str fixed_filename: path to the trimmed CSV file
            :param int start_time: timestamp to start recording values
            :param int end_time: timestamp to stop recording values
        """
        with open(base_filename, 'r') as read_file:
            csv_reader = csv.reader(read_file)
            next(csv_reader)
            with open(fixed_filename, 'w', newline='') as write_file:
                csv_writer = csv.writer(write_file)
                for row in csv_reader:            
                    if int(row[0]) > start_time and int(row[0]) < end_time: #trimming by timestamp
                        csv_writer.writerow(row)
    
    @staticmethod
    def trim_ALL_CSV(flightNum, start_time, end_time):
        """ Generates a trimmed ALL CSV file without a header based on\
            supplied timestamps
            
        :param int flightNum: the flight number in the BIN file.\
                              Ex) 00000004.BIN -> flightNum = 4
        :param int start_time: timestamp to start recording values
        :param int end_time: timestamp to stop recording values
        """
        base_filename = f"{str(flightNum).zfill(8)}ALL.csv"
        trimmed_filename = f"{str(flightNum).zfill(8)}ALL_TRIMMED.csv"
        FlightData.trimArduPlaneCSV(base_filename, trimmed_filename, start_time, end_time)
        
class Profile():
    """ A Profile object takes data from a FlightData object and processes it, 
    namely applying a pressure correction and averaging sensor data at 
    discrete steps.  
    
    :var str TIME_FORMAT: Format for start time
    """
    
    TIME_FORMAT = "%H:%M:%S"
    
    def __init__(self, flightNum, correction="Linear", userHeightInput = False):
        """ Creates a Profile object.
        
        :param int flightNum: the flight number in the BIN file.\
                              Ex) 00000004.BIN -> flightNum = 4
        :param str correction: Pressure correction to apply; linear by default.
        :param bool userHeightInput: Controls whether the user supplies every\ 
            altitude step (True), or if the user supplies only starting\
                altitude and timestep.
        """
        
        self.flightNum = flightNum
        
        #reading in a trimmed ALL csv
        trimmedFilePath = f"{str(flightNum).zfill(8)}ALL_TRIMMED.csv"
        data = FlightData(trimmedFilePath)
        
        #assigning data lists with columns from the dataframe
        self.altitude_list = data.get_altitudes()
        self.avg_ppm_list = data.get_avgCO2_with_Offset()
        temp1_list, temp2_list = data.get_temperatures()
        pressure_list = data.get_pressures()
        
        #setting the start time of the flight
        start_time_datetime = data.get_UTC_times()[0]
        start_time = start_time_datetime.strftime(self.TIME_FORMAT)
        self.start_time = start_time
        
        #setting boolean
        self.useLinearRegression = False
        self.useLiCorrection = False
        if (correction == "Linear"):
            self.useLinearRegression = True
        if (correction == "Li"):
            self.useLiCorrection = True
        
        print(f"\nYou are visualizing flight {str(flightNum)} \n")
        #creating the list of heights
        if(userHeightInput):
            prompt1 = "Please enter a height to add to the height list. "
            prompt2 = "To remove the last input, enter 'oops' and to finish, enter 'q'\n"
            userInput = input(prompt1 + prompt2)
            self.heights = []
            while userInput != 'q':
                if (userInput == "oops"):
                    self.heights.pop()
                    userInput = input(prompt1 + prompt2)
                    continue
                try:
                    height = int(userInput)
                except ValueError:
                    print("That was invalid input. Let's try that again.\n")
                    userInput = input(prompt1 + prompt2)
                    continue
                else:
                    self.heights.append(height)
                    userInput = input(prompt1 + prompt2)
        else:
            prompt = "Please enter the lowest height (this is usually around 35)\n"
            
            while True:
                try:
                    start_height = int(input(prompt))
                except ValueError:
                    print("That's not a number. Try again.\n")
                    continue
                else:
                    #we got a good value and can exit the loop
                    break
            
            prompt = "Please enter the smallest height for starting regular steps\n"
            
            while True:
                try:
                    height = int(input(prompt))
                except ValueError:
                    print("That's not a number. Try again.\n")
                    continue
                else:
                    #we got a good value and can exit the loop
                    break            
                
            prompt = "Please enter the step size\n"
            
            while True:
                try:
                    step_height = int(input(prompt))
                except ValueError:
                    print("That's not a number. Try again.\n")
                    continue
                else:
                    #we got a good value and can exit the loop
                    break        
            
            prompt = "Please enter the maximum altitude\n"
            
            while True:
                try:
                    max_height = int(input(prompt))
                except ValueError:
                    print("That's not a number. Try again.\n")
                    continue
                else:
                    #we got a good value and can exit the loop
                    break        
            
            self.heights = []
            self.heights.append(start_height)
            while height<max_height:
                self.heights.append(height)
                height += step_height 
                
        #parsing the ppms
        if(self.useLinearRegression == True):
            initial_pressure = pressure_list[0]
            offset = self.avg_ppm_list[0] - Profile.lRegression(initial_pressure, 0)
            
            pivot = Profile.lRegression(initial_pressure, offset)
            self.avg_ppm_list = [ppm + (pivot - Profile.lRegression(pressure, offset)) for ppm, pressure in zip(self.avg_ppm_list, pressure_list)]
        
        elif(self.useLiCorrection == True):
            self.avg_ppm_list = [Profile.li_correction(c, T, p) for c, T, p in zip(self.avg_ppm_list, temp1_list, pressure_list)]
        
        ppms_at_height = {}
        temps_at_height = {}
        for height in self.heights:
            ppms_at_height[f'ppms_at{str(height)}'] = []
            temps_at_height[f'temps_at_{str(height)}'] = [] 
  
        for ppm, altitude, temp in zip(self.avg_ppm_list, self.altitude_list, temp1_list):
            for height in self.heights:
                if altitude > height-10 and altitude < height+10:
                    ppms_at_height[f'ppms_at{str(height)}'].append(ppm)
                    temps_at_height[f'temps_at_{str(height)}'].append(temp)
        
        avg_ppm_at_height = []
        ppm_at_height_stdev = []
        avg_temp_at_height = []
        temp_at_height_stdev = []
        
        for height in self.heights:
            avg_ppm_at_height.append(sum(ppms_at_height[f'ppms_at{str(height)}'])/len(ppms_at_height[f'ppms_at{str(height)}']))
            ppm_at_height_stdev.append(statistics.stdev(ppms_at_height[f'ppms_at{str(height)}']))
            avg_temp_at_height.append(sum(temps_at_height[f'temps_at_{str(height)}'])/len(temps_at_height[f'temps_at_{str(height)}']))
            temp_at_height_stdev.append(statistics.stdev(temps_at_height[f'temps_at_{str(height)}']))
        
        self.avg_ppm_at_height = avg_ppm_at_height
        self.ppm_at_height_stdev = ppm_at_height_stdev
        self.avg_temp_at_height = avg_temp_at_height
        self.temp_at_height_stdev = temp_at_height_stdev
    
    def get_start_time(self):
        """ Returns a string containing the flight's start time in the format 
        of the class variable TIME_FORMAT.
        """
        return self.start_time
    
    def get_correction(self):
        """ Returns a string containing the name of the pressure correction 
        used.
        """
        if (self.useLinearRegression):
            return "Linear Regression"
        elif (self.useLiCorrection):
            return "Li Correction"
        else:
            return "None"
        
    def get_heights(self):
        """ Returns a list of the altitudes at which the sensor readings have
        been averaged around.
        """
        heights = self.heights[:]
        return heights
    
    def get_corrected_ppm_values(self):
        """
        Returns a list containing corrected ppm values using the Profile's correction
        """
        
        corrected_ppms = self.avg_ppm_list[:]
        return corrected_ppms
    
    def get_avg_ppm_at_heights(self):
        """ Returns a list of the average ppm readings for each altitude step
        """
        avg_ppm_at_heights = self.avg_ppm_at_height[:]
        return avg_ppm_at_heights
    
    def get_ppm_stdev_at_heights(self):
        """ Returns a list of the standard deviations for the CO2 readings at
        each altitude step
        """
        ppm_at_height_stdev = self.ppm_at_height_stdev[:]
        return ppm_at_height_stdev
    
    def get_avg_temp_at_heights(self):
        """ Returns a list of the average temperature readings for each 
        altitude step
        """
        avg_temp_at_height = self.avg_temp_at_height[:]
        return avg_temp_at_height
    
    def get_temp_stdev_at_heights(self):
        """ Returns a list of the standard deviations for the temperature 
        readings at each altitude step
        """        
        temp_at_height_stdev = self.temp_at_height_stdev[:]
        return temp_at_height_stdev
    
    @staticmethod
    def lRegression(pressure, offset): #avg of the 3 linear regressions from the chamber
        """ Returns an expected CO2 reading based on the
        linear regression developed in the pressure chamber
        experiment.
        
        :param double pressure: Pressure reading
        :param double offset: Difference between the first \ 
        averaged CO2 value and the regression with no offset \
        (refer to constructor code for implementation)         
        """
        slope = 0.46698
        intercept = -1.5188
        ppm = slope * pressure + intercept + offset
        return ppm

    @staticmethod
    def li_correction(c, T, p):
        """ Returns a corrected CO2 value based on the Li
        correction
        """
        return c * (1013*(T)/((25+273)*p))
    
      
    @staticmethod
    def plot_profile(flights, profile_type = "CO2", width = 7,
                     height = 10, xlabel_size = 14, ylabel_size = 14,
                     capsize = 6, marker = "D"):
        """ Creates a plot of the profile for a flight day.
        
        :param list<Profile> flights: List of Profile objects\n
        :param str profile_type: String containing the name of
        the parameter to be plotted (default "CO2," or "Temp").\n
        :param int width: width of the plot in inches; 7 default\n
        :param int height: height of the plot in inches; 10 default\n
        :param int xlabel_size: xlabel fontsize; 14 default\n
        :param int ylabel_size: ylabel fontsize; 14 default\n
        """
        if profile_type == "CO2":
            fig, axs = plt.subplots(figsize=(width,height))
            for flight in flights:
                axs.errorbar(flight.avg_ppm_at_height, flight.heights, 
                     xerr=flight.ppm_at_height_stdev, capsize=capsize, marker=marker, 
                     label=f'Starting at {flight.start_time}')
                
            axs.set_xlabel('CO2 ppm', fontsize=xlabel_size)
            axs.set_ylabel('Altitude (in meters)', fontsize=ylabel_size)
            axs.legend()
            axs.grid()
            axs.plot()
        elif profile_type == "Temp":
            fig, axs = plt.subplots(figsize=(width,height))
            for flight in flights:
                axs.errorbar(flight.avg_temp_at_height, flight.heights, 
                     xerr=flight.temp_at_height_stdev, capsize=6, marker="D", 
                     label=f'Starting at {flight.start_time}')
                
            axs.set_xlabel('Temperature °C', fontsize=xlabel_size)
            axs.set_ylabel('Altitude (in meters)', fontsize=ylabel_size)
            axs.legend()
            axs.grid()
            axs.plot()            
    
    @staticmethod
    def plot_scatter_profile(flights, profile_type = "CO2", width = 7,
                             height = 10, xlabel_size = 14, ylabel_size = 14,
                             marker = 'o', marker_size = 2):
        
        if profile_type == "CO2":
            fig, axs = plt.subplots(figsize=(width,height))
            for flight in flights:
                axs.scatter(flight.avg_ppm_list, flight.altitude_list,
                            marker = marker, s = marker_size,
                            label=f'Starting at {flight.start_time}')
                
            axs.set_xlabel('CO2 ppm', fontsize=xlabel_size)
            axs.set_ylabel('Altitude (in meters)', fontsize=ylabel_size)
            axs.legend()
            axs.grid()
            axs.plot()
        
        
        
        
        
        
        
        
        
        
        
    