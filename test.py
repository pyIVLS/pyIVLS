import pyvisa

rm = pyvisa.ResourceManager("@py")
print(rm.list_resources("?*"))
keithley_add = "192.168.001.005"
keithley_port = 5025
Keithley_visa = f"TCPIP::{keithley_add}::{keithley_port}::SOCKET"
session = rm.open_resource(Keithley_visa)
print("\n Open Successful!")
session.read_termination = "\n"
session.write_termination = "\n"
command = "*IDN?"
print("Command: " + command)
print("IDN: " + str(session.query(command)))


"""
# ==========================================================================
# Function to initialize the instrument
def instrumentInit():
  
    try :
        # Clear the event status register and all prior errors in the queue
        instrumentDirectSocket.sendall("*CLS\n")
        
        # Reset instrument and via *OPC? hold-off for reset completion.
        instrumentDirectSocket.sendall("*RST;*OPC?\n")
        opComplete = instrumentDirectSocket.recv(8)
        #print("Operation complete detection = " + resetComplete
        
        # Assert a Identification query
        instrumentDirectSocket.sendall("*IDN?\n")
        idnResults = instrumentDirectSocket.recv(255)
        print("Identification results = " + idnResults)

    except socket.error:
        #Send failed
        print('Send failed')
        instrumentDirectSocket.exit()
    

import socket  # For sockets
import sys	    # For exit
import struct  # Allows for parsing of binary bin block data
import matplotlib.pyplot as plt # For plotting data results as stimulus - response arrays.
import time # Used as a sleep timer. 

from pylab import *

try:
	#create an AF_INET, STREAM socket (TCP)
	instrumentDirectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
	print('Failed to create socket. Error code: ' + str(msg))

print('Socket Created')

# Alter this host name, or IP address, in the line below to accommodate your specific instrument
host = "192.168.001.005" # Or you could utilize an IP address.

# Alter the socket port number in the line below to accommodate your 
# specific instrument socket port. Traditionally, most Keysight Technologies, 
# Agilent Technologies, LAN based RF instrumentation socket ports use 5025. 
# Refer to your specific instrument User Guide for additional details.
port = 5025
#
# A delay time variable for the sleep function call, unit is seconds
# For clarification of the use of the waitTime variable used in the sleep timer call
# please refer to any one of these function calls and the notes on the timer use:
    # getDataAsAsciiTransfer() - FUNCTION
    # getDataAsBinBlockTransfer() - FUNCTION 
    # getStimulusArrayAsBinBlock() - FUNCTION
waitTime = 0.2
#

# The measureSelectFormat variable may be used in future releases.
# The following notes are an exceprt from the determineDataArraySize(): function call
# and are repeated below for clarity
   # Those formats returning one dimensional arrays are 
   # MLINear,MLOGarithmic,PHASe,UPHase 'Unwrapped phase,
   # IMAGinary,REAL,SWR,GDELay 'Group Delay,KELVin,FAHRenheit,CELSius. 
   # Those FORMats returning    # 2x number of points data arrays (for FDATA query) are POLar,'
   # SMITh,'SADMittance 'Smith Admittance
# Start by setting the measSelectFormat variable to "" null. 
measSelectFormat = ""

# Variables for the center frequency, frequency span, 
# IF Bandwidth and Number of Trace Points.
centerFrequency =  10.24E9
frequencySpan = 1E9
ifBandWidth = 1000
sweepPoints = 201

try:
	remote_ip = socket.gethostbyname( host )
except socket.gaierror:
	#could not resolve
	print('Hostname could not be resolved. Exiting')

print('Ip address of ' + host + ' is ' + remote_ip)

# Given the instrument's computer name or IP address and socket port number now
# connect to the instrument remote server socket connection. At this point we
# are instantiating the instrument as an LAN SOCKET CONNECTION.
instrumentDirectSocket.connect((remote_ip , port))

print('Socket Connected to ' + host + ' on ip ' + remote_ip)

instrumentInit()
"""
