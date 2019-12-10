############################################################################
#                                                                          #
#                    USING THE SLIDING WINDOW PROGRAM:                     #
#                       Enter the folder name/path                         #
#             Enter the parameters that the program requests               #
#        The output files will be exported to a folder in the root         #
#                                                                          #
############################################################################
#
#   the name for "clam" was originally "clump", but clam sounds better
#
#   Clam - a class dedicated for holding multiple files (a folder of files)
#   NameData - a class dedicated for individual files
#   
#   Each NameData object's m_data and m_orig consists of an array of [time, data] pairs.
#   NameData objects may also be referred to:
#       SyncPair's m_first and m_second
#

import os
import math
#import pandas as pd
from datetime import datetime

#############
# Constants #
#############
# Features
AVG = 0
STD = 1
SLOPE = 2
MM_NORM = 3
ZS_NORM = 4
SYNC = 5
CALCS = 6
NORMS = 7
DIRAG = 8
SIGMA = 9

TOTALFEAT = 10
# Parameters
WIDTH = 0
INCRE = 1
COUNT = 2
START = 3

###=-=-=-=-=-=-= BEGIN CLASS AVGDATA =-=-=-=-=-=-=###

class AvgData:
    def __init__(self, data, params):
        self.m_data = data
        self.calc(params)

    ############################################################################################
    # calcAvg() - Calculate and produce an array of average EDA in the given window parameters

    def calc(self, params):
        sectTime = params[WIDTH]
        incrTime = params[INCRE]
        windowCt = params[COUNT]
        start = params[START]
        end = start + sectTime
        tempCt = 0

        self.m_avg = []
        # Continuously calculate averages until window is out of bounds
        while(end < len(self.m_data) and (tempCt < windowCt or windowCt <= 0)):
            num = 0.0
            # Calculate sum of data in window
            for i in range(start, end):
                num += float(self.m_data[i][1])
            self.m_avg.append(num/sectTime) # Add average to list of averages
            
            # Next window bounds
            start  += incrTime
            end    += incrTime
            tempCt += 1
        
        self.m_data = self.m_avg

###=-=-=-=-=-=-= END CLASS AVGDATA =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS STDDATA =-=-=-=-=-=-=###

class StdData:
    def __init__(self, data, params, avg):
        self.m_data = data
        self.calc(params, avg)

    ###################################################################################################
    # calcStd() - Calculate and produce an array of standard deviation in the given window parameters

    def calc(self, params, avg):
        sectTime = params[WIDTH]
        incrTime = params[INCRE]
        windowCt = params[COUNT]
        start = params[START]
        end = start + sectTime
        tempCt = 0

        self.m_std = []
        # Continuously calculate standard deviation until window is out of bounds
        # Standard Deviation:
        while(end < len(self.m_data) and (tempCt < windowCt or windowCt <= 0)):
            # 1. Take the average of the original set
            firstAvg = avg.m_data[tempCt]

            # 2. For each number of the original set, substract average, then square result
            num = 0.0
            for i in range(start, end):
                num += (math.pow((float(self.m_data[i][1]) - firstAvg), 2))

            # 3. Find the average of the new squared set
            # 4. Square root the average of the new squared set
            self.m_std.append(math.sqrt(num/sectTime))

            # Next window bounds
            start  += incrTime
            end    += incrTime
            tempCt += 1

        self.m_data = self.m_std

###=-=-=-=-=-=-= END CLASS STDDATA =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS SLOPEDATA =-=-=-=-=-=-=###

class SlopeData:
    def __init__(self, data, params):
        self.m_data = data
        self.calc(params)

    ###################################################################################################
    # calcSlope() - Calculate and produce an array of slope in the given window parameters

    def calc(self, params):
        sectTime = params[WIDTH]
        incrTime = params[INCRE]
        windowCt = params[COUNT]
        start = params[START]
        end = start + sectTime
        tempCt = 0

        self.m_slope = []
        # Continuously calculate slope until window is out of bounds
        # Slope:
        while(end < len(self.m_data) and (tempCt < windowCt or windowCt <= 0)):
            # Sum of the window (time = tnum, data = dnum)
            tnum = dnum = 0.0
            for i in range(start, end):
                tnum += float(self.m_data[i][0])
                dnum += float(self.m_data[i][1])
            
            # x is Time ; y is Data
            xavg = tnum/sectTime
            yavg = dnum/sectTime

            # Calculate average slope (line of regression)
            xtotal = ytotal = 0
            for j in range(start, end):
                xtotal += (float(self.m_data[j][0]) - xavg) * (float(self.m_data[j][1]) - yavg)
                ytotal += math.pow((float(self.m_data[j][0]) - xavg), 2)

            self.m_slope.append(xtotal/ytotal)

            # Next window bounds
            start  += incrTime
            end    += incrTime
            tempCt += 1

        self.m_data = self.m_slope

###=-=-=-=-=-=-= END CLASS SLOPEDATA =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS MMNORMDATA =-=-=-=-=-=-=###

class MMNormData:
    def __init__(self, data):
        self.m_data = data
        self.calc()

    #####################################################
    #           Calculation (min-max)
    # mMnormalize() - Normalize the value using minmax
    #           staticmethod due to not using self values

    @staticmethod
    def normalize(value, minv, maxv):
        return (value - minv)/(maxv - minv)

    ##################################################################################
    # calcmMNorm() - Calculate and replace NameData.data with minmax normalized data

    def calc(self):
        un_norm_values = []
        times = []
        for data in self.m_data: # data = [time, EDA]
            times.append(data[0])
            un_norm_values.append(float(data[1]))

        minv = min(un_norm_values)
        maxv = max(un_norm_values)

        self.m_minmax = []
        for i in range(len(times)):
            norm_value = self.normalize(un_norm_values[i], minv, maxv)
            self.m_minmax.append([times[i], norm_value])

        # Setting data to norm: If normalization was picked, is main data
        #                       If calculations were picked first, it's still main data anyway
        self.m_data = self.m_minmax

###=-=-=-=-=-=-= END CLASS MMNORMDATA =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS ZSNORMDATA =-=-=-=-=-=-=###

class ZSNormData:
    def __init__(self, data):
        self.m_data = data
        self.calc()

    #####################################################
    #           Calculation (z-score)
    # zSnormalize() - Normalize the value using zscore
    #           staticmethod due to not using self values

    @staticmethod
    def normalize(value, average, standard):
        return (value - average)/standard
        
    ##################################################################################
    # calczSNorm() - Calculate and replace NameData.data with zscore normalized data
    def calc(self):
        un_norm_values = []
        times = []
        num = total = 0

        # Append un-normalized values, times, and calculate average
        for data in self.m_data: # data = [time, EDA]
            times.append(data[0])
            un_norm_values.append(float(data[1]))
            total += float(data[1])
            num += 1

        # Find Standard Deviation
        average = total/num
        total = 0
        for val in un_norm_values:
            val = math.pow((val - average), 2)
            total += val

        sqavg = total/num
        standard = math.sqrt(sqavg)

        self.m_zscore = []
        for i in range(len(times)):
            norm_value = self.normalize(un_norm_values[i], average, standard)
            self.m_zscore.append([times[i], norm_value])
        
        self.m_data = self.m_zscore

###=-=-=-=-=-=-= END CLASS ZSNORMDATA =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS CLAM =-=-=-=-=-=-=###

class Clam:
    def __init__(self, folderPath):
        self.m_datasets = self.readFolder(folderPath)

    #
    #           PER FILE
    # readFile() - Read the file and produce an array of time-EDA pairs
    #

    def readFile(self, folderPath, fileName):
        filePath = folderPath + "\\" + fileName
        with open(filePath, "r") as dataFile:
            # Data is extracted as ["Time Data"] per line
            pairs = dataFile.readlines()

        # Data is adjusted as  [Time, Data] per line
        for i in range(len(pairs)):
            pairs[i] = pairs[i].strip()
            pairs[i] = pairs[i].split()

        return pairs

    #
    #           PER FOLDER
    # readFolder() - Take a path and produce an array of [name, arrays of time-EDA pairs]
    #

    def readFolder(self, folderPath):
        setOfNameData = []
        print("\nProcessing files in folder path: " + folderPath)
        for fileName in os.listdir(folderPath):
            if(fileName[:1] != "-"): # Exempt files begin with '-'
                print("File name: " + fileName)
                namedata = NameData(fileName, self.readFile(folderPath,fileName))
                setOfNameData.append(namedata)
        return setOfNameData

    #
    # setPairs() - If synchrony is enabled, set a member variable containing the array of pairs
    #

    def setPairs(self, pairs):
        self.m_pairs = pairs

###=-=-=-=-=-=-= END CLASS CLAM =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS NAMEDATA =-=-=-=-=-=-=###

class NameData:
    def __init__(self, name, data):
        self.m_name = name # original filename
        self.m_orig = data # array of [time, data] (BEFORE NORMALIZATION [if applicable])
        self.m_data = data # array of [time, data]

    # The following calculation-related arrays are single lists example: m_avg = [data, data, data, data, ...]

    def calcAvg(self, params):
        self.m_avg = AvgData(self.m_data, params)

    def calcStd(self, params):
        self.m_std = StdData(self.m_data, params, self.m_avg)

    def calcSlope(self, params):
        self.m_slope = SlopeData(self.m_data, params)

    def calcMMnorm(self):
        self.m_NormData = MMNormData(self.m_orig)
        self.m_data = self.m_NormData.m_data

    def calcZSnorm(self):
        self.m_NormData = ZSNormData(self.m_orig)
        self.m_data = self.m_NormData.m_data


    #######################################################################################################
    # writeFile() - Writes the output files for both calculation and normalization depending on writeType

    def writeFile(self, outputPath, params, writeType, doFeat, normType = -1):
        try:
            dataLength = len(self.m_data)
            calcs = []
            if(writeType == CALCS):
                sectTime = params[WIDTH]
                incrTime = params[INCRE]
                windowCt = params[COUNT]
                startPos = params[START]

                if(doFeat[AVG]):
                    calcs.append(self.m_avg.m_data)
                if(doFeat[STD]):
                    calcs.append(self.m_std.m_data)
                if(doFeat[SLOPE]):
                    calcs.append(self.m_slope.m_data)

            # newName: AVG_ct#_width_increment_start_originalfile.txt
            newFName = ""
            if(writeType == CALCS):
                newFName = "CALCS_ct" + str(windowCt) + "_w" + str(sectTime) + "_i" + str(incrTime) + "_s" + str(startPos) + "_" + self.m_name
            elif(writeType == NORMS):
                newFName = "NORM_" + self.m_name
                if(normType == MM_NORM):
                    newFName = "NORM_MM_" + self.m_name
                if(normType == ZS_NORM):
                    newFName = "NORM_ZS_" + self.m_name
            
            newFPath = outputPath + newFName

            # Write new file
            with open(newFPath, "w+") as newF:
                
                ##########################
                ### Calculation Output ###
                ##########################

                if(writeType == CALCS):
                    # Name of the original file
                    if(doFeat[NORMS]):
                        newF.write("[NOTE] File was normalized prior to calculation.\n\n")
                    newF.write("Calculations of file: " + self.m_name + "\n\n")

                    # Writing details of the windows
                    newF.write("[Details]\n")
                    newF.write("Window Count: %s\n" % (windowCt))
                    newF.write("Window width: %s lines of data, or %s seconds\n" % (sectTime, sectTime/4))
                    newF.write("Increments: Every %s lines of data, or %s seconds\n" % (incrTime, incrTime/4))
                    newF.write("Starting Position: line %s, or %s seconds\n\n" % (startPos, startPos/4))
                    # newF.write("Timestamps are exclusive. Notation: [start, end)\n\n")

                    headers = "Time:\t\t\t\t"
                    if(doFeat[AVG]):
                        headers = headers + "Average\t\t"
                    if(doFeat[STD]):
                        headers = headers + "Standard Dev.\t"
                    if(doFeat[SLOPE]):
                        headers = headers + "Slope\t\t"

                    newF.write(headers + "\n")

                    # List of the timestamps and average per timestamp
                    dataRange = windowCt
                    if(dataRange <= 0): # Window count was set to unlimited
                        dataRange = int(len(calcs[0])) # No need to check which is the least since same window count as other calcs
                    for i in range(dataRange):
                        start = (startPos/4) + (i * (incrTime/4))
                        end = (startPos/4) + (i * (incrTime/4)) + (sectTime/4) - (1/4) # Subtract .25 (1 data count) since end is exclusive

                        # Timestamps
                        newWrite = '{:<7}'.format(str(start)) + " secs - " + '{:>7}'.format(str(end)) + " secs:"

                        # Calculations
                        for j in range(len(calcs)):
                            # Calculated Data
                            newWrite = newWrite + "\t" + str(round(calcs[j][i], 9))

                        newWrite = newWrite + "\n"
                        newF.write(newWrite)

                ############################
                ### Normalization Output ###
                ############################

                if(writeType == NORMS):
                    norms = self.m_NormData.m_data
                    for val in norms:
                        time = val[0]
                        EDA = val[1]

                        newF.write("%s\t\t%s \n" % (time, EDA))

            # Output Confirmation
            if(writeType == CALCS):
                print("[SAFE] Calculations output file for \"%s\" created!" % self.m_name)
            elif(writeType == NORMS):
                print("[SAFE] Normalized output file for \"%s\" created!" % self.m_name)

            # File info returned for fileList.txt [size, name]
            fileInfo = [os.stat(newFPath).st_size, newFName]
            return fileInfo
        except:
            if(writeType == CALCS):
                print("[ERROR] Calculations output file for \"%s\" failed!" % self.m_name)
            elif(writeType == NORMS):
                print("[ERROR] Normalized output file for \"%s\" failed!" % self.m_name)
            
            # Return dummy info for fileList.txt [size, name]
            failedName = "[FAILED] " + newFName
            fileInfo = [0, failedName]
            return fileInfo

###=-=-=-=-=-=-= END CLASS NAMEDATA =-=-=-=-=-=-=###



###=-=-=-=-=-=-= BEGIN CLASS SYNCPAIR =-=-=-=-=-=-=###

class SyncPair:
    def __init__(self, first = None, second = None):
        if(second == None):
            self.m_first = first
            self.m_second = second
        else:
            if("_TL_" in second.m_name):
                self.m_first = second
                self.m_second = first
            else:
                self.m_first = first
                self.m_second = second
        
        self.m_maxlen = len(self.m_first.m_data)
        if(self.m_second is not None):
            # Initialize the DA vars
            self.m_DA_count = 0
            self.m_DA_match = []

            # Initialize the SM vars
            self.m_SM_diffs = []

            # Correct the maxlen (should be the lesser of the two)
            if(len(self.m_second.m_data) < self.m_maxlen): # Use lessthan to prevent OOB exceptions
                self.m_maxlen = len(self.m_second.m_data)
    
    #######################################################################################################
    # calcMatch() - Calculate the amount of matches for Directional Agreement
    def calcMatch(self):
        # number of matches
        self.m_DA_count = 0
        # array of 1/0 to indicate matches, -1 is null
        self.m_DA_match = []

        if(self.m_second is not None):
            tempA = self.m_first.m_data[0][1]
            tempB = self.m_second.m_data[0][1]
            prevsigA = "x"
            prevsigB = "x"

            self.m_DA_match.append([0, prevsigA, prevsigB])

            for i in range(1, self.m_maxlen):
                entry = [i, "", ""] # Default entry
                if(self.m_first.m_data[i][1] > tempA):
                    entry[1] = "+"
                elif(self.m_first.m_data[i][1] < tempA):
                    entry[1] = "-"
                else:
                    entry[1] = prevsigA

                if(self.m_second.m_data[i][1] > tempB):
                    entry[2] = "+"
                elif(self.m_second.m_data[i][1] < tempB):
                    entry[2] = "-"
                else:
                    entry[2] = prevsigB

                if(entry[1] == entry[2]):
                    self.m_DA_count += 1

                self.m_DA_match.append(entry)
                
                tempA = self.m_first.m_data[i][1]
                tempB = self.m_second.m_data[i][1]
                prevsigA = entry[1]
                prevsigB = entry[2]
    
    #######################################################################################################
    # calcDiffs() - Calculate the difference values of the pair

    def calcDiffs(self):
        # array of time and float values (difference between two points)
        # Will have [time, data] pairs due to having somewhat similar output to normalized data
        self.m_SM_diffs = []

        if(self.m_second is not None):
            for i in range(self.m_maxlen):
                diffVal = abs(self.m_first.m_data[i][1] - self.m_second.m_data[i][1])
                self.m_SM_diffs.append([self.m_first.m_data[i][0], diffVal])


    #######################################################################################################
    # writeFile() - Writes the output files for both calculation and normalization depending on writeType

    def writeFile(self, outputPath, params, writeType, doFeat):
        try:
            dataLength = len(self.m_first.m_data)
            calcs = []
            if(writeType == CALCS):
                sectTime = params[WIDTH]
                incrTime = params[INCRE]
                windowCt = params[COUNT]
                startPos = params[START]
                if(self.m_second is not None):
                    if(doFeat[AVG]):
                        calcs.append([self.m_first.m_avg.m_data, self.m_second.m_avg.m_data])
                    if(doFeat[STD]):
                        calcs.append([self.m_first.m_std.m_data, self.m_second.m_std.m_data])
                    if(doFeat[SLOPE]):
                        calcs.append([self.m_first.m_slope.m_data, self.m_second.m_slope.m_data])
                else:
                    if(doFeat[AVG]):
                        calcs.append([self.m_first.m_avg.m_data, None])
                    if(doFeat[STD]):
                        calcs.append([self.m_first.m_std.m_data, None])
                    if(doFeat[SLOPE]):
                        calcs.append([self.m_first.m_slope.m_data, None])

            sessFile = self.m_first.m_name.split("_")
            # 0        1  2    3     4          5      6         7       8
            # Session#_ID_DATE_COLOR_PAIRMEMBER_BANDID_STARTTIME_ENDTIME_"PROC".txt

            sessPos = sessFile[0].find("Session")
            sessID = sessFile[0][sessPos + 7:]
            sessDate = sessFile[2]
            sessEnd = sessFile[6] + "_" + sessFile[7] + "_" + sessFile[8]
            
            sessName = "SYNC_Sess" + sessID
            self.m_name = sessName + "_" + sessDate + "_" + sessEnd
            newFName = ""
            if(writeType == CALCS):
                newFName = "CALCS_ct" + str(windowCt) + "_w" + str(sectTime) + "_i" + str(incrTime) + "_s" + str(startPos) + "_" + self.m_name
            if(writeType == DIRAG):
                newFName = "DIRAG_" + self.m_name
            if(writeType == SIGMA):
                newFName = "SIGMA_" + self.m_name
            
            newFPath = outputPath + newFName

            # Write new calculations or normalization file

            if(writeType == DIRAG and self.m_second is None):
                print("[WARN] Directional Agreement file for \"%s\" not created! (Dyad/Pair incomplete)" % self.m_name)
            if(writeType == SIGMA and self.m_second is None):
                print("[WARN] Signal Matching file for \"%s\" not created! (Dyad/Pair incomplete)" % self.m_name)
            else:
                with open(newFPath, "w+") as newF:
                    
                    ##########################
                    ### Calculation Output ###
                    ##########################

                    if(writeType == CALCS):
                        # Name of the original file
                        if(doFeat[NORMS]):
                            newF.write("[NOTE] File was normalized prior to calculation.\n\n")
                        if(self.m_second is not None):
                            newF.write("Calculations of files:\n" + self.m_first.m_name + "\n" + self.m_second.m_name + "\n\n")
                        else:
                            newF.write("Calculations of file:\n" + self.m_first.m_name + "\n\n")

                        # Writing details of the windows
                        newF.write("[Details]\n")
                        newF.write("Window Count: %s\n" % (windowCt))
                        newF.write("Window width: %s lines of data, or %s seconds\n" % (sectTime, sectTime/4))
                        newF.write("Increments: Every %s lines of data, or %s seconds\n" % (incrTime, incrTime/4))
                        newF.write("Starting Position: line %s, or %s seconds\n\n" % (startPos, startPos/4))
                        # newF.write("Timestamps are exclusive. Notation: [start, end)\n\n")

                        headers1 = "\t\t\t\t"
                        headers2 = "Time:\t\t\t\t"
                        if(doFeat[AVG]):
                            headers1 = headers1 + "Average\t\t\t\t"
                            if(self.m_second == None):
                                headers2 = headers2 + "Solo Data\t\t\t"
                            else:
                                headers2 = headers2 + "Team Leader\tPartner\t\t"
                        if(doFeat[STD]):
                            headers1 = headers1 + "Standard Dev.\t\t\t"
                            if(self.m_second == None):
                                headers2 = headers2 + "Solo Data\t\t\t"
                            else:
                                headers2 = headers2 + "Team Leader\tPartner\t\t"
                        if(doFeat[SLOPE]):
                            headers1 = headers1 + "Slope\t\t\t\t"
                            if(self.m_second == None):
                                headers2 = headers2 + "Solo Data\t\t\t"
                            else:
                                headers2 = headers2 + "Team Leader\tPartner\t\t"

                        newF.write(headers1 + "\n" + headers2 + "\n")

                        # List of the timestamps and average per timestamp
                        dataRange = windowCt
                        if(dataRange <= 0): # Window count was set to unlimited
                            dataRange = int(len(calcs[0][0])) 
                            # Check which is the least to avoid errors where one set is longer than the other in pairs
                            if(calcs[0][1] is not None):
                                if(int(len(calcs[0][1])) < dataRange):
                                    dataRange = int(len(calcs[0][1]))
                        for i in range(dataRange):
                            start = (startPos/4) + (i * (incrTime/4))
                            end = (startPos/4) + (i * (incrTime/4)) + (sectTime/4) - (1/4) # Subtract .25 (1 data count) since end is exclusive
                            # Timestamps
                            newWrite = '{:<7}'.format(str(start)) + " secs - " + '{:>7}'.format(str(end)) + " secs:"

                            # Calculated Data
                            for j in range(len(calcs)):
                                if(self.m_second == None):
                                    newWrite = newWrite + "\t" + str(round(calcs[j][0][i], 9)) + "\t\t"
                                else:
                                    newWrite = newWrite + "\t" + str(round(calcs[j][0][i], 9)) + "\t" + str(round(calcs[j][1][i], 9))

                            newWrite = newWrite + "\n"
                            newF.write(newWrite)

                    ##############################
                    ### Signal Matching Output ###
                    ##############################

                    elif(writeType == SIGMA and self.m_second is not None):
                        newF.write("Signal Matching data of files:\n" + self.m_first.m_name + "\n" + self.m_second.m_name + "\n\n")

                        # Writing details of the windows
                        newF.write("[Details]\n")
                        newF.write("Data Count: %s\n" % (self.m_maxlen))

                        # Calculate average of the whole set
                        temp = 0.0
                        for i in range(self.m_maxlen):
                            temp = temp + self.m_SM_diffs[i][1]
                        dataAvg = temp / self.m_maxlen
                        newF.write("Overall mean difference: %s\n\n" % (dataAvg))

                        # Data Header
                        header = "Time:\t\tDifference:\t\t\tTL Data:\t\t\tP Data:\n"
                        newF.write(header)

                        # Write data
                        for i in range(self.m_maxlen):
                            newWrite = '{:<7}'.format(str(self.m_SM_diffs[i][0])) + "\t\t" + str(self.m_SM_diffs[i][1]) + "\t\t"
                            newWrite = newWrite + str(self.m_first.m_data[i][1]) + "\t\t" + str(self.m_second.m_data[i][1]) + "\n"
                            newF.write(newWrite)

                    ####################################
                    ### Directional Agreement Output ###
                    ####################################

                    elif(writeType == DIRAG and self.m_second is not None):
                        newF.write("Directional Agreement of files:\n" + self.m_first.m_name + "\n" + self.m_second.m_name + "\n\n")

                        # Writing details of the windows
                        newF.write("[Details]\n")
                        newF.write("Data Count: %s\n" % (self.m_maxlen))
                        newF.write("Matches: %s\n\n" % (self.m_DA_count))

                        # TODO: write the code to display the matches timestamps and such
                        matchArray = [] # Array of [isMatch, TLs, Ps, startNew]:
                                        # isMatch, did they match?
                                        # TLs, sign of Team Leader 
                                        # Ps, sign of Partner
                                        # startNew, is this entry the start of a new range of match/opposites?
                        # Each DA_match entry is [position, TL sign, P sign]
                        prevA = self.m_DA_match[0][1]
                        prevB = self.m_DA_match[0][2]
                        prevMatch = (prevA == prevB and prevA != "x" and prevB != "x")

                        matchArray.append([prevMatch, prevA, prevB, False])

                        # Write the matchArray to have loop indicators
                        for i in range(1, self.m_maxlen):
                            match = self.m_DA_match[i]

                            isMatch = (match[1] == match[2] and match[1] != "x" and match[2] != "x")
                            if(isMatch):
                                if(prevA == match[1] and prevMatch == isMatch):
                                    matchArray.append([isMatch, match[1], match[2], False])
                                else:
                                    matchArray.append([isMatch, match[1], match[2], True])
                            else:
                                if(prevA == match[1] and prevB == match[2] and prevMatch == isMatch):
                                    matchArray.append([isMatch, match[1], match[2], False])
                                else:
                                    matchArray.append([isMatch, match[1], match[2], True])

                            prevMatch = isMatch
                            prevA = match[1]
                            prevB = match[2]

                        start = end = prevPos = 0
                        # Write the new Directional Agreement data
                        for i in range(len(matchArray)):
                            startNew = matchArray[i][3]

                            if(startNew):
                                end = prevPos / 4.0
                                    

                                # Build the new line
                                newWrite = '{:<7}'.format(str(start)) + " secs - " + '{:>7}'.format(str(end)) + " secs:"
                                
                                # Check the previous matchArray data to finalize + write its information
                                if(matchArray[prevPos][0]): # If previous was a match
                                    if(matchArray[prevPos][1] == "+"):
                                        signstr = "Increasing\t"
                                    if(matchArray[prevPos][1] == "-"):
                                        signstr = "Decreasing\t"
                                else: # If previous was not a match
                                    signstr = "Opposites TL: " + matchArray[prevPos][1] + " P: " + matchArray[prevPos][2]
                                    
                                # Elapsed time during the sync/desync
                                elapsed = end - start

                                newWrite = newWrite + "\t" + str(signstr) + "\tElapsed Time: " + '{:<7}'.format(str(elapsed)) + "\n"

                                # Write the new line
                                newF.write(newWrite)

                                # Begin next interval (Starting at i - 1 because it is now increasing since that point)
                                start = prevPos / 4.0

                            prevPos = i

                    ###################
                    ### End Outputs ###
                    ###################

            # Output Confirmation
            if(writeType == CALCS):
                print("[SAFE] Calculations output file for \"%s\" created!" % self.m_name)
            if(writeType == DIRAG and self.m_second is not None):
                print("[SAFE] Directional Agreement file for \"%s\" created!" % self.m_name)
            if(writeType == SIGMA and self.m_second is not None):
                print("[SAFE] Signal Matching file for \"%s\" created!" % self.m_name)

            # File info returned for fileList.txt [size, name]
            if((writeType == DIRAG and self.m_second is None) or (writeType == SIGMA and self.m_second is None)):
                fileInfo = [0, newFName]
            else:
                fileInfo = [os.stat(newFPath).st_size, newFName]
            return fileInfo
        except:
            if(writeType == CALCS):
                print("[ERROR] Calculations output file for \"%s\" failed!" % self.m_name)
            if(writeType == DIRAG):
                print("[ERROR] Directional Agreement file for \"%s\" failed!" % self.m_name)
            if(writeType == SIGMA):
                print("[ERROR] Signal Matching file for \"%s\" failed!" % self.m_name)
            
            # Return dummy info for fileList.txt [size, name]
            failedName = "[FAILED] " + newFName
            fileInfo = [0, failedName]
            return fileInfo

###=-=-=-=-=-=-= END CLASS SYNCPAIR =-=-=-=-=-=-=###

#
#           HELPER FUNCTION
# pickCalc() - Selecting what calculation to choose, data validation helper, returns choice int
#

def pickCalc(failed = False, first = True, second = True, third = True, options = [False] * TOTALFEAT):
    if(failed):
        print("\nPlease select a valid option.\n")
    # This check works because the user still has to clarify a choice first regardless.
    doNorm = True # Placeholder for recursive data validation on selecting how to normalize

    # Ask the user if they would like to normalize a dataset
    if(first):
        print("\nWould you like to normalize your data? (If no, please ensure that you are planning to use normalized data)\n")
        msg = "1. Yes\n2. No\n"
        choice = int(input(msg))
        if(choice == 2):
            doNorm = False
        if(choice < 1 or choice > 2):
            return pickCalc(True, first, second, third, options)
        first = False

    # Ask the user what method of normalization they would like to perform
    if(doNorm and not first and second):
        print("\nHow would you like to normalize? (Currently, only one at once is possible)\n")
        msg = "1. Min-Max\n2. Z-Score\n"
        nchoice = int(input(msg))
        if(nchoice == 1):
            options[MM_NORM] = True
        if(nchoice == 2):
            options[ZS_NORM] = True
        if(nchoice < 1 or nchoice > 2):
            return pickCalc(True, first, second, third, options)
    
    # Ask the user what calculation they would like to perform
    # If normalization was denied, and they choose "None", then they will have an empty output
    second = False
    if(third):
        print("\nWhat would you like to calculate? (If you normalized, calculations will be done after normalizing)\n")
        msg = "1. Averages\n2. Standard Deviation\n3. Slope per Window\n4. Both AVG and STD\n"
        msg += "5. Both STD and SLOPE\n6. Both AVG and SLOPE\n7. All of AVG, STD, and SLOPE\n8. None\n"
        choice = int(input(msg))
        if(choice == 1 or choice == 4 or choice == 6 or choice == 7):
            options[AVG] = True
        if(choice == 2 or choice == 4 or choice == 5 or choice == 7):
            options[STD] = True
        if(choice == 3 or choice == 5 or choice == 6 or choice == 7):
            options[SLOPE] = True
        if(choice == 8 and not doNorm): 
            print("\n\n\n[WARNING] You have selected not to calculate, and not to normalize, code will return blank folder.")
        if(choice < 1 or choice > 8):
            return pickCalc(True, first, second, third, options)
        third = False
    
    # Ask the user if they want to output comparisons or individual data
    print("\nWould you like to compare pairs (synchrony) or just output calculations per individual?\n")
    msg = "1. Pairs\n2. Individuals\n"
    choice = int(input(msg))
    if(choice == 1):
        options[SYNC] = True
    if(choice < 1 or choice > 2):
        return pickCalc(True, first, second, third, options)
    
    return options

#
#           HELPER FUNCTION
# pickCalc() - Selecting what calculation to choose, data validation helper, returns choice int
#

def pickParam(options):
    print("\n\nPlease enter values in counts of data (integer).")
    print("For reference, 4 counts of data equates to 1 second.\n")
    msg = "Enter the timeframe you wish to section the data with: (how much data per section)\n"
    options[WIDTH] = (int(input(msg))) # sectTime
    msg = "Enter the increment you wish to section the data with: (how much data in between sections)\n"
    options[INCRE] = (int(input(msg))) # incrTime
    msg = "Enter how many windows you wish to section the data with: (0 for no limit)\n"
    options[COUNT] = (int(input(msg))) # windowCt
    msg = "Enter the position you wish to begin sectioning: (0 is default)\n"
    options[START] = (int(input(msg))) # startPos
    return options

#
#           HELPER FUNCTION
# pickDA() - Decide if doing Directional Agreement
#

def pickDA():
    print("\n\nI recommend that your dataset is normalized before calculating Directional Agreement.")
    msg = "Would you like to calculate Directional Agreement? (y/n)\n"
    choice = str(input(msg))
    if(choice != "y" and choice != "n" and choice != "Y" and choice != "N"):
        print("Incorrect input! Please indicate y for Yes, or n for No.\n")
        return pickDA()
    elif(choice == "y" or choice == "Y"):
        return True
    elif(choice == "n" or choice == "N"):
        return False

#
#           HELPER FUNCTION
# pickSM() - Decide if doing Signal Matching
#

def pickSM():
    print("\n\nI recommend that your dataset is normalized before performing Signal Matching.")
    msg = "Would you like to perform Signal Matching? (y/n)\n"
    choice = str(input(msg))
    if(choice != "y" and choice != "n" and choice != "Y" and choice != "N"):
        print("Incorrect input! Please indicate y for Yes, or n for No.\n")
        return pickSM()
    elif(choice == "y" or choice == "Y"):
        return True
    elif(choice == "n" or choice == "N"):
        return False

#
#           HELPER FUNCTION
# updateDT() - Return a small array of datetime strings
#

def updateDT():
    # Create datetime strings
    now = datetime.now() # Contains the current datetime information
    # Ex. 1970-12-1
    date = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    # Ex. 12/1/1970
    datestr = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
    # Ex. 13h_33m_31s
    time = now.strftime("%H") + "h_" + now.strftime("%M") + "m_" + now.strftime("%S") + "s"
    # Ex. 13:31
    timestr = now.strftime("%H:%M")

    return [date, datestr, time, timestr]

#
#           DRIVER FUNCTION
# main() - driver function
#

def main():
    
    print("|==============================|\n")
    print("|                              |\n")
    print("| EDA Dataset Interpreter v2.2 |\n")
    print("|                              |\n")
    print("|==============================|\n")

    ####################
    # Folder Selection #
    ####################
    
    msg = "Enter the name of or path to the folder of data files:\n"
    folderPath = input(msg)

    # Retrieve a clam (Retrieve Clam object containing NameData objects)
    clam = Clam(folderPath)

    #####################
    # Feature Selection # [v2] - Allows the user to decide to normalize, then prompt kind of norm, then prompt calculation
    #####################

    doFeat = pickCalc()
    if(doFeat[AVG] or doFeat[STD] or doFeat[SLOPE]):
        doFeat[CALCS] = True
    if(doFeat[MM_NORM] or doFeat[ZS_NORM]):
        doFeat[NORMS] = True

    ################### For calculations only; Normalizer does not need
    # User Parameters # [v2] - Now has pre-init values rather than appending new ones
    ###################

    params = [0,0,0,0]
    if(doFeat[CALCS]):
        params = pickParam(params)

    ################
    # Calculations #
    ################

    # Do Min Max Normalization: Set min-max normalized dataset for each NameData object
    if(doFeat[MM_NORM]):
        for obj in clam.m_datasets:
            obj.calcMMnorm()

    # Do z-score Normalization: Set z-score normalized dataset for each NameData object
    if(doFeat[ZS_NORM]):
        for obj in clam.m_datasets:
            obj.calcZSnorm()

    # Do Averages: Set average dataset for each NameData object
    if(doFeat[AVG] or doFeat[STD]):
        for obj in clam.m_datasets:
            obj.calcAvg(params)

    # Do Standard Deviations: Set standard deviation dataset for each NameData object
    if(doFeat[STD]):
        for obj in clam.m_datasets:
            obj.calcStd(params)

    # Do Slopes: Set slope dataset for each NameData object
    if(doFeat[SLOPE]):
        for obj in clam.m_datasets:
            obj.calcSlope(params)

    #######################
    # SyncPair Assignment # This assumes that the dataset will only have at most 2 datasets per session
    #######################

    # Do Assignment
    if(doFeat[SYNC]):
        sessIDList = []
        for obj in clam.m_datasets:
            sessPos = obj.m_name.find("Session") + 7 # Position of the session ID
            sessIDList.append(obj.m_name[sessPos:sessPos + 1])

        # Set a temporary pair starting with [first NameData, None]
        tempPairList = [] 
        tempPair = [clam.m_datasets[0], None]
        prevSess = sessIDList[0]
        # Iterate over all NameData objects in the set
        for i in range(len(clam.m_datasets)):
            # Set a completed pair if there are two of the same session
            # In case you forget: The reason why the first Session1 object doesn't duplicate despite tempPair initializing
            #       with the first NameData object, is because it will get replaced by the second Session1 object since
            #       it will end up with sessIDList[i = 1] = second Session1 object, leaving this with
            #       tempPair = [clam.m_datasets[0], clam.m_datasets[i = 1]].
            if(sessIDList[i] == prevSess):
                tempPair[1] = clam.m_datasets[i]
            # If the session is different, create SyncPair object, then start a new pair
            else:
                tempPair = SyncPair(tempPair[0], tempPair[1])
                tempPairList.append(tempPair)
                tempPair = [clam.m_datasets[i], None]
            
            prevSess = sessIDList[i]

        tempPair = SyncPair(tempPair[0], tempPair[1]) # Set final pair
        tempPairList.append(tempPair)
        
        clam.setPairs(tempPairList)

    #########################
    # SM - DA - Calculation #
    #########################

    if(doFeat[SYNC]):
        doFeat[DIRAG] = pickDA()
        doFeat[SIGMA] = pickSM()

    # Calculate Agreement matches
    if(doFeat[DIRAG]):
        for pair in clam.m_pairs:
            pair.calcMatch()

    # Calculate Difference between each data
    if(doFeat[SIGMA]):
        for pair in clam.m_pairs:
            pair.calcDiffs()


    ########################
    # Writing Output Files # [v2.1] - Now does not get interrupted when a single file fails to write
    ########################

    try:
        # date = 0
        # datestr = 1
        # time = 2
        # timestr = 3
        DTstr = updateDT()

        locOut = [DTstr[0], DTstr[2]]
        # Info Message: Location
        print("\n\n\nWriting output files into \"\\outputs\\%s\\%s\\\"" % (locOut[0], locOut[1]))

        # Create the folders for the new calculated files and file list
        outputPath = "outputs\\" + locOut[0] + "\\" + locOut[1] + "\\"
        
        # Create the info file path
        fListPath = outputPath + "-fileList.txt"

        # Create the directory/path if not exist
        os.makedirs(os.path.dirname(fListPath), exist_ok=True)

        # Initiate writing to fileList.txt
        with open(fListPath, "w+") as fList:
            # Write the output files per calculated files
            # fList is fileList.txt writer to display list of new files

            # Initialize data size, begin Normalization
            totalDataSize = 0
            totalDataCount = 0

            # Normalization
            if(doFeat[NORMS]):
                # Min-Max Normalization #
                if(doFeat[MM_NORM]):
                    DTstr = updateDT()
                    fList.write("%s %s\t\t\t[Min-Max Normalization]\n" % (DTstr[1], DTstr[3]))
                
                    # Data Writing
                    for obj in clam.m_datasets:
                        DTstr = updateDT()
                        fileInfo = obj.writeFile(outputPath, params, NORMS, doFeat, MM_NORM)
                        fList.write("%s %s\t\t%s\t%s\n" % (DTstr[1], DTstr[3], fileInfo[0], fileInfo[1]))

                        totalDataSize += fileInfo[0]
                        totalDataCount += 1
                        
                # Z-Score Normalization #
                if(doFeat[ZS_NORM]):
                    DTstr = updateDT()
                    fList.write("%s %s\t\t\t[Z-Score Normalization]\n" % (DTstr[1], DTstr[3]))
                
                    # Data Writing
                    for obj in clam.m_datasets:
                        DTstr = updateDT()
                        fileInfo = obj.writeFile(outputPath, params, NORMS, doFeat, ZS_NORM)
                        fList.write("%s %s\t\t%s\t%s\n" % (DTstr[1], DTstr[3], fileInfo[0], fileInfo[1]))

                        totalDataSize += fileInfo[0]
                        totalDataCount += 1

            # End Normalization

            # Synchrony
            if(doFeat[SYNC]):
                # Data Writing
                if(doFeat[CALCS]):
                    DTstr = updateDT()
                    fList.write("%s %s\t\t\t[Calculations]\n" % (DTstr[1], DTstr[3]))
                    for pair in clam.m_pairs:
                        DTstr = updateDT()
                        fileInfo = pair.writeFile(outputPath, params, CALCS, doFeat)
                        fList.write("%s %s\t\t%s\t%s\n" % (DTstr[1], DTstr[3], fileInfo[0], fileInfo[1]))

                        totalDataSize += fileInfo[0]
                        totalDataCount += 1
                
                # DIRAG Writing
                if(doFeat[DIRAG]):
                    DTstr = updateDT()
                    fList.write("%s %s\t\t\t[Directional Agreement]\n" % (DTstr[1], DTstr[3]))
                    for pair in clam.m_pairs:
                        DTstr = updateDT()
                        fileInfo = pair.writeFile(outputPath, params, DIRAG, doFeat)
                        fList.write("%s %s\t\t%s\t%s\n" % (DTstr[1], DTstr[3], fileInfo[0], fileInfo[1]))

                        totalDataSize += fileInfo[0]
                        totalDataCount += 1
                
                # SIGMA Writing
                if(doFeat[SIGMA]):
                    DTstr = updateDT()
                    fList.write("%s %s\t\t\t[Signal Matching]\n" % (DTstr[1], DTstr[3]))
                    for pair in clam.m_pairs:
                        DTstr = updateDT()
                        fileInfo = pair.writeFile(outputPath, params, SIGMA, doFeat)
                        fList.write("%s %s\t\t%s\t%s\n" % (DTstr[1], DTstr[3], fileInfo[0], fileInfo[1]))

                        totalDataSize += fileInfo[0]
                        totalDataCount += 1

            # Individuals
            else:
                # Data Writing
                if(doFeat[CALCS]):
                    DTstr = updateDT()
                    fList.write("%s %s\t\t\t[Calculations]\n" % (DTstr[1], DTstr[3]))
                    for obj in clam.m_datasets:
                        DTstr = updateDT()
                        fileInfo = obj.writeFile(outputPath, params, CALCS, doFeat)
                        fList.write("%s %s\t\t%s\t%s\n" % (DTstr[1], DTstr[3], fileInfo[0], fileInfo[1]))

                        totalDataSize += fileInfo[0]
                        totalDataCount += 1
            
            fList.write("\n\t%s File(s)\t%s bytes" % (totalDataCount, totalDataSize))

        # Info Message: Completion
        print("\nFile writing has been completed.")

        # Info Message: Location
        print("Location: \"\\outputs\\%s\\%s\\\"" % (locOut[0], locOut[1]))
    except:
        print("File writing was interrupted or could not fully complete.")

# Start Program
print("\n\n\n\n\n") # Spacer (Clear Home)
main()