##############################################################################
# TestParams.py
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
# Parses a JSON file and manages test parameters for testing over a serial
# port.  The JSON file defines a set of prompts and responses for running
# a test.
##

import json
import sys       

##
# @class
# TestParamsError class to handle errors specific to the TestParams object.
## 
class TestParamsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
 

##
# @class
# TestParams class to manage test parameters.
# Intended to be used in support of the SerialTestRunner application.
#
# Test parameters are read from a JSON formatted file.
# The JSON file defines a set of prompts and responses for running a test.
# Once a JSON test file is properly parsed, the following properties are
# available:
#   + TestParams.Valid (True/False if test parameters are successfully parsed)
#   + TestParams.StartPrompt (First string to search to begin test)
#   + TestParams.StartResponse (String sent in response to start prompt)
#   + TestParams.StartTimeout (Timeout value in seconds to wait for start prompt)
#   + TestParams.EndPrompt (String that indicates end of test; script exits when detected)
#   + TestParams.Timeout (Timeout value in seconds if no serial data is received)
#   + TestParams.UserParams (Optional user prompts and responses for a specific test)
##    
class TestParams(object):

    ##
    # @brief
    # Initialize the TestParams object.
    #
    # @return An initialized TestParams object
    #
    # Exceptions: 
    #    + IOError - raised if a file I/O error occurs
    #    + ValueError - raised if a JSON parsing error occurs
    #    + TestParamsError - raised if an error occurs while parsing and 
    #        formatting the test parameters
    ##
    def __init__(self, scriptFile):
        self.Valid = False
        
        # Load the script into the UserParams property.  All non-user params
        # will be removed during the parsing process.
        f = open(scriptFile, 'r')
        self.UserParams = json.load(f)
        f.close()
        
        # Parse the JSON data into test parameters.
        self.__parse__()
        self.Valid = True
        
        
    ##
    # @brief
    # Parse the JSON dictionary into test parameters.
    # Internal function only. Not intended to be called from the outside.
    #
    # Exceptions: 
    #    + TestParamsError - raised if an error occurs while parsing and 
    #        formatting the test parameters
    ##
    def __parse__(self):
    
        self.StartPrompt = None
        self.StartResponse = None
        self.StartTimeout = 10
        self.EndPrompt = None
        self.Timeout = 10
        
        # Must have start and end prompts at a minimum.
        item = None
        try:
            item = "'start' prompt"
            self.StartPrompt   = str(self.UserParams["start"]["prompt"])
            item = "'start' response"
            self.StartResponse = str(self.UserParams["start"]["response"])  
            item = "'end' prompt"
            self.EndPrompt     = str(self.UserParams["end"]["prompt"])
        except (KeyError) as err:
            raise TestParamsError(str("Missing key " + str(err) + " in " + item))
            return
            
        # Optional parameters.
        try:
            self.StartTimeout  = int(self.UserParams["start"]["timeout"])
        except (KeyError) as err:
            pass
        try:
            self.Timeout  = int(self.UserParams["timeout"])
            del self.UserParams["timeout"]
        except (KeyError) as err:
            pass
            
        # Remove the required, non-user-defined parameters.
        del self.UserParams["start"]
        del self.UserParams["end"]
        
        # Parse the remaining user-defined prompts and responses.
        # This simply ensures that each remaining dictionary entry
        # Has a corresponding "prompt" and "response" entry.
        try:
            for k in self.UserParams.keys():
                p = str(self.UserParams[k]["prompt"])
                r = str(self.UserParams[k]["response"])
        except (KeyError, AttributeError) as err:
            raise TestParamsError("Key '" + str(k) + "': " + str(err))
            return
       
# End of file.