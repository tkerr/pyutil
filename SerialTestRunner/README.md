# SerialTestRunner

Python application for running unit tests on a target processor over a serial port.

## Overview

Reads a JSON formatted file containing test parameters for a specific test.
The parameters consist primarily of prompts received over the serial port from the Device Under Test (DUT), and responses to send to the DUT over the serial port.

The application manages test execution as follows:
  + Wait for test start prompt from DUT
  + Send the test start response to the DUT
  + Continually read and parse data from the DUT over the serial port
  + If a matching user-defined prompt is found, then send the corresponding response
  + When the end propmt is received from the DUT, end the test

At a minimum, the unit test on the target processor must be designed to provide a test start prompt and a test end prompt.

### Usage
See the print_usage() function in SerialTestRunner.py for usage syntax.

### Return value
The script returns one of the following values:
  + 0 = Success
  + 1 = A test error occurred
  + 2 = A script error occurred
  
## Prerequisites

Requires the pySerial module for access to a serial port.
See the following:
  + GitHub: https://github.com/pyserial/pyserial
  + Documentation: https://pyserial.readthedocs.org/en/latest

## Test Parameters File

Here is an example JSON formatted test parameters file:

    {
        "start" : {
            "prompt" : "Press a key to start:",
            "response" : "A",
            "timeout" : 10
        },
    
        "end" : { "prompt" : "TEST DONE" },
    
        "timeout" : 120,
    
        "user1" : {
            "prompt" : "Example user-defined prompt",
            "response" : "Example user-defined response"
        }
    }

The "start" and "end" blocks are required.  The remaining blocks are optional.

### "start" block

The "start" block must contain "prompt" and "response" fields that specify the test start prompt and the corresponding response.
Both field entries must be strings.  In the above example, the script waits for the string "Press a key to start:" to be received over the serial port from the DUT.  When the string is received, it sends the single character "A" over the serial port to the DUT.

An optional "timeout" field specifies how long to wait (in seconds) for the start prompt before timing out and exiting the test with an error status.  The timeout value must be a positive integer.  A default value is provided if not specified.

### "end" block
The "end" block must contain a "prompt" field that specifies the test end prompt.  Once the test has started, the script scans the data received over the serial port and looks for the end prompt.  In the above example, when the string "TEST DONE" is received over the serial port, the script exits.

### "timeout" block
The "timeout" block specifies the maximum time to wait (in seconds) for serial data before ending the test with an error status.  The timeout timer is reset with each data byte received over the serial port.  This field is optional, but must be a positive integer if supplied.  A default value is provided if not specified.

### "user1" block
This shows an optional block of a user-defined prompt and response to monitor and execute while the test is in progress.  After the test has started, the script scans the data received over the serial port and looks for either the end prompt, or any user-defined prompts that are specified.  If a user-defined prompt is received, the corresponding response is sent.

User-defined block names are arbitrary, but must be unique.  The block names are ignored by the script once JSON parsing and formatting is complete.  For example, they can be named "user1", "user2", etc., or they can have more descriptive names such as "username". Zero or more user-defined prompt/response blocks can be specified.  Prompts and responses are expected to be strings.

