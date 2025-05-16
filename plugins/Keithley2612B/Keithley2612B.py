import sys
import os
import time
from threading import Lock


'''
           settings dictionary for communicationg with hardware
           
		# s["source"] source channel: may take values [smua, smub]
		# s["drain"] dain channel: may take values [smub, smua]
		# s["type"] source inject current or voltage: may take values [i ,v]
		# s["sourcesense"] source sence mode: may take values [True - 4 wire, False - 2 wire]
		# s["drainsense"] drain sence mode: may take values [True - 4 wire, False - 2 wire]
		
		# s["single_ch"] single channel mode: may be True or False
		
		# s["pulse"] set pulsed mode: may be True - pulsed, False - continuous
		# s["pulsepause"] pause between pulses in sweep
		
		# s['sourcenplc'] integration time in nplc units
		# s["drainnplc"] integration time in nplc units
		
		# s["delay"] stabilization time mode for source: may take values [True - Auto, False - manual]
		# s["delayduration"] stabilization time duration if manual
		
		# s["draindelay"] stabilization time mode for drain: may take values [True - Auto, False - manual]
		# s["draindelayduration"] stabilization time duration if manual
		
		# s["steps"] number of points in sweep
		# s["start"] start point of sweep
		# s["end"] end point of sweep
		# s["limit"] limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode
		
		# s["sourcehighc"] high capacitance mode for source
		# s["drainhighc"] high capacitance mode for drain
		
		# s["repeat"] repeat count

		# settings for drain
		## s["drainvoltage"] voltage on drain
		## s["drainlimit"] limit for current in voltage mode or for voltage in current mode

'''


##IRtothink#### currently usbtmc is used for communication with Keithley via USB, however it may also be connected via eth with pyvisa 
# In principle it may make some sence to allow user to select way to connect, or to create two different plugins one for USB connection and another one with eth connection
# It is obvious, but it is still worth to mention that not all the methods of self.rm.open_resource are the same as for usbtmc.Instrument, eventhought write and read methods are presented in both 
# For implementing both connections simultaneously some abstractions for module specific commands should be implemented e.g query in pyvisa and ask in usbtmc
# At the moment all the pyvisa methods are commented

#import pyvisa
import usbtmc
import numpy as np
import time

import pyIVLS_constants


class Keithley2612B:
   
    
    ####################################  threads

    ################################### internal functions

    ########Slots

    ########Signals

    ########Functions
    def __init__(self, dbg_mode=False):
        
        #handler for Keithley
        self.k = None
        
        # Initialize pyvisa resource manager
        #self.rm = pyvisa.ResourceManager("@py")
             
        # Initialize constants 
        ##IRtothink#### debug_mode may be replaced with something like logging
        self.debug_mode = dbg_mode 
        # Initialize the lock for the measurement
        self.lock = Lock()

    ## Communication functions
    def safewrite(self, command):
        try:
            self.k.write(command)
            ##IRtothink#### debug_mode may be replaced with something like logging
            #if self.debug_mode:
            #    error_code = self.k.query("print(errorqueue.next())")
            #    if "Queue Is Empty" not in error_code:
            #        print(f"Error sending command: {command}\nError code: {error_code}")
        except Exception as e:
            ##IRtodo#### mov to the log
            print(f"Exception sending command: {command}\nException: {e}")
            ##IRtothink#### some exception handling should be implemented
            raise e
        #finally:
        #    if self.debug_mode:
        #        self.k.write("errorqueue.clear()")

    def safequery(self, command):
        try:
            self.k.write(command)
            return self.k.read()
        except Exception as e:
	    ##IRtodo#### mov to the log
            print(f"Exception querying command: {command}\nException: {e}")
            ##IRtothink#### some exception handling implemented
            raise e

    #def safequery(self, command):
    #    try:
    #        return self.k.query_ascii_values(command)
    #    except Exception as e:
    #        print(f"Exception querying command: {command}\nException: {e}")
    #        raise e
    def keithley_IDN(self):
        return self.k.ask("*IDN?")

    def keithley_connect(self, address):# -> status:
        """Connect to the Keithley 2612B.

        Returns [status, message]:
            0 - no error, ~0 - error (add error code later on if needed)
            message contains devices response to IDN query if devices is connected, or an error message otherwise
        """
        self.address = address
        if self.k is None: 
                #connect the device
                #### connect with pyvisa resource manager
                #self.k = self.rm.open_resource(self.address)
                #self.k.read_termination = "\n"
                #self.k.write_termination = "\n"
                ##IRtodo#### move to log
                #print(self.k.query("*IDN?"))
                #### connect with usbtmc
                self.k =  usbtmc.Instrument(self.address)

    def keithley_disconnect(self):
        ##IRtodo#### move to log
        #print("Disconnecting from Keithley 2612B")
        if self.k is not None:
            self.k.close()

    ## Device functions
    def resistance_measurement(self, channel) -> float:
        """Measure the resistance at the probe.

        Returns:
            float: resistance
        """
        if channel == "smua" or channel == "smub":
            try:
                # Restore Series 2600B defaults.
                self.safewrite(f"{channel}.reset()")
                # Select current source function.
                self.safewrite(f"{channel}.source.func = {channel}.OUTPUT_DCAMPS")
                # Set source range to 10 mA.
                self.safewrite(f"{channel}.source.rangei = 10e-3")
                # Set current source to 10 mA.
                self.safewrite(f"{channel}.source.leveli = 10e-3")
                # Set voltage limit to 10 V. FIXME: Value of 1 v is arbitrary.
                self.safewrite(f"{channel}.source.limitv = 1")
                # Enable 2-wire ohms. FIXME: Check this
                self.safewrite(f"{channel}.sense = {channel}.SENSE_LOCAL")
                # Set voltage range to auto.
                self.safewrite(f"{channel}.measure.autorangev = {channel}.AUTORANGE_ON")
                # Turn on output.
                self.safewrite(f"{channel}.source.output = {channel}.OUTPUT_ON")
                # Get resistance reading.
                res = self.safequery(f"print({channel}.measure.r())")
                return res
            except Exception as e:
                print(f"Error measuring resistance: {e}")
                return -1
            finally:
                self.safewrite(f"{channel}.source.leveli = 0")
                self.safewrite(f"{channel}.source.output = {channel}.OUTPUT_OFF")
        else:
            raise ValueError(f"Invalid channel {channel}")

    def getLineFrequency(self):
        """gets line frequency from Keithley 2612B for nplc calculation.

        Returns [status, message]:
            0 - no error, ~0 - error (add error code later on if needed)
            message contains line frequency as float, or an error message otherwise
        """

        if self.k is None: 
        	self.keithley_connect()        	
        freq = float(self.safequery('print(localnode.linefreq)'))
        return freq
        
    def getIV(self, channel):
        """gets IV data

        Returns:
            list [i, v]
        """
        ##IRtothink#### some check may be added
        return list(np.array(self.safequery(f"print ({channel}.measure.iv())'").split(",")).astype(float))

    def setOutput(self, channel, outputType, value):
        """sets smu output but does not switch it ON
	channel = "smua" or "smub"
	outputType = "i" or "v"
	value = float
        """
        ##IRtothink#### some check may be added
        self.safewrite(f"{source}.source.level{outputType} = {value}")

    def get_last_buffer_value(self, channel, readings = None):
        """
        Args:
            channel (str): smua or smub

        Returns:
            list [i, v, number of point in the buffer]
        """
        ##IRtothink#### some check may be added to make sure that the value may be converted
        if readings is None:
	        readings = int(float(self.safequery(f"print({channel}.nvbuffer2.n)")))
        i_value = float(self.safequery(f"printbuffer({readings}, {readings}, {channel}.nvbuffer1)"))
        v_value = float(self.safequery(f"printbuffer({readings}, {readings}, {channel}.nvbuffer2)"))
        return [i_value, v_value, readings]

    def read_buffers(self, channel) -> np.ndarray:
        """The maximum this can read is 60000 points. This method should be used after the sweep is finished.
        Args:
            channel (str): smua or smub

        Returns:
            np.ndarray: Each element is a tuple of (current, voltage)
        """
        iv = []
        # Get the number of readings in nvbuffer2
        readings_count = int(float(self.safequery(f"print({channel}.nvbuffer2.n)")))
        i_values = self.safequery(
            f"printbuffer({1}, {readings_count}, {channel}.nvbuffer1)"
        )
        v_values = self.safequery(
            f"printbuffer({1}, {readings_count}, {channel}.nvbuffer2)"
        )

        # Add to the iv array
        ##IRtothink#### some check may be added to make sure that the value may be converted
        iv.extend(list(zip(np.array(i_values.split(",")).astype(float), np.array(v_values.split(",")).astype(float))))
        return np.array(iv)

    def abort_sweep(self, channel):
        """
        aborts the sweep
        Args:
            channel (str): smua or smub
        """
        self.safewrite(f"{channel}.abort()")

    def channelsON(self, source, drain):
        """
        swihces on channels
        """
        if not source == None:
        	self.safewrite(f"{source}.source.output={source}.OUTPUT_ON")
        if not drain == None:
        	self.safewrite(f"{drain}.source.output={drain}.OUTPUT_ON")

    def channelsOFF(self):
        """
        swihces off both channels
        """
        self.safewrite(f"smua.source.output=smua.OUTPUT_OFF")
        self.safewrite(f"smub.source.output=smub.OUTPUT_OFF")

    def keithley_init(self, s: dict):
    ##IRtothink#### pulsed operation should be rechecked if strict pulse duration will be needed
      #"""Initialize Keithley SMU for single or dual channel operation.
#	
#	Returns:
#            0 - no error
#            ~0 - error (add error code later on if needed)
#
#        Args:
#            s (dict): Configuration dictionary.
#      """
      try:
        self.safewrite("reset()")
        self.safewrite("beeper.enable=0")
        
        ####set visualization
        self.safewrite("display.screen = display.SMUA_SMUB")
        self.safewrite("format.data = format.ASCII")
        
        ####source settings
        self.safewrite(f"{s['source']}.reset()")         

        if s["sourcesense"]:
            self.safewrite(f"{s['source']}.sense = {s['source']}.SENSE_REMOTE")
        else:
            self.safewrite(f"{s['source']}.sense = {s['source']}.SENSE_LOCAL")

        self.safewrite(f"{s['source']}.measure.nplc = {s['sourcenplc']}")

        if s["sourcehighc"]:
            self.safewrite(f"{s['source']}.source.highc = {s['source']}.ENABLE")

        self.safewrite(f"{s['source']}.source.settling = {s['source']}.SETTLE_FAST_RANGE")

	####set stabilization times for source
	##IRtodo#### add delay factor to GUI
        if s["delay"]:
            self.safewrite(f"{s['source']}.measure.delay = {s['source']}.DELAY_AUTO")
            if not s["pulse"]:
                self.safewrite(f"{s['source']}.measure.delayfactor = 28.0")
            else:
                self.safewrite(f"{s['source']}.measure.delayfactor = 1.0")
        else:
            self.safewrite(f"{s['source']}.measure.delay = {s['delayduration']}")
        
	# set limits and modes
        if s["type"] == "i": # if current injection
                    if abs(s["start"]) < 1.5 and abs(s["end"]) < 1.5:
                        # if the sweep maximum is under 1.5 A, set the limit from the GUI.
                        # 10A limit is available only in pulse mode (see 2-83, p108 of manual)
                        self.safewrite(f"{s['source']}.trigger.source.limitv = {s['limit']}")
                        self.safewrite(f"{s['source']}.source.limitv = {s['limit']}")
                        
                        # Set filter for source
                        ##IRtodo#### create filter section in GUI
                        self.safewrite(f"{s['source']}.measure.filter.count = 4")
                        self.safewrite(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_ON")
                        self.safewrite(f"{s['source']}.measure.filter.type = {s['source']}.FILTER_REPEAT_AVG")
                        
                        # set autoranges on for source. see ranges on 2-83 (108) of the manual
                        self.safewrite(f"{s['source']}.measure.autorangei = {s['source']}.AUTORANGE_ON")
                        self.safewrite(f"{s['source']}.measure.autorangev = {s['source']}.AUTORANGE_ON")
                    else:
                        # If the sweep maximum is over 1.5 A, make sure pulses are as short as possible, i.e. no range adjust, no delays, no filtering:
                        self.safewrite(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_OFF")
                        self.safewrite(f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF")
                        self.safewrite(f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF")
                        self.safewrite(f"{s['source']}.source.delay = 100e-6")
                        self.safewrite(f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF")
                        self.safewrite(f"{s['source']}.source.rangei = 10")
                        self.safewrite(f"{s['source']}.source.leveli = 0")
                        self.safewrite(f"{s['source']}.source.limitv = 6")
                        self.safewrite(f"{s['source']}.trigger.source.limiti = 10")
                    self.safewrite(f"display.{s['source']}.measure.func = display.MEASURE_DCVOLTS")               
        else:  # if voltage injection
                    if abs(s["limit"]) < 1.5:
                        # if the sweep maximum is under 1.5 A, set the limit from the GUI.
                        # 10A limit is available only in pulse mode (see 2-83, p108 of manual)
                        self.safewrite(f"{s['source']}.trigger.source.limiti = {s['limit']}")
                        self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
                    else:
                        # If the current limit is over 1.5 A, make sure pulses are as short as possible, i.e. no range adjust, no delays, no filtering:
                        self.safewrite(f"{s['source']}.measure.filter.enable = {s['source']}.FILTER_OFF")
                        self.safewrite(f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF")
                        self.safewrite(f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF")
                        self.safewrite(f"{s['source']}.measure.rangei = 10")
                        self.safewrite(f"{s['source']}.source.delay = 100e-6")
                        self.safewrite(f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF")
                        self.safewrite(f"{s['source']}.source.rangev = 6")
                        self.safewrite(f"{s['source']}.source.levelv = 0")
                        self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
                        self.safewrite(f"{s['source']}.trigger.source.limiti = {s['limit']}")
                    self.safewrite(f"display.{s['source']}.measure.func = display.MEASURE_DCAMPS")
   
        ####################setting up drain
        if not s["single_ch"]:
            self.safewrite(f"{s['drain']}.reset()")
            
            if s["drainsense"]:
                self.safewrite(f"{s['drain']}.sense = {s['drain']}.SENSE_REMOTE")
            else:
                self.safewrite(f"{s['drain']}.sense = {s['drain']}.SENSE_LOCAL")
            
            self.safewrite(f"{s['drain']}.measure.nplc = {s['drainnplc']}")
            
            if s["drainhighc"]:
	            self.safewrite(f"{s['drain']}.source.highc = {s['drain']}.ENABLE")
        
            self.safewrite(f"{s['drain']}.source.settling = {s['drain']}.SETTLE_FAST_RANGE")
        
            self.safewrite(f"display.{s['drain']}.measure.func = display.MEASURE_DCAMPS")
            ###set stabilization times for source
            ##IRtodo#### add delay factor to GUI
            if s["draindelay"]:
                 self.safewrite(f"{s['drain']}.measure.delay = {s['drain']}.DELAY_AUTO")
                 if not s["pulse"]:
                     self.safewrite(f"{s['drain']}.measure.delayfactor = 28.0")
                 else:
                    self.safewrite(f"{s['drain']}.measure.delayfactor = 1.0")
            else:
                    self.safewrite(f"{s['drain']}.measure.delay = {s['draindelayduration']}")
        
            # set limits and modes
            if (s["type"] == "i" and (abs(s["start"]) < 1.5 and abs(s["end"]) < 1.5)) or (s["type"] == "v" and abs(s["limit"]) >= 1.5):
                        self.safewrite(f"{s['drain']}.measure.filter.enable = {s['source']}.FILTER_OFF")
                        self.safewrite(f"{s['drain']}.source.autorangei = {s['source']}.AUTORANGE_OFF")
                        self.safewrite(f"{s['drain']}.source.autorangev = {s['source']}.AUTORANGE_OFF")
                        self.safewrite(f"{s['drain']}.source.rangei = 10")
            else:
                        ##IRtodo#### create filter section in GUI
                        self.safewrite(f"{s['drain']}.measure.filter.count = 4")
                        self.safewrite(f"{s['drain']}.measure.filter.enable = {s['drain']}.FILTER_ON")
                        self.safewrite(f"{s['drain']}.measure.filter.type = {s['drain']}.FILTER_REPEAT_AVG")
                        # set autoranges on for drain. see ranges on 2-83 (108) of the manual
                        self.safewrite(f"{s['drain']}.measure.autorangei = {s['drain']}.AUTORANGE_ON")
                        self.safewrite(f"{s['drain']}.measure.autorangev = {s['drain']}.AUTORANGE_ON")     

        return 0

      except:
        return 1

    def keithley_run_sweep(self, s: dict):# -> status:
        """Runs a single channel sweep on. Handles locking the instrument and releasing it after the sweep is started.
        This method sets the start, end, steps, type of injection and the limit. 
        
        The progress of the sweep should be followed separately with read_buffers

        Args:
            s (dict): settings dictionary

	Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        # Try and acquire the lock to make sure nothing else is running
        ##IRtothink#### is locking really needed?
        with self.lock:
            try:
                # Clear buffers, set repeats and steps, set sweep range.
                self.safewrite(f"{s['source']}.nvbuffer1.clear()")
                self.safewrite(f"{s['source']}.nvbuffer2.clear()")
                
                ####set pulse mode for single channel
                if not s["pulse"]:
                	self.safewrite(f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_HOLD")
                #### by default smuX.trigger.source.stimulus = 0, i.e. next set point in sweep will be set py source without waiting for an event (7-250, 595)
                else:
                	self.safewrite(f"{s['source']}.trigger.endpulse.action = {s['source']}.SOURCE_IDLE")
                	self.safewrite(f"trigger.timer[1].delay = {s['pulsepause']}")
                	self.safewrite("trigger.timer[1].passthrough = false")
                	self.safewrite("trigger.timer[1].count = 1")
                	self.safewrite("trigger.blender[1].orenable = true")
                	self.safewrite(f"trigger.blender[1].stimulus[1] = {s['source']}.trigger.SWEEPING_EVENT_ID")
                	self.safewrite(f"trigger.blender[1].stimulus[2] = {s['source']}.trigger.PULSE_COMPLETE_EVENT_ID")
                	self.safewrite("trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID")
                	self.safewrite(f"{s['source']}.trigger.source.stimulus = trigger.timer[1].EVENT_ID")
                
                #see trigger models on pp 3-35-36 (172-173) of the manual
                self.safewrite(f"{s['source']}.trigger.count = {s['steps']}")
                self.safewrite(f"{s['source']}.trigger.arm.count = {s['repeat']}")
                self.safewrite(f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})")

                #### initialize actions for sweep (see trigger models on pp 3-35-36 (172-173) of the manual)
                self.safewrite(f"{s['source']}.trigger.measure.iv({s['source']}.nvbuffer1, {s['source']}.nvbuffer2)")
                self.safewrite(f"{s['source']}.trigger.measure.action = {s['source']}.ENABLE")
                self.safewrite(f"{s['source']}.trigger.source.action = {s['source']}.ENABLE")
                self.safewrite(f"{s['source']}.trigger.endsweep.action = {s['source']}.SOURCE_IDLE")
                self.safewrite(f"{s['source']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID")
                if s["single_ch"]:
                	self.safewrite(f"{s['source']}.trigger.endpulse.stimulus = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID")
                    
                ####################setting up drain    
                else:   
                   self.safewrite(f"{s['drain']}.nvbuffer1.clear()")
                   self.safewrite(f"{s['drain']}.nvbuffer2.clear()")
                   
                   self.safewrite(f"{s['drain']}.trigger.count = {s['steps']}")
                   self.safewrite(f"{s['drain']}.trigger.arm.count = {s['repeat']}")
                   
                   #### initialize sweep actions
                   self.safewrite(f"{s['drain']}.trigger.measure.iv({s['drain']}.nvbuffer1, {s['drain']}.nvbuffer2)")
                   self.safewrite(f"{s['drain']}.trigger.measure.action = {s['drain']}.ENABLE")
                   self.safewrite(f"{s['drain']}.trigger.source.action = {s['drain']}.DISABLE") #do not sweep the source (see 7-243 or 590 of the manual)
                   self.safewrite(f"{s['drain']}.trigger.measure.stimulus = {s['source']}.trigger.SOURCE_COMPLETE_EVENT_ID")
                   self.safewrite("trigger.blender[2].orenable = false")
                   self.safewrite(f"trigger.blender[2].stimulus[1] = {s['source']}.trigger.MEASURE_COMPLETE_EVENT_ID")
                   self.safewrite(f"trigger.blender[2].stimulus[2] = {s['drain']}.trigger.MEASURE_COMPLETE_EVENT_ID")
                   self.safewrite(f"{s['source']}.trigger.endpulse.stimulus = trigger.blender[2].EVENT_ID")
                   
                   self.safewrite(f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS")
                   self.safewrite(f"{s['drain']}.source.levelv = {s['drainvoltage']}")
                   self.safewrite(f"{s['drain']}.source.limiti = {s['drainlimit']}") 
                   
                   # Turn on the source and trigger the sweep.
                   self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_ON")
                   self.safewrite(f"{s['drain']}.trigger.initiate()")
                       
              
                # Turn on the source and trigger the sweep.
                self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
                self.safewrite(f"{s['source']}.trigger.initiate()")
                return 0

            except:
                # if something fails, abort the measurement and turn off the source.
                self.safewrite(f"{s['source']}.abort()")
                self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_OFF")
                if not s["single_ch"]:  
                      self.safewrite(f"{s['drain']}.abort()")
                      self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_OFF")
                
                return 1

