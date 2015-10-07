##############################################################################
# LogFile.py
# Copyright (c) 2015 Thomas Kerr
# Tom Kerr PA at gmail dot com
#
# Released under the MIT License (MIT). 
# See http://opensource.org/licenses/MIT
#
# Modification History:
# 10/03/2015 - Tom Kerr
# Created.
##############################################################################

##
# @file
# Python support class for the SerialTestRunner application.
# Encapsulates a test log file.
##

import os
import sys
import time  

##
# @class
# LogFile class to encapsulate a test log file.
# Operations on an uninitialized log file are ignored.
##
class LogFile(object):

    ##
    # @brief
    # Initialize the LogFile object.
    #
    # @param logFileName Optional name of a log file to initialize.
    #
    # @return An initialized LogFile object
    ##
    def __init__(self, logFileName = None):
        self._file = None
        self.Name = logFileName
        if logFileName is not None:
            self.open(logFileName)
            
            
    ##
    # @brief
    # Open and initialize a log file.
    #
    # @param logFileName Name of a log file to initialize
    ##
    def open(self, logFileName):
        self.Name = logFileName
        self._file = open(logFileName, 'w')
        self.writeline(str(os.path.basename(sys.argv[0]) + " " + 
            time.strftime("%Y-%m-%d %H:%M:%S")))
        
        
    ##
    # @brief
    # Write data to the log file.
    #
    # @param data Data string to write.
    ##
    def write(self, data):
        if self.Name is not None:
            self._file.write(data)
        
        
    ##
    # @brief
    # Write data to the log file, terminated with a newline.
    #
    # @param data Data string to write.
    ##
    def writeline(self, data):
        if self.Name is not None:
            self._file.write(data)    
            self._file.write("\n")
        
        
    ##
    # @brief
    # Close the log file.
    ##      
    def close(self):
        if self.Name is not None:
            self._file.close()
        
# End of file.