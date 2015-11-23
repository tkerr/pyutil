##############################################################################
# SerialTestRunner.py
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
# Python application for running unit tests on a target processor over a
# serial port.
#
# Reads a JSON formatted file containing test parameters for a specific test.
# The parameters consist primarily of prompts received over the serial port  
# from the Device Under Test (DUT), and responses to send to the DUT over the 
# serial port.
#
# The application manages test execution as follows:
# + Wait for test start prompt from DUT
# + Send the test start response to the DUT
# + Continually read and parse data from the DUT over the serial port
# + If a matching user-defined prompt is found, then send the corresponding response
# + When the end propmt is received from the DUT, end the test
#
# Requires the pySerial module for access to a serial port.
# See the following:
#  + GitHub: https://github.com/pyserial/pyserial
#  + Documentation: https://pyserial.readthedocs.org/en/latest
#
# Usage:
# + See print_usage() below.
##

# Trick to allow printing to stderr.  Must be the first line in the script.
from __future__ import print_function

import getopt
import os
import serial
import sys
import time

import TestParams
import LogFile

# Global serial port read buffer.
global gReadBuffer


##
# @brief
# Print usage syntax.
#
# @return Program exits with an exit code of 2.
##
def print_usage():
    print("Usage: " + str(os.path.basename(sys.argv[0])) + " [-bonhv] <port> <params> ")
    print("  Execute a unit test on a target platform over a serial port")
    print("  <port> is the serial port device name")
    print("  <params> is a JSON file describing the prompts and responses")
    print("  -b BAUD = Set the serial port baud rate")
    print("  -o FILE = Log all serial port output to FILE")
    print("  -n NUM  = Run the test NUM times")
    print("  -h = Print this help message")
    print("  -v = Verbose printing")
    sys.exit(2)
    
    
##
# @brief
# Print an error message.
##
def print_error(msg):
    print("\n" + str(os.path.basename(sys.argv[0])) + ": " + msg, file=sys.stderr)


##
# @brief
# Prune the read buffer to keep it from growing too big over the course
# of many test runs.
###
def prune_read_buffer():
    global gReadBuffer
    
    # Prompt searches are performed on a line-by-line basis.
    # If a line break occured, discard the previous line.
    # This helps keep the read buffer from growing too large.
    lines = gReadBuffer.split("\r\n", 1)
    if (len(lines) > 1):
        gReadBuffer = lines[1]


##
# @brief
# Check for user prompts and send responses.
#
# @param port The serial port object
# @param params The TestParams object
# @param verbose Verbose flag (True/False)
# @param The LogFile object
#
# @return False if response write operation times out, or True otherwise.
###
def check_user_prompts(port, params, verbose, logfile):
    global gReadBuffer
    ok = True
    for k in params.UserParams.keys():
        prompt = str(params.UserParams[k]["prompt"])
        if (prompt in gReadBuffer):
            try:
                response = str(params.UserParams[k]["response"])
                port.write(response)
                msg = str("\nResponse sent: '" + response + "'")
                logfile.writeline(msg)
                if (verbose):
                    print(msg)
                    
                # Remove the prompt to ensure that the response is only sent once.
                gReadBuffer = gReadBuffer.replace(prompt, "", 1)

            except (serial.serialutil.SerialTimeoutException) as err:
                ok = False
                
    return ok

    
##
# @brief
# Start the test.
#
# Waits for the start prompt, and sends the start response when found.
#
# @param port The serial port object
# @param params The TestParams object
# @param verbose Verbose flag (True/False)
# @param The LogFile object
#
# @return True if test is started, or False if a timeout occurs while waiting
# for the start prompt or sending the response.
###
def start_test(port, params, verbose, logfile):
    global gReadBuffer
    gReadBuffer = ""
    gotPrompt = False
    sentResponse = False
    start = time.time()
    delta = time.time() - start
    
    # Wait for the start prompt.
    while (delta < params.StartTimeout):
    
        # Read serial port.
        if (port.in_waiting > 0):
            chunk = port.read(port.in_waiting)
            logfile.write(chunk)
            if (verbose):
                sys.stdout.write(chunk)
            gReadBuffer += chunk
            
        # Check for prompt.
        if (params.StartPrompt in gReadBuffer):
            gotPrompt = True
            
            # Remove the prompt to ensure that the response is only sent once.
            gReadBuffer = gReadBuffer.replace(params.StartPrompt, "", 1)
            break
            
        # Prune the read buffer and update the timeout time.     
        prune_read_buffer()
        delta = time.time() - start
            
    # Send the start response.
    if (gotPrompt):
        try:
            port.write(params.StartResponse)
            sentResponse = True
            msg = str("\nResponse sent: '" + params.StartResponse + "'")
            logfile.writeline(msg)
            if (verbose):
                print(msg)
        except (serial.serialutil.SerialTimeoutException) as err:
            pass
            
    # Done.
    return (gotPrompt and sentResponse)
    
    
##
# @brief
# Main program.
#
# @return One of the following exit codes:
#    + 0 = Success
#    + 1 = A test error occurred
#    + 2 = A script error occurred
###
if __name__ == "__main__":
    
    global gReadBuffer
    
    # Local initialization.
    baud            = 9600
    exit_code       = 0
    gotEndPrompt    = False
    numRuns         = 1
    logFile         = LogFile.LogFile()
    logFileName     = None
    params          = None
    port            = None
    verbose         = False
    
    # Get command line options and arguments.
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "b:o:n:hv")
    except (getopt.GetoptError) as err:
        print_error(str(err))
        print_usage()

    for (o, a) in opts:
        if (o == "-b"):
            baud = int(a)
        if (o == "-o"):
            logFileName = str(a)
        if (o == "-n"):
            numRuns = int(a)
        if (o == "-h"):
            print_usage()
        if (o == "-v"):
            verbose = True
            
    # Check argument count.
    if (len(args) < 2):
        print_error("ERROR: missing argument")
        print_usage()
        
    # Create a test parameters object from the supplied script file.
    scriptName = str(args[1])
    try:
        params = TestParams.TestParams(scriptName)
    except (IOError) as err:
        print_error("I/O error reading " + scriptName + ": " + str(err))
        sys.exit(2)
    except (ValueError) as err:
        print_error("JSON format error while parsing " + scriptName + ": " + str(err))
        sys.exit(2)
    except (TestParams.TestParamsError) as err:
        print_error("TestParams error while parsing " + scriptName + ": " + str(err))
        sys.exit(2)
        
    # Open and initialize a log file.
    if logFileName is not None:
        try:
            logFile.open(logFileName)
        except (IOError) as err:
            print_error("I/O error initializing " + logFileName + ": " + str(err))
            sys.exit(2)
            
    # Get the serial port name and try to open it.
    portName = str(args[0])
    try:
        port = serial.Serial(portName, baud, timeout = 1, write_timeout = 10)
    except (serial.serialutil.SerialException) as err:
        print_error(str(err))
        sys.exit(2)

    # Test loop.
    while (numRuns > 0):
        numRuns = numRuns - 1
        
        # Start the test.
        if (not start_test(port, params, verbose, logFile)):
            print_error("Timeout attempting to start test")
            sys.exit(1)
            
        # Continuously parse the serial port read buffer.
        # Exit when end prompt is found or timeout occurs.
        start = time.time()
        delta = time.time() - start
        while (delta < params.Timeout):
        
            # Read data from serial port.
            if (port.in_waiting > 0):
                chunk = port.read(port.in_waiting)
                start = time.time()
                gReadBuffer += chunk
                logFile.write(chunk)
                if (verbose):
                    sys.stdout.write(chunk)
                    
            # Check for end prompt.
            if (params.EndPrompt in gReadBuffer):
                gotEndPrompt = True
                break
                
            # Check for user prompts.
            if (not check_user_prompts(port, params, verbose, logFile)):
                print_error("Response write timeout")
                exit_code = 1
                break
                
            # Prune the read buffer and update the timeout time.
            prune_read_buffer()
            delta = time.time() - start
            
        # Check for timeout.
        if (not gotEndPrompt):
            print_error("Test timed out waiting for end prompt")
            exit_code = 1
            break
            
    # Cleanup.
    if (verbose):
        sys.stdout.write('\n')
    port.close()
    logFile.close()
    sys.exit(exit_code)
    
# End of file. 