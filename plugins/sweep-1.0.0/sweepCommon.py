from datetime import datetime
import copy


def create_file_header(settings, smu_settings, backVoltage=None):
    """
    creates a header for the csv file in the old measuremnt system style

    input	smu_settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
        settings dictionary for the sweep plugin

    str containing the header

    """

    ## header may not be optimal, this is because it should repeat the structure of the headers produced by the old measurement station
    comment = "#####################"
    if settings["samplename"] == "":
        comment = f"{comment}\n#\n# measurement of {{noname}}\n#\n#"
    else:
        comment = f"{comment}\n#\n# measurement of {settings['samplename']}\n#\n#"
    comment = f"{comment}date {datetime.now().strftime('%d-%b-%Y, %H:%M:%S')}\n#"
    comment = f"{comment}Keithley source {settings['channel']}\n#"
    comment = f"{comment}Source in {settings['inject']} injection mode\n#"
    if settings["inject"] == "voltage":
        stepunit = "V"
        limitunit = "A"
    else:
        stepunit = "A"
        limitunit = "V"
    if settings["mode"] == "continuous":
        comment = f"{comment}Steps in sweep {settings['continuouspoints']}\n#"
    elif settings["mode"] == "pulsed":
        comment = f"{comment}Steps in sweep {settings['pulsedpoints']}\n#"
    else:
        comment = f"{comment}Steps in continuous sweep {settings['continuouspoints']} and in pulsed sweep {settings['pulsedpoints']}\n#"
    comment = comment = f"{comment}Sweep repeat for {settings['repeat']} times\n#"
    if settings["mode"] == "continuous":
        comment = f"{comment}Start value for sweep {settings['continuousstart']} {stepunit}\n#"
        comment = f"{comment}End value for sweep {settings['continuousend']} {stepunit}\n#"
        comment = f"{comment}Limit for sweep step {settings['continuouslimit']} {limitunit}\n#"
        if settings["continuousdelaymode"] == "auto":
            comment = f"{comment}Measurement stabilization period is done in AUTO mode\n#"
        else:
            comment = f"{comment}Measurement stabilization period is{settings['continuousdelay'] / 1000} ms\n#"
        comment = f"{comment}NPLC value {settings['continuousnplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['continuousnplc']})"
    else:
        comment = f"{comment}Start value for sweep {settings['pulsedstart']} {stepunit}\n#"
        comment = f"{comment}End value for sweep {settings['pulsedend']} {stepunit}\n#"
        comment = f"{comment}Limit for sweep step {settings['pulsedlimit']} {limitunit}\n#"
        if settings["pulseddelaymode"] == "auto":
            comment = f"{comment}Measurement stabilization period is done in AUTO mode\n#"
        else:
            comment = f"{comment}Measurement stabilization period is{settings['pulseddelay'] / 1000} ms\n#"
        comment = f"{comment}NPLC value {settings['pulsednplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['pulsednplc']})\n#"

    comment = f"{comment}\n#\n#\n#"
    if settings["mode"] == "continuous":
        comment = f"{comment}Continuous operation of the source\n#"
    elif settings["mode"] == "pulsed":
        comment = f"{comment}Pulse operation of the source with delays of {settings['pulsedpause']} s\n#"
    else:
        comment = f"{comment}Mixed operation of the source with delays of {settings['pulsepause']} s\n#"
        comment = f"{comment}NPLC value for continuous operation arm {settings['continuousnplc'] * 1000 / smu_settings['lineFrequency']} ms (for detected line frequency {smu_settings['lineFrequency']} Hz is {settings['continuousnplc']})"
        comment = f"{comment}Limit for continuous operation arm {settings['continuouslimit']} {limitunit}\n#"
        comment = f"{comment}Start value for continuous operation arm {settings['continuousstart']} {stepunit}\n#"
        comment = f"{comment}End value for continuous operation arm {settings['continuousend']} {stepunit}\n#"
    comment = f"{comment}\n#\n#"

    if backVoltage is not None:
        comment = f"{comment}Back voltage set to drain is {backVoltage} V\n#"
    else:
        comment = f"{comment}\n#"
    comment = f"{comment}\n#\n#\n#\n#"

    comment = f"{comment}Comment: {settings['comment']}\n#"
    comment = f"{comment}\n#\n#\n#\n#\n#"

    if smu_settings["sourcehighc"]:
        comment = f"{comment}High capacitance mode for source is enabled\n#"
    else:
        comment = f"{comment}High capacitance mode for source is disabled\n#"
    if not (settings["singlechannel"]):
        if smu_settings["drainhighc"]:
            comment = f"{comment}High capacitance mode for drain is enabled\n#"
        else:
            comment = f"{comment}High capacitance mode for drain is disabled\n#"
    else:
        comment = f"{comment}\n#"

    comment = f"{comment}\n#\n#\n#\n#\n#\n#\n#\n#\n#"

    if settings["sourcesensemode"] == "2 wire":
        comment = f"{comment}Sourse in 2 point measurement mode\n#"
    elif settings["sourcesensemode"] == "4 wire":
        comment = f"{comment}Sourse in 4 point measurement mode\n#"
    else:
        comment = f"{comment}Source performs both 2 and 4 point measurements\n#"
    if not (settings["singlechannel"]):
        if settings["drainsensemode"] == "2 wire":
            comment = f"{comment}Drain in 2 point measurement mode\n"
        elif settings["drainsensemode"] == "4 wire":
            comment = f"{comment}Drain in 4 point measurement mode\n"
        else:
            comment = f"{comment}Drain performs both 2 and 4 point measurements\n"
    else:
        comment = f"{comment}\n"

    return comment


def create_sweep_reciepe(settings, settings_smu):
    """
    creates a recipe for measurement. Reciepe is a list of dictionaries in the form of settings dictionary for communicationg with hardware (see Keithley2612B.py). Each item of a list is  sweep

    input  settings dictionary for Keithley2612GUI.py class (see Keithley2612BGUI.py)
    output list of reciepes
    drainsteps :int number of steps in drain to properly form files
    sensesteps :int number of sense steps 2w/4w
    modesteps: int number of steps for continuous/pulse
    """
    #### create measurement reciepe (i.e. settings and steps to measure)
    recipe = []
    s = {}
    # making a template for modification
    s["source"] = settings["channel"]  # source channel: may take values depending on the channel names in smu, e.g. for Keithley 2612B [smua, smub]
    s["drain"] = settings["drainchannel"]
    s["type"] = "v" if settings["inject"] == "voltage" else "i"  # source inject current or voltage: may take values [i ,v]
    s["single_ch"] = settings["singlechannel"]  # single channel mode: may be True or False
    s["repeat"] = settings["repeat"]  # repeat count: should be int >0
    s["pulsepause"] = settings["pulsedpause"]  # pause between pulses in sweep (may not be used in continuous)
    s["drainnplc"] = settings["drainnplc"]  # drain NPLC (may not be used in single channel mode)
    s["draindelay"] = settings["draindelaymode"]  # stabilization time before measurement for drain channel: may take values [auto, manual] (may not be used in single channel mode)
    s["draindelayduration"] = settings["draindelay"]  # stabilization time duration if manual (may not be used in single channel mode)
    s["drainlimit"] = settings["drainlimit"]  # limit for current in voltage mode or for voltage in current mode (may not be used in single channel mode)
    s["sourcehighc"] = settings_smu["sourcehighc"]
    s["drainhighc"] = settings_smu["drainhighc"]
    if settings["singlechannel"]:
        loopdrain = 1  # 1 step for the drain loop
        drainstart = 0  # no voltage on drain, not needed in practice, but the variable may be used
        drainchange = 0  # step of the drain voltage, not needed in practice, but the variable may be used
    else:
        loopdrain = settings["drainpoints"]
        drainstart = settings["drainstart"]
        if settings["drainpoints"] > 1:
            drainchange = (settings["drainend"] - settings["drainstart"]) / (settings["drainpoints"] - 1)
        else:
            drainchange = 0

    if settings["sourcesensemode"] == "2 & 4 wire":
        loopsensesource = [False, True]
    elif settings["sourcesensemode"] == "2 wire":
        loopsensesource = [False]
    else:
        loopsensesource = [True]
    if settings["drainsensemode"] == "2 & 4 wire":
        loopsensedrain = [False, True]
        if not (settings["sourcesensemode"] == "2 & 4 wire"):
            loopsensesource.append(loopsensesource[0])
    elif settings["drainsensemode"] == "2 wire":
        loopsensedrain = [False]
    else:
        loopsensedrain = [True]
    if len(loopsensesource) > len(loopsensedrain):
        loopsensedrain.append(loopsensedrain[0])
    for drainstep in range(loopdrain):
        s["drainvoltage"] = drainstart + drainstep * drainchange  # voltage on drain
        for sensecnt, sense in enumerate(loopsensesource):
            s["sourcesense"] = sense  # source sence mode: may take values [True - 4 wire, False - 2 wire]
            s["drainsense"] = loopsensedrain[sensecnt]  # drain sence mode: may take values [True - 4 wire, False - 2 wire]
            if not (settings["mode"] == "pulsed"):
                s["pulse"] = False  # set pulsed mode: may be True - pulsed, False - continuous
                s["sourcenplc"] = settings["continuousnplc"]  # integration time in nplc units
                s["delay"] = settings["continuousdelaymode"]  # stabilization time mode for source: may take values [True - Auto, False - manual]
                s["delayduration"] = settings["continuousdelay"]  # stabilization time duration if manual
                s["steps"] = settings["continuouspoints"]  # number of points in sweep
                s["start"] = settings["continuousstart"]  # start point of sweep
                s["end"] = settings["continuousend"]  # end point of sweep
                s["limit"] = settings["continuouslimit"]  # limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode
                recipe.append(copy.deepcopy(s))
            if not (settings["mode"] == "continuous"):
                s["pulse"] = True  # set pulsed mode: may be True - pulsed, False - continuous
                s["sourcenplc"] = settings["pulsednplc"]  # integration time in nplc units
                s["delay"] = settings["pulseddelaymode"]  # stabilization time mode for source: may take values [True - Auto, False - manual]
                s["delayduration"] = settings["pulseddelay"]  # stabilization time duration if manual
                s["steps"] = settings["pulsedpoints"]  # number of points in sweep
                s["start"] = settings["pulsedstart"]  # start point of sweep
                s["end"] = settings["pulsedend"]  # end point of sweep
                s["limit"] = settings["pulsedlimit"]  # limit for the voltage if is in current injection mode, limit for the current if in voltage injection mode
                recipe.append(copy.deepcopy(s))

    return [recipe, loopdrain, len(loopsensesource), 2 if settings["mode"] == "mixed" else 1]
