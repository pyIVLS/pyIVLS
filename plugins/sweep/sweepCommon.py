from datetime import datetime
import pyIVLS_constants

def create_file_header(settings, smu_settings, backVoltage = None):
            '''
            creates a header for the csv file in the old measuremnt system style
            
            input	smu_settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
            	settings dictionary for the sweep plugin	
            
            str containing the header
            
            '''

            ## header may not be optimal, thi is because it should repeat the structure of the headers produced by the old measurement station
            comment = "#####################"
            if settings["samplename"] == "":
               comment = f"{comment}\n\n measurement of {{noname}}\n\n"
            else:   
               comment = f"{comment}\n\n measurement of {settings['samplename']}\n\n" 
            comment = f"{comment}date {datetime.now().strftime('%d-%b-%Y, %H:%M:%S')}\n"
            comment = f"{comment}Keithley source {smu_settings['channel']}\n"
            comment = f"{comment}Source in {smu_settings['inject']} injection mode\n"
            if smu_settings["inject"] == "voltage":
               stepunit = "V"
               limitunit = "A"
            else:   
               stepunit = "A"
               limitunit = "V"
            if smu_settings["mode"] == "continuous":
                comment = f"{comment}Steps in sweep {smu_settings['continuouspoints']}\n"
            elif smu_settings["mode"] == "pulsed":
                comment = f"{comment}Steps in sweep {smu_settings['pulsedpoints']}\n"
            else:
                comment = f"{comment}Steps in continuous sweep {smu_settings['continuouspoints']} and in pulsed sweep {smu_settings['pulsedpoints']}\n"
            comment = comment = f"{comment}Sweep repeat for {smu_settings['repeat']} times\n"
            if smu_settings["mode"] == "continuous":
                comment = f"{comment}Start value for sweep {smu_settings['continuousstart']} {stepunit}\n"
                comment = f"{comment}End value for sweep {smu_settings['continuousend']} {stepunit}\n"
                comment = f"{comment}Limit for sweep step {smu_settings['continuouslimit']} {limitunit}\n"
                if smu_settings["continuousdelaymode"] == 'auto':
                    comment = f"{comment}Measurement stabilization period is done in AUTO mode\n"
                else:
                    comment = f"{comment}Measurement stabilization period is{smu_settings['continuousdelay']/1000} ms\n"
                ##IRtodo#### line frequency may be read from Keithley itself    
                comment = f"{comment}NPLC value {smu_settings['continuousnplc']*1000/pyIVLS_constants.LINE_FREQ} ms (for detected line frequency {pyIVLS_constants.LINE_FREQ} Hz is {smu_settings["continuousnplc"]})"
            else:
                comment = f"{comment}Start value for sweep {smu_settings['pulsedstart']} {stepunit}\n"
                comment = f"{comment}End value for sweep {smu_settings['pulsedend']} {stepunit}\n"
                comment = f"{comment}Limit for sweep step {smu_settings['pulsedlimit']} {limitunit}\n"
                if smu_settings["pulseddelaymode"] == 'auto':
                    comment = f"{comment}Measurement stabilization period is done in AUTO mode\n"
                else:
                    comment = f"{comment}Measurement stabilization period is{smu_settings['pulseddelay']/1000} ms\n"
                ##IRtodo#### line frequency may be read from Keithley itself       
                comment = f"{comment}NPLC value {smu_settings['pulsednplc']*1000/pyIVLS_constants.LINE_FREQ} ms (for detected line frequency {pyIVLS_constants.LINE_FREQ} Hz is {smu_settings["pulsednplc"]})\n"    

            comment = f"{comment}\n\n\n"   
            if smu_settings["mode"] == "continuous":
            	comment = f"{comment}Continuous operation of the source\n"
            elif smu_settings["mode"] == "pulsed":
            	comment = f"{comment}Pulse operation of the source with delays of {smu_settings['pulsedpause']} s\n"
            else:
            	comment = f"{comment}Mixed operation of the source with delays of {smu_settings['pulsedpause']} s\n"  
                ##IRtodo#### line frequency may be read from Keithley itself       
            	comment = f"{comment}NPLC value for continuous operation arm {smu_settings['continuousnplc']*1000/pyIVLS_constants.LINE_FREQ} ms (for detected line frequency {pyIVLS_constants.LINE_FREQ} Hz is {smu_settings['continuousnplc']})"
            	comment = f"{comment}Limit for continuous operation arm {smu_settings['continuouslimit']} {limitunit}\n"
            	comment = f"{comment}Start value for continuous operation arm {smu_settings['continuousstart']} {stepunit}\n"
            	comment = f"{comment}End value for continuous operation arm {smu_settings['continuousend']} {stepunit}\n"
            comment = f"{comment}\n\n"
	   
            if backVoltage is not None:
            	comment = f"{comment}Back voltage set to drain is {backVoltage} V\n"
            else:
            	comment = f"{comment}\n"
            comment = f"{comment}\n\n\n\n"
		
            comment = f"{comment}Comment: {settings['comment']}\n"
            comment = f"{comment}\n\n\n\n\n"
	   
            if smu_settings["sourcehighc"]:
                comment = f"{comment}High capacitance mode for source is enabled\n"
            else:
                comment = f"{comment}High capacitance mode for source is disabled\n"
            if not(smu_settings["singlechannel"]):
                if smu_settings["drainhighc"]:
                    comment = f"{comment}High capacitance mode for drain is enabled\n"
                else:
                    comment = f"{comment}High capacitance mode for drain is disabled\n"
            else:
                comment = f"{comment}\n"
                
            comment = f"{comment}\n\n\n\n\n\n\n\n\n"

            if smu_settings["sourcesensemode"] == "2 wire":
                comment = f"{comment}Sourse in 2 point measurement mode\n"
            elif smu_settings["sourcesensemode"] == "4 wire":
                comment = f"{comment}Sourse in 4 point measurement mode\n"
            else:
                comment = f"{comment}Source performs both 2 and 4 point measurements\n"
            if not(smu_settings["singlechannel"]):
                if smu_settings["drainsensemode"] == "2 wire":
                    comment = f"{comment}Drain in 2 point measurement mode\n"
                elif smu_settings["drainsensemode"] == "4 wire":
                    comment = f"{comment}Drain in 4 point measurement mode\n"
                else:
                    comment = f"{comment}Drain performs both 2 and 4 point measurements\n"
            else:
                comment = f"{comment}\n"

            return comment
            
def create_sweep_reciepe(smu_settings): 
	'''
	creates a recipe for measurement. Reciepe is a list of dictionaries in the form of settings dictionary for communicationg with hardware (see Keithley2612B.py). Each item of a list is  sweep
	
	input  settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
	output list of reciepes
	drainsteps :int number of steps in drain to properly form files
	sensesteps :int number of sense steps 2w/4w
	modesteps: int number of steps for continuous/pulse
	'''
	#### create measurement reciepe (i.e. settings and steps to measure)
	recipe = []
	s = {}
	#making a template for modification
	s["source"] = smu_settings["channel"] #source channel: may take values [smua, smub]
	s["drain"] = "smub" if smu_settings["channel"] == "smua" else "smua"#drain channel: may take values [smub, smua]
	s["type"] = "v" if smu_settings["inject"] == "voltage" else "i"#source inject current or voltage: may take values [i ,v]
	s["single_ch"] = smu_settings["singlechannel"] #single channel mode: may be True or False
	s["repeat"] = smu_settings["repeat"] #repeat count: should be int >0
	s["pulsepause"] = smu_settings["pulsepause"] #pause between pulses in sweep (may not be used in continuous)
	 
	s["sourcehighc"] = smu_settings["sourcehighc"]
	##IRtodo#### recalculate with inefrequency from the device. After doing this modify definition of settings["drainnplc"], settings["pulsednplc"] and settings["continuousnplc"] in Keithley2612GUI.py
	s["drainnplc"] = smu_settings["drainnplc"] #drain NPLC (may not be used in single channel mode)
	
	s["draindelay"] = smu_settings["draindelaymode"] #stabilization time before measurement for drain channel: may take values [auto, manual] (may not be used in single channel mode)
	s["draindelayduration"] = smu_settings["draindelay"] #stabilization time duration if manual (may not be used in single channel mode)
	s["drainlimit"] = smu_settings["drainlimit"] #limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
	
	s["sourcehighc"] = smu_settings["sourcehighc"]
	s["drainhighc"] = smu_settings["drainhighc"]
	if smu_settings["singlechannel"]:
		loopdrain = 1 #1 step for the drain loop
		drainstart = 0 #no voltage on drain, not needed in practice, but the variable may be used
		drainchange = 0 #step of the drain voltage, not needed in practice, but the variable may be used
	else:
		loopdrain = smu_settings["drainpoints"]
		drainstart = smu_settings["drainstart"]
		if smu_settings["drainpoints"] > 1:
			drainchange = (smu_settings["drainend"] - smu_settings["drainstart"])/(smu_settings["drainpoints"]-1)
		else:	
			drainchange = 0

	if smu_settings["sourcesensemode"]	== "2 & 4 wire":
		loopsensesource = [False, True]
	elif smu_settings["sourcesensemode"] == "2 wire":
		loopsensesource = [False]
	else:	
		loopsensesource = [True]
	if smu_settings["drainsensemode"]	== "2 & 4 wire":
		loopsensedrain = [False, True]
		if not(smu_settings["sourcesensemode"] == "2 & 4 wire"):
		    loopsensesource.append(loopsensesource[0])
	elif smu_settings["drainsensemode"] == "2 wire":	    
		loopsensedrain = [False]
	else:	
		loopsensedrain = [True]
	if len(loopsensesource) > len(loopsensedrain):
		loopsensedrain.append(loopsensedrain[0])
	for drainstep in range(loopdrain):
		s["drainvoltage"] = drainstart + drainstep*drainchange#voltage on drain
		for sensecnt,sense in enumerate(loopsensesource):
			s["sourcesense"] = sense #source sence mode: may take values [True - 4 wire, False - 2 wire]
			s["drainsense"] = loopsensedrain[sensecnt] #drain sence mode: may take values [True - 4 wire, False - 2 wire]
			if not (smu_settings["mode"] == "pulsed"):
				s["pulse"] = False# set pulsed mode: may be True - pulsed, False - continuous
				s['sourcenplc'] = smu_settings["continuousnplc"] #integration time in nplc units
				s["delay"] = smu_settings["continuousdelaymode"] #stabilization time mode for source: may take values [True - Auto, False - manual]
				s["delayduration"] = smu_settings["continuousdelay"] #stabilization time duration if manual				
				s["steps"] = smu_settings["continuouspoints"] #number of points in sweep
				s["start"] = smu_settings["continuousstart"] #start point of sweep
				s["end"] = smu_settings["continuousend"] #end point of sweep
				s["limit"] = smu_settings["continuouslimit"] #limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode
				recipe.append(s)
			if not (smu_settings["mode"] == "continuous"):
				s["pulse"] = True# set pulsed mode: may be True - pulsed, False - continuous
				s['sourcenplc'] = smu_settings["pulsednplc"] #integration time in nplc units
				s["delay"] = smu_settings["pulseddelaymode"] #stabilization time mode for source: may take values [True - Auto, False - manual]
				s["delayduration"] = smu_settings["pulseddelay"] #stabilization time duration if manual				
				s["steps"] = smu_settings["pulsedpoints"] #number of points in sweep
				s["start"] = smu_settings["pulsedstart"] #start point of sweep
				s["end"] = smu_settings["pulsedend"] #end point of sweep
				s["limit"] = smu_settings["pulsedlimit"] #limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode
				recipe.append(s)
	
	return [recipe, loopdrain, len(loopsensesource), 2 if smu_settings["mode"] == "mixed" else 1]
