
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%   Automated stage move function  %%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%% PREREQUISITIONS TO RUN SPECTROMETER %%%%%%%%%%%%%%

%%%%% MATLAB requires JAVA version >1.8.0.144 (see note to the MATLAB example from Ocean Optics techSupport)
%%%%% this may be installed with this how to
%%%%%   https://www.mathworks.com/help/compiler_sdk/java/configure-your-java-environment.html
%%%%% and setting the MATLAB_JAVAKeithley_handle system variable to the directory,
%%%%% containing the installation of JAVA
%%%%% after this MATLAB was not able to save and load Desktop
%%%%% this was solved with acording to this how to
%%%%%   https://www.mathworks.com/matlabcentral/answers/299880-matlab-2016a-error-the-desktop-configuration-was-not-saved-successfully
%%%%% particularly "I deleted java\jarext\saxon9-xpath.jar in the matlab installation location, then the error gone away, I can save layout. But I haven't fully test whether other functions break"

%%%%%%%%%%%%%% END OF PREREQUISITIONS TO RUN SPECTROMETER %%%%%%%%%%%%%%

%%%todo list%%%
%%% 2) probably it will be better to create some common structures for
%%%     X, Y, Z motors. This structure should include motor numbers, 
%%%     handlers for the motor related feilds (i.e. *_text, *_currentPos,
%%%     *_setPos). Then moveButton_Callback and updatefields may be
%%%     significantly simplified, analyzing all motors in loop
%%% 3) common structures that will contain all the headers for GUI also
%%%    should be considered
%%% 4) runButton_Callback partially repeats callback functions for
%%%    gotoButton and moveButton. Probably separate funcions for goto and
%%%    move should be created, and then they may be called from all of the
%%%    callbacks


function IVLS(varargin)
 warning('off','MATLAB:subscripting:noSubscriptsSpecified');
 %%%% supresses warning messages, when snapshot value is send directly to
 %%%% the addMatrix function
 bufreadn = 20; 
 
 result_handles = [];
 %%%%define main constants used in the script
 %%%%%
 %%% port and motor constants
 %%%%%
  motors = {'Z', 'X', 'Y'}; %order of the motors with respect to the controller board
  parameters = {'distanceToGo','currentPosition','targetPosition','maxspeed', 'speed'};  %order of the parameters returned by firmware
  portname = 'COM8';
  brate = 115200;
  delaytime = 2; %time to wait until Arduino reacts
  running = 0;
  specPreviewRunnig = 0;
 
 %%%%%
 %%% getting initialization file
 %%%%%  
 iniFileName = 'IVLS_DLT_ini_dummy.mat';
 ini = load(iniFileName);
  
 %%%%%
 %%% load sample mask
 %%%%% 
   if isempty(ini.load_mask)
       map_name = [];
       map_coord =[];
   else    
       [map_name, map_coord] = getMap(ini.load_mask);
   end  	  
 
 %%%%%
 %%% Keithley constants
 %%%%%
 KeithleyAddress = '192.168.1.5';
 KeithleyPort = 5025;

 %%%%%
 %%% Camera parameters
 %%%%%
 CamAddress = '192.168.1.2';
 
  %%%%check the calibration and get transformation coefficients if possible

  calibration_list = ini.calibration_list;
  min_calibration = 4;
  coef_X = [];
  coef_Y = [];
  if ~isempty(calibration_list)
   if ~check_calibration(calibration_list)  
    [coef_X, coef_Y] = getTransformation(calibration_list);
   end
  end
      
  table_struct = 1;
  table_calib = 2;
  table_change = 3;
  table_delete = 4;
  table_X = 5;
  table_Y = 6;
  
  save_filename ='';
 %%%%check the port handle and open the port if neccessary
% % % % % % % % % % % % % % % % % % % % % % %    global port;
% % % % % % % % % % % % % % % % % % % % % % %    if ~isempty(port)
% % % % % % % % % % % % % % % % % % % % % % %      if strcmp(port.status, 'closed')
% % % % % % % % % % % % % % % % % % % % % % %        port = openport(portname, brate); 
% % % % % % % % % % % % % % % % % % % % % % %        pause(delaytime);
% % % % % % % % % % % % % % % % % % % % % % %      end
% % % % % % % % % % % % % % % % % % % % % % %    else
% % % % % % % % % % % % % % % % % % % % % % %        port = openport(portname, brate);  
% % % % % % % % % % % % % % % % % % % % % % %        pause(delaytime);
% % % % % % % % % % % % % % % % % % % % % % %    end  
  port = NaN;
 
 function out_dummyFunc = dummy_func(in_data)
     out_dummyFunc = 0;   
 end    
   
 IVanalysis = @(pathAnalysis, filenameAnanlysis, handleAnalysis){}; 
 IVinProc = @(in_data)dummy_func(in_data); 
  
 %%%close port 
  % closeport(port);
  % %%%% closing the arduino port leads to lose of the position values 

 %%%%%%%%%%%
 %%% function that allows stage control and creates a GUI for it
 %%%%%%%%%%% 
 
%    function actionMoveActivated(port)   
    keyMove = 5e8;
 %%   resp = getresponse(port); 
    [~, motorXind] = find(strcmp(motors,'X'));
    [~, motorYind] = find(strcmp(motors,'Y'));
    [~, motorZind] = find(strcmp(motors,'Z'));
    [~, currentPositionInd] = find(strcmp(parameters,'currentPosition'));
    [~, targetPositionInd] = find(strcmp(parameters,'targetPosition'));
    
    regionOfInterest_handle = [];
    reg_coordX1 = 1;
    reg_coordY1 = 2;
    reg_coordX2 = 3;
    reg_coordY2 = 4;
    
    expTimeSwap = [1 10 100 1000 1e4 1e5 1e6];
    intTimeSwap = [1 10 100 1000];
    
    %%%%Keithley structure
    
      Keithley.handle = [];
% % % Keithley.steps %%int
% % % Keithley.repeat %%int
% % % Keithley.start %%int
% % % Keithley.end %%int
% % % Keithley.limit %%float
% % % Keithley.delay %%str "off"/time in sec before measurement
% % % Keithley.pulse %%str "off"/time in sec pause between pulses
% % % Keithley.source %%str "smua"/"smub"
% % % Keithley.drain %%str "smua"/"smub"
% % % Keithley.type %%str "i"/"v"
% % % Keithley.drainLimit %% str
% % % Keithley.freq %% float
% % % Keithley.drainVoltage %% str "off"/value
% % % Keithley.nplc %% str
% % % Keithley.sense %% true/false
% % % Keithley.sense_drain %% true/false
% % % Keithley.single_ch %% true/false
% % % keithley.highC %% true/false
    
%%%%% structure for spectrometer
    specDevices_list = [];

    %%%%camera structure
    
    cam_struct.handle = [];
    cam_struct.address =  CamAddress;
    cam_struct.expTime = ini.setExpTime_value;
    cam_struct.imgSize = ini.imgSize_value;
    cam_struct.imgOffset = ini.imgOffset_value;
    cam_struct.reverseX = ini.reverseX_value;
    cam_struct.reverseY = ini.reverseY_value;
    
    
    [fig_handle, cam_struct] = start_camera(cam_struct);
    hManager = uigetmodemanager(fig_handle);
    [hManager.WindowListenerHandles.Enabled] = deal(false);
    set(fig_handle,'KeyPressFcn', @key_pressed_fcn);
    %set(fig_handle,'WindowKeyPressFcn', @(fig_obj,eventDat) key_pressed_fcn(fig_obj,eventDat));
    set(fig_handle,'CloseRequestFcn',@my_closereq);
    axes_handle = findobj(fig_handle, 'type', 'Axes');
    set(zoom(fig_handle), 'ActionPostCallback',@blockKeyHandler);
    set(pan(fig_handle), 'ActionPostCallback',@blockKeyHandler);
    
    handle_tabgroup = uitabgroup('Parent', fig_handle, 'SelectionChangedFcn', {@tabChangedCB});
    handle_tab_stage = uitab('Parent',  handle_tabgroup, 'Title', 'Stage control');
    handle_tab_Keithley = uitab('Parent',  handle_tabgroup, 'Title', 'Keithley control');
    handle_tab_camera = uitab('Parent',  handle_tabgroup, 'Title', 'Camera control');
    handle_tab_spectra = uitab('Parent',  handle_tabgroup, 'Title', 'Spectrometer controls');
    handle_tab_DLT = uitab('Parent',  handle_tabgroup, 'Title', 'DLT');
    handle_tab_run = uitab('Parent',  handle_tabgroup, 'Title', 'Run');
    handle_tab_result = uitab('Parent',  handle_tabgroup, 'Title', 'Result');
    
    %%% Stage control gui
    
    set(axes_handle, 'Parent', handle_tab_stage, 'Position', [0.05 0.05 0.7 0.9]);
    X_text = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','text', 'String','X position','Units', 'normalized', 'Position',[0.75,0.95,0.25,0.03]);
    X_currentPos = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','text','String','0','Units', 'normalized', 'Position',[0.75,0.90,0.11,0.04]);
    X_setPos = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','edit','String','0','Units', 'normalized', 'Position',[0.87,0.90,0.11,0.04]);
    Y_text = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','text', 'String','Y position','Units', 'normalized', 'Position',[0.75,0.87,0.25,0.03]);
    Y_currentPos = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','text','String','0','Units', 'normalized', 'Position',[0.75,0.82,0.11,0.04]);
    Y_setPos = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','edit','String','0','Units', 'normalized', 'Position',[0.87,0.82,0.11,0.04]);
    Z_text = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','text', 'String','Z position','Units', 'normalized', 'Position',[0.75,0.79,0.25,0.03]);
    Z_currentPos = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','text','String','0','Units', 'normalized', 'Position',[0.75,0.74,0.11,0.04]);
    Z_setPos = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','edit','String','0','Units', 'normalized', 'Position',[0.87,0.74,0.11,0.04]);
    updateButton = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','pushbutton','String', 'Update', 'Units','normalized', 'Position',[0.77,0.70,0.10,0.04], 'Callback',{@updateButton_Callback});
    moveButton = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','pushbutton','String','Move','Units', 'normalized', 'Position',[0.88,0.70,0.10,0.04], 'Callback',{@moveButton_Callback});
    addMarkerButton = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String', 'Add marker', 'Units','normalized', 'Position',[0.77,0.65,0.10,0.04], 'Callback',{@addMarkerButton_Callback});
    clearMarkerButton = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String','Clear markers','Units', 'normalized', 'Position',[0.88,0.65,0.10,0.04], 'Callback',{@clearMarkerButton_Callback});
    
    loadMask_label = uicontrol('Parent', handle_tab_stage, 'Style','text', 'String','Load new mask file','Units', 'normalized', 'Position',[0.75,0.62,0.25,0.03]);
    [~,mask_name]= fileparts(ini.load_mask);
    loadMask_edit = uicontrol('Parent', handle_tab_stage, 'Style','edit','String',mask_name,'Units', 'normalized', 'Position',[0.77,0.57,0.10,0.04]);
    loadMask_Button = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String','load','Units', 'normalized', 'Position',[0.88,0.57,0.10,0.04], 'Callback',{@loadMask_Button_Callback});
    
    newCalibrationButton = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String','New calibration','Units', 'normalized', 'Position',[0.77,0.50,0.10,0.04], 'Callback',{@newCalibrationButton_Callback});
    check_calibration_list = check_calibration(calibration_list);
    if size(calibration_list,1) < min_calibration || check_calibration_list
     if check_calibration_list == -1
        calibrationButton = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String', 'Calibration','Enable', 'off', 'Units', 'normalized', 'Position',[0.88,0.50,0.10,0.04], 'Callback',{@calibrationButton_Callback});
     else
        calibrationButton = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String', 'Calibration','Enable', 'on', 'Units', 'normalized', 'Position',[0.88,0.50,0.10,0.04], 'Callback',{@calibrationButton_Callback});
     end  
         gotoButton = uicontrol('Parent', handle_tab_stage,  'Enable','off', 'Style','pushbutton','String','Go to','Enable', 'off', 'Units', 'normalized', 'Position',[0.88,0.05,0.10,0.04], 'Callback',{@gotoButton_Callback});
    else
     calibrationButton = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String','Calibration','Enable', 'off', 'Units', 'normalized', 'Position',[0.88,0.50,0.10,0.04], 'Callback',{@calibrationButton_Callback});   
     gotoButton = uicontrol('Parent', handle_tab_stage,  'Enable','off', 'Style','pushbutton','String','Go to','Units', 'normalized', 'Position',[0.88,0.05,0.10,0.04], 'Callback',{@gotoButton_Callback});
    end
    set_goto = uicontrol('Parent', handle_tab_stage, 'Enable','off', 'Style','edit','String','','Units', 'normalized', 'Position',[0.77,0.05,0.10,0.04]);
    
    addStruct_label = uicontrol('Parent', handle_tab_stage, 'Style','text', 'String','Add struct to calib. list','Units', 'normalized', 'Position',[0.75,0.46,0.25,0.03]);
    addCalib_edit = uicontrol('Parent', handle_tab_stage, 'Style','edit','String','','Units', 'normalized', 'Position',[0.77,0.41,0.10,0.04]);
    addcalib_Button = uicontrol('Parent', handle_tab_stage,'Style','pushbutton','String','Add','Units', 'normalized', 'Position',[0.88,0.41,0.10,0.04], 'Callback',{@addCalibButton_Callback});
    
    calibration_table = uitable('Parent',handle_tab_stage,'Units', 'normalized','Position',[0.77, 0.1, 0.22, 0.25]);
    calibration_table.ColumnName = {'Structure','Calibrated','Change','Delete', 'X', 'Y'};
    calibration_table.ColumnEditable = [false, false, true, true, false, false];
    calibration_table.Data = generate_tabledata(calibration_list);
    calibration_table.CellEditCallback = @calibration_table_modif;
    %%%
    
    %%% Measuremetns gui
    Keithley_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String','Keithley settings','Units', 'normalized', 'Position',[0.05,0.9,0.9,0.05]);
    source_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Select source','Units', 'normalized', 'Position',[0.05,0.8,0.2,0.05]);
    source_popup = uicontrol('Parent', handle_tab_Keithley, 'Style', 'popup', 'String', {'smua','smub'},'Value',ini.sourcePopup_value, 'Units', 'normalized', 'Position',[0.25,0.81,0.18,0.05]);
    type_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Inject I or V','Units', 'normalized', 'Position',[0.50,0.8,0.2,0.05]);
    type_popup = uicontrol('Parent', handle_tab_Keithley, 'Style', 'popup', 'String', {'current','voltage'}, 'Value',ini.typePopup_value, 'Units', 'normalized', 'Position',[0.70,0.81,0.18,0.05], 'Callback', {@settype});
    steps_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Steps in sweep','Units', 'normalized', 'Position',[0.05,0.7,0.2,0.05]);
    steps_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.stepsEdit_value,'Units', 'normalized', 'Position',[0.25,0.71,0.18,0.05]);
    repeat_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Repeat sweep','Units', 'normalized', 'Position',[0.50,0.7,0.2,0.05]);
    repeat_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.repeatEdit_value, 'Units', 'normalized', 'Position',[0.70,0.71,0.18,0.05]);
    
    start_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Start value','Units', 'normalized', 'Position',[0.05,0.6,0.2,0.05]);
    start_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.startEdit_value, 'Units', 'normalized', 'Position',[0.21,0.61,0.07,0.05]);
    start_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'A','Units', 'normalized', 'Position',[0.29,0.60,0.02,0.05]);
    end_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'End value','Units', 'normalized', 'Position',[0.35,0.6,0.2,0.05]);
    end_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.endEdit_value, 'Units', 'normalized', 'Position',[0.51,0.61,0.07,0.05]);
    end_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'A','Units', 'normalized', 'Position',[0.59,0.60,0.02,0.05]);
    limit_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Limit','Units', 'normalized', 'Position',[0.65,0.6,0.2,0.05]);
    limit_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.limitEdit_value, 'Units', 'normalized', 'Position',[0.81,0.61,0.07,0.05]);
    limit_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'V','Units', 'normalized', 'Position',[0.89,0.60,0.02,0.05]);
   
    measurement_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Acquisition time','Units', 'normalized', 'Position',[0.02,0.5,0.2,0.05]);
    measurement_popup = uicontrol('Parent', handle_tab_Keithley, 'Style', 'popup', 'String', {'auto','manual'},'Value',ini.measurementPopup_value,'Units', 'normalized', 'Position',[0.22,0.51,0.10,0.05], 'Callback', {@setmeasurement});
    measurement_duration_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Delay time','Units', 'normalized', 'Position',[0.37,0.5,0.10,0.05]);
    measurement_duration_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.measurementDurationEdit_value,'Enable', 'off' ,'Units', 'normalized', 'Position',[0.47,0.51,0.1,0.05]);
    measurement_duration_units = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 's','Units', 'normalized', 'Position',[0.57,0.5,0.02,0.05]);
    measurement_nplc_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'NPLC','Units', 'normalized', 'Position',[0.65,0.5,0.07,0.05]);
    measurement_nplc_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.measurementNPLCEdit_value,'Units', 'normalized', 'Position',[0.72,0.51,0.1,0.05]);
    measurement_nplc_units = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'ms','Units', 'normalized', 'Position',[0.82,0.5,0.04,0.05]);
    
    pulsed_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Measurement mode','Units', 'normalized', 'Position',[0.02,0.40,0.2,0.05]);
    pulsed_popup = uicontrol('Parent', handle_tab_Keithley, 'Style', 'popup', 'String', {'continuous','pulsed', 'mixed'},'Value',ini.pulsedPopup_value,'Units', 'normalized', 'Position',[0.22,0.41,0.12,0.05], 'Callback', {@setpulsed});
    pulsed_duration_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Pause','Units', 'normalized', 'Position',[0.36,0.40,0.07,0.05]);
    pulsed_duration_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.pulsedDurationEdit_value,'Enable', 'off' ,'Units', 'normalized', 'Position',[0.43,0.41,0.05,0.05]);
    pulsed_units_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 's','Units', 'normalized', 'Position',[0.48,0.40,0.02,0.05]);
    mixed_limit_label =  uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Cont. limit','Units', 'normalized', 'Position',[0.50,0.40,0.12,0.05]);
    mixed_limit_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.mixedLimitEdit_value, 'Enable', 'off', 'Units', 'normalized', 'Position',[0.62,0.41,0.05,0.05]);
    mixed_limit_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'V','Units', 'normalized', 'Position',[0.68,0.40,0.02,0.05]);
    mixed_nplc_label =  uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Cont. NPLC','Units', 'normalized', 'Position',[0.75,0.40,0.12,0.05]);
    mixed_nplc_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.mixedNPLCEdit_value, 'Enable', 'off', 'Units', 'normalized', 'Position',[0.87,0.41,0.05,0.05]);
    mixed_nplc_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'ms','Units', 'normalized', 'Position',[0.92,0.40,0.04,0.05]);
    
    back_label =  uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Back voltage','Units', 'normalized', 'Position',[0.05,0.30,0.15,0.05]);
    back_checkbox = uicontrol('Parent', handle_tab_Keithley, 'Style', 'checkbox', 'Value',ini.backCheckbox_value, 'Units', 'normalized', 'Position',[0.21,0.31,0.04,0.05],'Callback',{@backVoltage_Callback});
    backStart_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Start','Units', 'normalized', 'Position',[0.25,0.3,0.07,0.05]);
    backStart_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.backStartEdit_value, 'Enable', 'off', 'Units', 'normalized', 'Position',[0.32,0.31,0.06,0.05]);
    backStart_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'V','Units', 'normalized', 'Position',[0.39,0.30,0.02,0.05]);
    backEnd_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'End','Units', 'normalized', 'Position',[0.43,0.3,0.06,0.05]);
    backEnd_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.backEndEdit_value, 'Enable', 'off', 'Units', 'normalized', 'Position',[0.49,0.31,0.06,0.05]);
    backEnd_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'V','Units', 'normalized', 'Position',[0.56,0.30,0.02,0.05]);
    backLimit_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Limit','Units', 'normalized', 'Position',[0.59,0.3,0.07,0.05]);
    backLimit_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String', ini.backLimitEdit_value, 'Enable', 'off', 'Units', 'normalized', 'Position',[0.67,0.31,0.06,0.05]);
    backLimit_units = uicontrol('Parent', handle_tab_Keithley, 'Style', 'text', 'String', 'A','Units', 'normalized', 'Position',[0.74,0.30,0.02,0.05]);
    backStep_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Steps','Units', 'normalized', 'Position',[0.78,0.3,0.07,0.05]);
    backStep_edit = uicontrol('Parent', handle_tab_Keithley, 'Style', 'edit', 'String',  ini.backStepEdit_value, 'Enable', 'off', 'Units', 'normalized', 'Position',[0.86,0.31,0.07,0.05]);
    
    highC_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'highC','Units', 'normalized', 'Position',[0.1,0.09,0.1,0.05]);
    highC_checkbox = uicontrol('Parent', handle_tab_Keithley, 'Style', 'checkbox', 'Value', ini.highCCheckbox_value, 'Units', 'normalized', 'Position',[0.21,0.10,0.04,0.05]);
    sweep_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Sweep','Units', 'normalized', 'Position',[0.1,0.05,0.1,0.05]);
    sweep_checkbox = uicontrol('Parent', handle_tab_Keithley, 'Style', 'checkbox', 'Value', ini.sweepCheckbox_value, 'Units', 'normalized', 'Position',[0.21,0.06,0.04,0.05], 'Callback',{@sweep_Callback});
    sense_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Sense','Units', 'normalized', 'Position',[0.24,0.05,0.1,0.05]);
    sense_popup = uicontrol('Parent', handle_tab_Keithley, 'Style', 'popup', 'String', {'2 wire','4 wire','2&4 wire'}, 'Value', ini.sensePopup_value, 'Units', 'normalized', 'Position',[0.34,0.06,0.15,0.05]);
    sense_drainLabel = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Use same sense for drain','Units', 'normalized', 'Position',[0.50,0.05,0.20,0.05]);
    sense_drainCheckbox = uicontrol('Parent', handle_tab_Keithley, 'Style', 'checkbox', 'Value', ini.senseDrain_value, 'Units', 'normalized', 'Position',[0.70,0.06,0.05,0.05]);
    singleCh_label = uicontrol('Parent', handle_tab_Keithley, 'Style','text', 'String', 'Single Ch','Units', 'normalized', 'Position',[0.75,0.05,0.10,0.05]);
    singleCh_checkbox = uicontrol('Parent', handle_tab_Keithley, 'Style', 'checkbox', 'Value', ini.singleChCheckbox_value, 'Units', 'normalized', 'Position',[0.85,0.06,0.04,0.05], 'Callback',{@singleCh_Callback});    
    %%%
    
    %%% Camera controls
     label_img_controls = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text','String','Image controls','Units', 'normalized', 'Position',[0.77,0.95,0.22,0.04]);
    label_img_size_label = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text','String','Image size','Units', 'normalized', 'Position',[0.77,0.90,0.1,0.04]);
    edit_img_size = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','edit','String',num2str(ini.imgSize_value),'Units', 'normalized', 'Position',[0.90,0.90,0.05,0.04]);
    label_img_offset_label = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text','String','Image offset','Units', 'normalized', 'Position',[0.77,0.85,0.1,0.04]);
    edit_img_offset = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','edit','String',num2str(ini.imgOffset_value),'Units', 'normalized', 'Position',[0.90,0.85,0.05,0.04]);
    checkbox_imgX_label = uicontrol('Parent',  handle_tab_camera, 'Enable','off', 'Style','text', 'String', 'Reverse X','Units', 'normalized', 'Position',[0.77,0.8,0.10,0.05]);
    checkbox_imgX = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style', 'checkbox','Value', ini.reverseX_value, 'Units', 'normalized', 'Position',[0.90,0.8,0.04,0.05]);
    checkbox_imgY_label = uicontrol('Parent',  handle_tab_camera, 'Enable','off', 'Style','text', 'String', 'Reverse Y','Units', 'normalized', 'Position',[0.77,0.75,0.10,0.05]);
    checkbox_imgY = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style', 'checkbox', 'Value', ini.reverseY_value, 'Units', 'normalized', 'Position',[0.90,0.75,0.04,0.05]);
    label_exptime = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text','String','Exp. time (us)','Units', 'normalized', 'Position',[0.77,0.70,0.1,0.04]);
    edit_setExpTime = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','edit','String',num2str(ini.setExpTime_value),'Units', 'normalized', 'Position',[0.90,0.70,0.05,0.04]);

    button_setcontrols = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style', 'pushbutton', 'String', 'Set img controls','Units', 'normalized', 'Position',[0.77,0.65,0.22,0.04],'Callback',{@setimg_controls_Callback});
    
    label_ExpTime_Set = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text','String','Exposure time ref','Units', 'normalized', 'Position',[0.77,0.60,0.10,0.04]);
    ExpTime_popup = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style', 'popup', 'String', {'auto','list','manual'}, 'Value', ini.expTimePopup_value, 'Units', 'normalized', 'Position',[0.89,0.60,0.10,0.04], 'Callback',{@expTime_popup_Callback});
    edit_ExpTime_list = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','edit','String',ini.expTimeListEdit_value,'Enable','off','Units', 'normalized', 'Position',[0.77,0.53,0.22,0.04]);
    button_ExpTime = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style', 'pushbutton', 'String', 'Get ExpTime list','Enable','off','Units', 'normalized', 'Position',[0.77,0.48,0.22,0.04],'Callback',{@set_expTimeList_Callback});
    
    label_repeat_img = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text','String','repeat','Units', 'normalized', 'Position',[0.77,0.42,0.10,0.04]);
    edit_repeat_img = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','edit','String',ini.repeatImgEdit_value,'Units', 'normalized', 'Position',[0.89,0.42,0.05,0.04]);

    addZoneButton = uicontrol('Parent', handle_tab_camera, 'Enable','off','Style','pushbutton','String', 'Add zone', 'Units','normalized', 'Position',[0.77,0.35,0.10,0.04], 'Callback',{@addZoneButton_Callback});
    clearZoneButton = uicontrol('Parent', handle_tab_camera, 'Enable','off','Style','pushbutton','String','Clear zones','Units', 'normalized', 'Position',[0.88,0.35,0.10,0.04], 'Enable', 'off', 'Callback',{@clearZonesButton_Callback});
    
    useFullImg_label = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style','text', 'String', 'Use full image', 'Units','normalized', 'Position',[0.77,0.30,0.16,0.05]);
    useFullImg_checkbox = uicontrol('Parent', handle_tab_camera, 'Enable','off', 'Style', 'checkbox', 'Value', ini.useFullImg_value, 'Units', 'normalized', 'Position',[0.93,0.30,0.04,0.05], 'Callback',{@useFullImage_Callback});    

    %%%% spectrometer controls
    
    spectrumAxes_handle = axes('Parent', handle_tab_spectra, 'Position', [0.10 0.12 0.6 0.8]);
    spectrumAxes_handle = updatePlotTitle(spectrumAxes_handle, 'Spectrum', 'Wavelength (nm)', 'Intensity (arb.un.)');
    
    label_spec_controls = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','Spectrometer controls','Units', 'normalized', 'Position',[0.72,0.95,0.28,0.04]);
    label_useSpec = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','use spectrometer','Units', 'normalized', 'Position',[0.71,0.90,0.16,0.04]);
    checkbox_useSpec = uicontrol('Parent', handle_tab_spectra, 'Style', 'checkbox', 'Value', false , 'Units', 'normalized', 'Position',[0.90,0.90,0.04,0.05], 'Callback',{@useSpectrometer_Callback});
    label_selectSpec = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','select spectrometer','Units', 'normalized', 'Position',[0.71,0.85,0.18,0.04]);
    selectSpec_popup = uicontrol('Parent', handle_tab_spectra, 'Style', 'popup', 'String', {''}, 'Value', 1, 'Enable', 'off' ,'Units', 'normalized', 'Position',[0.71,0.82,0.24,0.03]);
    
    label_specAver = uicontrol('Parent', handle_tab_spectra, 'Style','text','String','Averaging', 'Units', 'normalized', 'Position',[0.72,0.72,0.1,0.04]);
    edit_specAver = uicontrol('Parent', handle_tab_spectra, 'Style','edit','String',num2str(ini.setSpecAver_value),'Enable','off','Units', 'normalized', 'Position',[0.90,0.72,0.05,0.04]);
    
    label_intTime = uicontrol('Parent', handle_tab_spectra, 'Style','text','String','Integr. time (ms)', 'Units', 'normalized', 'Position',[0.72,0.67,0.1,0.04]);
    edit_intTime = uicontrol('Parent', handle_tab_spectra, 'Style','edit','String',num2str(ini.setIntTime_value),'Enable','off','Units', 'normalized', 'Position',[0.90,0.67,0.05,0.04]);
    button_getSpectrum = uicontrol('Parent', handle_tab_spectra, 'Style', 'pushbutton', 'String', 'Get single spectrum','Enable','off','Units', 'normalized', 'Position',[0.72,0.62,0.26,0.05],'Callback',{@getSpectrum_Callback});
    label_spec_preview = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','Spectrometer preview', 'Units', 'normalized', 'Position',[0.72,0.57,0.28,0.04]);
    button_startSpecPreview = uicontrol('Parent', handle_tab_spectra, 'Style', 'pushbutton', 'String', 'start','Enable','off','Units', 'normalized', 'Position',[0.72,0.52,0.10,0.05],'Callback',{@startSpecPrev_Callback});
    button_stopSpecPreview = uicontrol('Parent', handle_tab_spectra, 'Style', 'pushbutton', 'String', 'stop','Enable','off','Units', 'normalized', 'Position',[0.88,0.52,0.10,0.05],'Callback',{@stopSpecPrev_Callback});

    label_measurementIntTime = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','Integr. time for measurements', 'Units', 'normalized', 'Position',[0.72,0.45,0.28,0.04]);
    IntTime_popup = uicontrol('Parent', handle_tab_spectra, 'Style', 'popup', 'String', {'auto','list', 'manual'}, 'Value', ini.intTimePopup_value, 'Enable','off', 'Units', 'normalized', 'Position',[0.71,0.40,0.24,0.03], 'Callback',{@intTime_popup_Callback});
    edit_intTime_list = uicontrol('Parent', handle_tab_spectra, 'Style','edit','String',ini.expIntListEdit_value,'Enable','off','Units', 'normalized', 'Position',[0.72,0.30,0.26,0.05]);
    button_intTime = uicontrol('Parent', handle_tab_spectra, 'Style', 'pushbutton', 'String', 'Get IntTime list','Enable','off','Units', 'normalized', 'Position',[0.72,0.25,0.26,0.05],'Callback',{@set_intTimeList_Callback});
    
    label_spectralROI = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','Spectral range of interest', 'Units', 'normalized', 'Position',[0.72,0.20,0.28,0.04]);
    label_startSpectralROI = uicontrol('Parent', handle_tab_spectra, 'Style','text','String','start (nm)', 'Units', 'normalized', 'Position',[0.72,0.15,0.07,0.04]);
    edit_startSpectralROI = uicontrol('Parent', handle_tab_spectra, 'Style','edit','String',num2str(ini.spectralROIStart_value),'Enable','off','Units', 'normalized', 'Position',[0.78,0.15,0.07,0.04]);
    label_endSpectralROI = uicontrol('Parent', handle_tab_spectra, 'Style','text','String','end (nm)', 'Units', 'normalized', 'Position',[0.85,0.15,0.07,0.04]);
    edit_endSpectralROI = uicontrol('Parent', handle_tab_spectra, 'Style','edit','String',num2str(ini.spectralROIEnd_value),'Enable','off','Units', 'normalized', 'Position',[0.90,0.15,0.07,0.04]);
    
    label_fullROI = uicontrol('Parent',  handle_tab_spectra, 'Style','text','String','use full spectral range', 'Units', 'normalized', 'Position',[0.71,0.10,0.16,0.04]);
    checkbox_fullROI = uicontrol('Parent', handle_tab_spectra, 'Style', 'checkbox', 'Value', ini.spectralROIFull , 'Enable','off', 'Units', 'normalized', 'Position',[0.90,0.10,0.04,0.05],'Callback',{@useFullROI_Callback});
    %%% Run gui
  
    useDarkSpectrum_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'use dark spectrum','Units', 'normalized', 'Position',[0.45,0.50,0.25,0.05]);
    useDarkSpectrum_checkbox = uicontrol('Parent', handle_tab_run, 'Style', 'checkbox', 'Value', ini.darkSpectrum_value, 'Units', 'normalized', 'Position',[0.70,0.50,0.04,0.05], 'Callback',{@useDarkSpectrum_Callback});    
    
    useDarkSpectrumStep_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'at every step', 'Units', 'normalized', 'Position',[0.75,0.50,0.12,0.05]);
    useDarkSpectrumStep_checkbox = uicontrol('Parent', handle_tab_run, 'Style', 'checkbox', 'Value', ini.darkSpectrumStep_value, 'Units', 'normalized', 'Position',[0.87,0.50,0.04,0.05]);    
    
    ignoreZero_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Ignore dark IVL image','Units', 'normalized', 'Position',[0.45,0.45,0.25,0.05]);
    ignoreZero_checkbox = uicontrol('Parent', handle_tab_run, 'Style', 'checkbox', 'Value', ini.ignoreZero_value, 'Units', 'normalized', 'Position',[0.70,0.45,0.04,0.05]);    
    
    saveFig_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Save last image from sweep as *.jpg','Units', 'normalized', 'Position',[0.05,0.45,0.35,0.05]);
    saveFig_checkbox = uicontrol('Parent', handle_tab_run, 'Style', 'checkbox', 'Value', ini.saveFigCheckbox_value, 'Units', 'normalized', 'Position',[0.40,0.45,0.04,0.05]);    
    
    saveFull_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Save full data to *.mat','Units', 'normalized', 'Position',[0.05,0.40,0.25,0.05]);
    saveFull_checkbox = uicontrol('Parent',handle_tab_run, 'Style', 'checkbox', 'Value', ini.saveFullCheckbox_value, 'Units', 'normalized', 'Position',[0.28,0.40,0.04,0.05]);    
    
    usepostProc_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Use IV post processing','Units', 'normalized', 'Position',[0.32,0.40,0.25,0.05]);
    usePostProc_checkbox = uicontrol('Parent',handle_tab_run, 'Style', 'checkbox', 'Value', ini.usePostProcCheckbox_value, 'Units', 'normalized', 'Position',[0.55,0.40,0.04,0.05], 'Callback',{@usePostProc_Callback});    
    
    [~,postProc_name]= fileparts(ini.load_postProc);
    postProc_edit = uicontrol('Parent', handle_tab_run, 'Style','edit','String',postProc_name,'Units', 'normalized', 'Position',[0.60,0.405,0.15,0.04]);
    postProc_Button = uicontrol('Parent', handle_tab_run,'Style','pushbutton','String','load','Units', 'normalized', 'Position',[0.75,0.40,0.10,0.04], 'Callback',{@postProc_Button_Callback});
    
    useInProc_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Use IV in processing','Units', 'normalized', 'Position',[0.32,0.35,0.25,0.05]);
    useInProc_checkbox = uicontrol('Parent',handle_tab_run, 'Style', 'checkbox', 'Value', ini.useInProcCheckbox_value, 'Units', 'normalized', 'Position',[0.55,0.35,0.04,0.05], 'Callback',{@useInProc_Callback});    
    
    [~,inProc_name]= fileparts(ini.load_inProc);
    inProc_edit = uicontrol('Parent', handle_tab_run, 'Style','edit','String',inProc_name,'Units', 'normalized', 'Position',[0.60,0.355,0.15,0.04]);
    inProc_Button = uicontrol('Parent', handle_tab_run,'Style','pushbutton','String','load','Units', 'normalized', 'Position',[0.75,0.35,0.10,0.04], 'Callback',{@inProc_Button_Callback});
    
    
    label_Comment = uicontrol('Parent', handle_tab_run, 'Style','text','String','Comment','Units', 'normalized', 'Position',[0.05,0.29,0.2,0.05]);
    edit_Comment = uicontrol('Parent', handle_tab_run, 'Style','edit','String',ini.commentEdit_value,'Units', 'normalized', 'Position',[0.21,0.29,0.65,0.05]);
    
    open_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Open list','Units', 'normalized', 'Position',[0.05,0.2,0.2,0.05]);
    open_edit = uicontrol('Parent', handle_tab_run, 'Style', 'edit', 'String', ini.openEdit_value, 'Units', 'normalized', 'Position',[0.21,0.21,0.5,0.05]);
    open_button = uicontrol('Parent', handle_tab_run, 'Style', 'pushbutton', 'String', 'Open','Units', 'normalized', 'Position',[0.75,0.21,0.10,0.05],'Callback',{@openListButton_Callback});
    open_dir_button = uicontrol('Parent', handle_tab_run, 'Style', 'pushbutton', 'String', 'Open dir','Units', 'normalized', 'Position',[0.75,0.14,0.10,0.05],'Callback',{@addressButtonDir_Callback});
    path_label = uicontrol('Parent', handle_tab_run, 'Style','text', 'String', 'Path to save','Units', 'normalized', 'Position',[0.05,0.13,0.2,0.05]);
    path_edit = uicontrol('Parent', handle_tab_run, 'Style', 'edit', 'String', ini.pathEdit_value, 'Units', 'normalized', 'Position',[0.21,0.14,0.5,0.05]); 
        
    label_useIVL = uicontrol('Parent', handle_tab_run, 'Style','text','String','Use IVL','Units', 'normalized', 'Position',[0.02,0.95,0.35,0.05]);
    label_useSpectra = uicontrol('Parent', handle_tab_run, 'Style','text','String','Use spectral measurements','Units', 'normalized', 'Position',[0.52,0.95,0.35,0.05]);
    useIVL_checkbox = uicontrol('Parent',handle_tab_run, 'Style', 'checkbox', 'Value', ini.useIVLCheckbox_value, 'Units', 'normalized', 'Position',[0.37,0.95,0.04,0.05],  'Callback',{@useIVL_Callback});    
    useSpectra_checkbox = uicontrol('Parent',handle_tab_run, 'Style', 'checkbox', 'Value', ini.useSpectraCheckbox_value, 'Enable','off', 'Units', 'normalized', 'Position',[0.87,0.95,0.04,0.05],  'Callback',{@useSpectra_Callback});    
    clearIVL_button = uicontrol('Parent',handle_tab_run, 'Style', 'pushbutton', 'String', 'clear IVL', 'Units', 'normalized', 'Position',[0.02,0.90,0.20,0.05], 'Callback',{@clearStep_Callback});    
    clearSpectra_button = uicontrol('Parent',handle_tab_run, 'Style', 'pushbutton', 'String', 'clear Spectra', 'Enable','off', 'Units', 'normalized', 'Position',[0.52,0.90,0.20,0.05], 'Callback',{@clearStep_Callback});    
    useFullIVL_button = uicontrol('Parent',handle_tab_run, 'Style', 'pushbutton', 'String', 'Full IVL', 'Units', 'normalized', 'Position',[0.27,0.90,0.20,0.05], 'Callback',{@useFullStep_Callback});    
    useFullSpectra_button = uicontrol('Parent',handle_tab_run, 'Style', 'pushbutton', 'String', 'Full spectra', 'Enable','off', 'Units', 'normalized', 'Position',[0.77,0.90,0.20,0.05], 'Callback',{@useFullStep_Callback});    
    addValueIVL_edit = uicontrol('Parent', handle_tab_run, 'Style', 'edit', 'String', '', 'Units', 'normalized', 'Position',[0.02,0.85,0.15,0.05]);
    addValueSpectra_edit = uicontrol('Parent', handle_tab_run, 'Style', 'edit', 'String', '', 'Enable','off', 'Units', 'normalized', 'Position',[0.52,0.85,0.15,0.05]);
    addValueIVL_units = uicontrol('Parent', handle_tab_run, 'Style', 'popup', 'String', {'A','V'}, 'Value', ini.unitsIVL_value, 'Units', 'normalized', 'Position',[0.17,0.85,0.08,0.05]);
    addValueSpectra_units = uicontrol('Parent', handle_tab_run, 'Style', 'popup', 'String', {'A','V'}, 'Value', ini.unitsSpectra_value, 'Units', 'normalized', 'Position',[0.67,0.85,0.08,0.05]);
    addValueIVL_button = uicontrol('Parent', handle_tab_run, 'Style', 'pushbutton', 'String', 'Add','Units', 'normalized', 'Position',[0.32,0.85,0.15,0.05], 'Callback',{@addValuebutton_Callback});
    addValueSpectra_button = uicontrol('Parent', handle_tab_run, 'Style', 'pushbutton', 'String', 'Add','Enable','off', 'Units', 'normalized', 'Position',[0.82,0.85,0.15,0.05], 'Callback',{@addValuebutton_Callback});
    
    IVL_table = uitable('Parent',handle_tab_run,'Units', 'normalized','Position',[0.02, 0.60, 0.45, 0.2]);
    IVL_table.ColumnName = {'Point','Delete', 'ExpTime, us'};
    IVL_table.ColumnEditable = [false, true, false];
    IVL_table.Data = ini.IVL_list;
    IVL_table.CellEditCallback = @step_table_modif;
    
    Spectra_table = uitable('Parent',handle_tab_run, 'Enable', 'off', 'Units', 'normalized','Position',[0.52, 0.60, 0.45, 0.20]);
    Spectra_table.ColumnName = {'Point','Delete', 'IntegrTime, ms'};
    Spectra_table.ColumnEditable = [false, true, false];
    Spectra_table.Data = ini.Spectra_list;
    Spectra_table.CellEditCallback = @step_table_modif;
    
    run_button = uicontrol('Parent', handle_tab_run, 'Style', 'pushbutton', 'String', 'Run','Units', 'normalized', 'Position',[0.05,0.05,0.10,0.05],'Callback',{@runButton_Callback});
    stop_button = uicontrol('Parent', handle_tab_run, 'Style', 'pushbutton', 'String', 'Stop','Enable', 'off', 'Units', 'normalized', 'Position',[0.20,0.05,0.10,0.05],'Callback',{@stopButton_Callback});
    label_useAutoSave = uicontrol('Parent', handle_tab_run, 'Style','text','String','Auto save','Units', 'normalized', 'Position',[0.34,0.05,0.1,0.05]);
    useAutoSave_checkbox = uicontrol('Parent',handle_tab_run, 'Style', 'checkbox', 'Value', ini.useAutoSave_value, 'Units', 'normalized', 'Position',[0.45,0.05,0.03,0.05],  'Callback',{@useAutoSave_Callback});    
    autoSave_edit = uicontrol('Parent', handle_tab_run, 'Style', 'edit', 'String', num2str(ini.autoSave_value), 'Units', 'normalized', 'Position',[0.50,0.05,0.06,0.05]);
    autoSave_units = uicontrol('Parent', handle_tab_run, 'Style', 'text', 'String', 'min', 'Units', 'normalized', 'Position',[0.57,0.05,0.04,0.05]);
    %%%
    
    %%% DLT gui

    label_useDLT = uicontrol('Parent', handle_tab_DLT, 'Style','text','String','Use DLT measurements','Units', 'normalized', 'Position',[0.05,0.95,0.25,0.05]);
    useDLT_checkbox = uicontrol('Parent',handle_tab_DLT, 'Style', 'checkbox', 'Value', ini.useDLTCheckbox_value, 'Enable','off', 'Units', 'normalized', 'Position',[0.3,0.95,0.04,0.05],  'Callback',{@useDLT_Callback});    
    clearDLT_button = uicontrol('Parent',handle_tab_DLT, 'Style', 'pushbutton', 'String', 'clear DLT', 'Enable','off', 'Units', 'normalized', 'Position',[0.1,0.90,0.20,0.05], 'Callback',{@clearStep_Callback});    
    useFullDLT_button = uicontrol('Parent',handle_tab_DLT, 'Style', 'pushbutton', 'String', 'Full DLT', 'Enable','off', 'Units', 'normalized', 'Position',[0.3,0.90,0.20,0.05], 'Callback',{@useFullStep_Callback});    
    addValueDLT_edit = uicontrol('Parent', handle_tab_DLT, 'Style', 'edit', 'String', '', 'Enable','off', 'Units', 'normalized', 'Position',[0.05,0.85,0.15,0.05]);
    addValueDLT_units = uicontrol('Parent', handle_tab_DLT, 'Style', 'popup', 'String', {'A','V'}, 'Value', ini.unitsDLT_value, 'Enable','off', 'Units', 'normalized', 'Position',[0.25,0.85,0.08,0.05], 'Callback',{@setDLTunits_Callback});
    addValueDLT_button = uicontrol('Parent', handle_tab_DLT, 'Style', 'pushbutton', 'String', 'Add','Enable','off', 'Units', 'normalized', 'Position',[0.35,0.85,0.15,0.05], 'Callback',{@addValuebutton_Callback});

    DLT_table = uitable('Parent',handle_tab_DLT, 'Enable', 'off', 'Units', 'normalized','Position',[0.05, 0.40, 0.80, 0.40]);
    DLT_table.ColumnName = {'Point','Delete', 'IntegrTime, ms'};
    DLT_table.ColumnEditable = [false, true, false];
    DLT_table.Data = ini.DLT_list;
    DLT_table.CellEditCallback = @step_table_modif;
    
    label_DLTref = uicontrol('Parent', handle_tab_DLT, 'Style','text','String','DLT reference value','Enable','off','Units', 'normalized', 'Position',[0.05,0.30,0.25,0.05]);
    DLTref_edit = uicontrol('Parent', handle_tab_DLT, 'Style', 'edit', 'String', num2str(ini.DLTref_value), 'Enable','off', 'Units', 'normalized', 'Position',[0.28,0.30,0.05,0.05]);
    DLTref_units = uicontrol('Parent', handle_tab_DLT, 'Style', 'text', 'String', '', 'Enable','off', 'Units', 'normalized', 'Position',[0.33,0.30,0.05,0.05]);
    label_DLTref_time = uicontrol('Parent', handle_tab_DLT, 'Style','text','String','DLT reference integration time','Enable','off','Units', 'normalized', 'Position',[0.4,0.30,0.25,0.05]);
    DLTref_edit_time = uicontrol('Parent', handle_tab_DLT, 'Style', 'edit', 'String', ini.DLTrefTime_value, 'Enable','off', 'Units', 'normalized', 'Position',[0.68,0.30,0.05,0.05]);
    label_DLTstabilization = uicontrol('Parent', handle_tab_DLT, 'Style','text','String','DLT stabilization time','Enable','off','Units', 'normalized', 'Position',[0.05,0.25,0.25,0.05]);
    DLTstabilization_edit = uicontrol('Parent', handle_tab_DLT, 'Style', 'edit', 'String', num2str(ini.DLTstabilization_value), 'Enable','off', 'Units', 'normalized', 'Position',[0.28,0.25,0.05,0.05]);
    DLTstabilization_units = uicontrol('Parent', handle_tab_DLT, 'Style', 'text', 'String', 'min', 'Enable','off', 'Units', 'normalized', 'Position',[0.33,0.25,0.05,0.05]);
    
    label_DLTrepeat = uicontrol('Parent', handle_tab_DLT, 'Style','text','String','DLT repetition','Enable','off','Units', 'normalized', 'Position',[0.05,0.20,0.25,0.05]);
    DLTrepeat_edit = uicontrol('Parent', handle_tab_DLT, 'Style', 'edit', 'String', num2str(ini.DLTrepeat_value), 'Enable','off', 'Units', 'normalized', 'Position',[0.28,0.20,0.05,0.05]);
    
    %%%
    
    
    %%% Result gui

     result_handles.resultBL_handle = subplot(2,2,3, 'Parent', handle_tab_result);
     result_handles.resultTR_handle = subplot(2,2,2, 'Parent', handle_tab_result);
     result_handles.resultBR_handle = subplot(2,2,4, 'Parent', handle_tab_result);
    %%%

    %%%%%%% Init interfaces
    settype(type_popup,NaN);
    setmeasurement(measurement_popup,NaN);
    setpulsed(pulsed_popup,NaN);
    backVoltage_Callback(back_checkbox,NaN);
    sweep_Callback(sweep_checkbox,NaN);
    singleCh_Callback(singleCh_checkbox,NaN);
    expTime_popup_Callback(ExpTime_popup,NaN);   
    useFullImage_Callback(useFullImg_checkbox,NaN);
    useIVL_Callback(useIVL_checkbox,NaN);
    useSpectra_Callback(useSpectra_checkbox, NaN);
    useDLT_Callback(useDLT_checkbox, NaN);
    usePostProc_Callback(usePostProc_checkbox,NaN);
    useInProc_Callback(useInProc_checkbox,NaN);
%    useFullROI_Callback(checkbox_fullROI, NaN);
    useDarkSpectrum_Callback(useDarkSpectrum_checkbox, NaN);
    setDLTunits_Callback(addValueDLT_units, NaN)
    useSaveFull_Callback(saveFull_checkbox,NaN);
    result_handles.resultBL_handle = updatePlotTitle(result_handles.resultBL_handle, 'I-V', 'Voltage (V)', 'Current (A)');
    result_handles.resultTR_handle = updatePlotTitle(result_handles.resultTR_handle, 'I-V', 'Voltage (V)', 'Current (A)');
    result_handles.resultBR_handle = updatePlotTitle(result_handles.resultBR_handle, 'I-V', 'Voltage (V)', 'Current (A)');
    %%%
    
    function setDLTunits_Callback(source, event)
      if get(addValueDLT_units, 'Value') == 1
        set(DLTref_units,'String','A');
      else    
        set(DLTref_units,'String','V');
      end      
    end    
    
    
    function useSpectra_Callback(source, event)
      if get(useSpectra_checkbox,'Value') && get(checkbox_useSpec,'Value')  
       set(clearSpectra_button, 'Enable', 'on');
       set(useFullSpectra_button, 'Enable', 'on');
       set(addValueSpectra_edit, 'Enable', 'on');
       set(addValueSpectra_units, 'Enable', 'on');
       set(addValueSpectra_button, 'Enable', 'on');
       set(Spectra_table, 'Enable', 'on');
       set(useDarkSpectrum_checkbox, 'Enable', 'on');
       set(useDarkSpectrum_label, 'Enable', 'on');
       useDarkSpectrum_Callback(useDarkSpectrum_checkbox, event);
      else
       set(clearSpectra_button, 'Enable', 'off');
       set(useFullSpectra_button, 'Enable', 'off');
       set(addValueSpectra_edit, 'Enable', 'off');
       set(addValueSpectra_units, 'Enable', 'off');
       set(addValueSpectra_button, 'Enable', 'off');
       set(Spectra_table, 'Enable', 'off');
       set(useDarkSpectrumStep_label, 'Enable', 'off');
       set(useDarkSpectrumStep_checkbox, 'Enable', 'off');
       set(useDarkSpectrum_checkbox, 'Enable', 'off');
       set(useDarkSpectrum_label, 'Enable', 'off');
      end  
    end    
    
    function useDLT_Callback(source, event)
      if get(useDLT_checkbox,'Value') && get(checkbox_useSpec,'Value')  
       set(clearDLT_button, 'Enable', 'on');
       set(useFullDLT_button, 'Enable', 'on');
       set(addValueDLT_edit, 'Enable', 'on');
       set(addValueDLT_units, 'Enable', 'on');
       set(addValueDLT_button, 'Enable', 'on');
       set(DLT_table, 'Enable', 'on');
       set(label_DLTref, 'Enable', 'on');
       set(DLTref_edit, 'Enable', 'on');
       set(DLTref_units, 'Enable', 'on');
       set(label_DLTstabilization, 'Enable', 'on');
       set(DLTstabilization_edit, 'Enable', 'on');
       set(DLTstabilization_units, 'Enable', 'on');
       set(label_DLTrepeat, 'Enable', 'on');
       set(DLTrepeat_edit, 'Enable', 'on');
       set(label_DLTref_time, 'Enable', 'on');
       set(DLTref_edit_time, 'Enable', 'on');
      else
       set(clearDLT_button, 'Enable', 'off');
       set(useFullDLT_button, 'Enable', 'off');
       set(addValueDLT_edit, 'Enable', 'off');
       set(addValueDLT_units, 'Enable', 'off');
       set(addValueDLT_button, 'Enable', 'off');
       set(DLT_table, 'Enable', 'off');
       set(label_DLTref, 'Enable', 'off');
       set(DLTref_edit, 'Enable', 'off');
       set(DLTref_units, 'Enable', 'off');
       set(label_DLTstabilization, 'Enable', 'off');
       set(DLTstabilization_edit, 'Enable', 'off');
       set(DLTstabilization_units, 'Enable', 'off');
       set(label_DLTrepeat, 'Enable', 'off');
       set(DLTrepeat_edit, 'Enable', 'off');
       set(label_DLTref_time, 'Enable', 'off');
       set(DLTref_edit_time, 'Enable', 'off');
      end  
    end

    function useAutoSave_Callback(source, event)
      if get(useAutoSave_checkbox, 'Value') && get(saveFull_checkbox, 'Value')
         set(autoSave_edit, 'Enable', 'on');
         set(autoSave_units, 'Enable', 'on');
      else   
         set(autoSave_edit, 'Enable', 'off');
         set(autoSave_units, 'Enable', 'off'); 
      end
    end

    function useSaveFull_Callback(source, event)
      if get(saveFull_checkbox, 'Value')
         set(label_useAutoSave, 'Enable', 'on');
         set(useAutoSave_checkbox, 'Enable', 'on');
         useAutoSave_Callback(useAutoSave_checkbox, NaN)
      else   
         set(label_useAutoSave, 'Enable', 'off');
         set(useAutoSave_checkbox, 'Enable', 'off');
         useAutoSave_Callback(useAutoSave_checkbox, NaN)
      end
    end  

    function useFullROI_Callback(source, event)
      if ~get(checkbox_fullROI,'Value') && get(checkbox_useSpec,'Value')  
       set(label_startSpectralROI, 'Enable', 'on');
       set(edit_startSpectralROI, 'Enable', 'on');
       set(label_endSpectralROI, 'Enable', 'on');
       set(edit_endSpectralROI, 'Enable', 'on');
      else
       set(label_startSpectralROI, 'Enable', 'off');
       set(edit_startSpectralROI, 'Enable', 'off');
       set(label_endSpectralROI, 'Enable', 'off');
       set(edit_endSpectralROI, 'Enable', 'off');  
      end  
    end       

    function useDarkSpectrum_Callback(source, event)
      if get(useDarkSpectrum_checkbox,'Value') && get(checkbox_useSpec,'Value') && get(useSpectra_checkbox,'Value')  
       set(useDarkSpectrumStep_label, 'Enable', 'on');
       set(useDarkSpectrumStep_checkbox, 'Enable', 'on');
      else
       set(useDarkSpectrumStep_label, 'Enable', 'off');
       set(useDarkSpectrumStep_checkbox, 'Enable', 'off');  
      end  
    end  


    function closeAllSpectrometers
       deviceNo = size(specDevices_list, 2);
       if deviceNo > 0
         for cnt = 1:deviceNo
            if ~isempty(specDevices_list(cnt).handler.hdl)
               specDevices_list(cnt).handler.close;
            end 
         end    
       end    
       specDevices_list = []; 
    end    


    function useSpectrometer_Callback(source,event)
       if get(checkbox_useSpec,'Value')     
        if  isempty(specDevices_list)
          spectraldevice = Thorlabs_CCS175;
          if spectraldevice.init == 0
              newDeviceNo = size(specDevices_list,2) +1 ;
              specDevices_list(newDeviceNo).handler = spectraldevice;
              specDevices_list(newDeviceNo).type = 1;
              specDevices_list(newDeviceNo).deviceID = 0;
              deviceList(newDeviceNo) = cellstr('Thorlabs CCS175');
          else
              spectraldevice.close
          end
          spectraldevice = [];
          spectraldevice = OceanOptics;
%           deviceNo = spectraldevice.init;
          deviceNo = 0; %to be able to use OceanOptics spectrometer its driver should be installed
          if deviceNo > 0       
            newDeviceNo = size(specDevices_list,2);  
            for cnt=1:deviceNo
              specDevices_list(newDeviceNo+cnt).handler = spectraldevice;  
              specDevices_list(newDeviceNo+cnt).type = 0;
              specDevices_list(newDeviceNo+cnt).deviceID = cnt-1;  
	          deviceList(newDeviceNo+cnt) = convertCharsToStrings(char(specDevices_list(newDeviceNo+cnt).handler.getDeviceName(cnt-1)));
            end        
          else
           spectraldevice.close   
          end
       else
         for cnt=1:size(specDevices_list,2)
             if specDevices_list(cnt).type == 0
                 deviceList(cnt) = convertCharsToStrings(char(specDevices_list(cnt).handler.getDeviceName(cnt-1)));
             else
                 deviceList(cnt) = cellstr('Thorlabs CCS175');
             end    
         end 
				  
				 
			  
			   
       end   
          if size(specDevices_list,2) == 0
								  
		  
																
						   
													
					   
          	     waitfor(msgbox('No spectrometers found'));
        	     set(checkbox_useSpec,'Value', 0)
		         return;
          else
              set(selectSpec_popup,'String', deviceList, 'Value', 1);
              set(useSpectra_checkbox, 'Enable', 'on');
              set(selectSpec_popup, 'Enable', 'on');
	          set(edit_specAver, 'Enable', 'on');
	          set(edit_intTime, 'Enable', 'on');
	          set(button_getSpectrum, 'Enable', 'on');
	          set(button_startSpecPreview, 'Enable', 'on');
	          set(IntTime_popup, 'Enable', 'on');
              set(label_selectSpec, 'Enable', 'on');
              set(label_specAver, 'Enable', 'on');
              set(label_intTime, 'Enable', 'on');
              set(label_spec_preview, 'Enable', 'on');
              set(label_measurementIntTime, 'Enable', 'on');
              set(label_spectralROI, 'Enable', 'on');
              set(label_fullROI, 'Enable', 'on');
              set(checkbox_fullROI, 'Enable', 'on');
              set(useDLT_checkbox, 'Enable', 'on');
              useFullROI_Callback(checkbox_fullROI, event);
              useSpectra_Callback(source,event);
              useDLT_Callback(source,event);
	          intTime_popup_Callback(IntTime_popup,event);
          end 
       else	   
       set(selectSpec_popup, 'Enable', 'off', 'String', {''}, 'Value', 1);
	   set(edit_specAver, 'Enable', 'off');
	   set(edit_intTime, 'Enable', 'off');
	   set(button_getSpectrum, 'Enable', 'off');
	   set(button_startSpecPreview, 'Enable', 'off');
	   set(button_stopSpecPreview, 'Enable', 'off');
	   set(IntTime_popup, 'Enable', 'off');
       set(edit_intTime_list, 'Enable', 'off');	 
	   set(button_intTime, 'Enable', 'off');
       set(useSpectra_checkbox, 'Enable', 'off');
       set(useDLT_checkbox, 'Enable', 'off');
       set(label_spectralROI, 'Enable', 'off');
       set(label_startSpectralROI, 'Enable', 'off');
       set(edit_startSpectralROI, 'Enable', 'off');
       set(label_endSpectralROI, 'Enable', 'off');
       set(edit_endSpectralROI, 'Enable', 'off');
       set(label_fullROI, 'Enable', 'off');
       set(checkbox_fullROI, 'Enable', 'off');
       set(label_selectSpec, 'Enable', 'off');
       set(label_specAver, 'Enable', 'off');
       set(label_intTime, 'Enable', 'off');
       set(label_spec_preview, 'Enable', 'off');
       set(label_measurementIntTime, 'Enable', 'off');
       useFullROI_Callback(checkbox_fullROI, NaN);
       useSpectra_Callback(source,event);
       useDLT_Callback(source,event);
	   closeAllSpectrometers;
     end
    end    
    
	function intTime_popup_Callback(source,event)
	 val = source.Value;
     mode = source.String;
     if strcmp(mode(val), 'auto') || strcmp(mode(val), 'manual')
       set(edit_intTime_list,'Enable', 'off');  
       set(button_intTime,'Enable', 'off');  
     else  
       set(edit_intTime_list,'Enable', 'on');  
       set(button_intTime,'Enable', 'on');    
     end  
	 if (strcmp(mode(val), 'manual'))
       Spectra_table.ColumnEditable = [false, true, true];  
     else
       Spectra_table.ColumnEditable = [false, true, false];
     end
    end
  
    function [intTime, Aver, status] = checkSpecValues
        status = 0;
        intTime = str2num(get(edit_intTime,'String'));
        Aver = str2num(get(edit_specAver,'String'));
        if isempty(intTime)
           waitfor(msgbox('Can not convert integration time to a number'));
           status=1;
           return;
        end
        if (rem(intTime,1) ~= 0) || (intTime <= 0)
          waitfor(msgbox('Integration time should be a positive integer number'));
          status=1;
          return;
        end
        if isempty(Aver)
           waitfor(msgbox('Can not convert spectrometer averaging to a number'));
           status=2;
           return;
        end
        if (rem(Aver,1) ~= 0) || (Aver <= 0)
          waitfor(msgbox('Spectrometer averaging should be a positive integer number'));
          status=2;
          return;
        end
    end
    
    function [wvl, spectrum] = getSingleSpectrum(intTime,Averaging, device)
        if device.type == 0
              device.handler.setIntegrationTime(device.deviceID, intTime*1000); %1000 = 1ms
              device.handler.setScansToAverage(device.deviceID,Averaging);
              [wvl, spectrum] = device.handler.getSpectrum(device.deviceID);
        elseif device.type == 1
              device.handler.setIntegrationTime(intTime/1000);
              device.handler.scan;
              [wvl, spectrum] = device.handler.getSpectrum;
              wvl = wvl.';
              spectrum = spectrum.';
              if Averaging > 1
                for specRepeat = 2:Averaging
                    device.handler.scan;
                    [~, tmp_spectrum] = device.handler.getSpectrum;
                    spectrum = spectrum + tmp_spectrum.';
                end
                spectrum = spectrum./Averaging;
              end  
        end   				 
    end    

    function startSpecPrev_Callback(source,event)
     specPreviewRunnig = 1;   
     set(button_getSpectrum, 'Enable', 'off');
     set(button_startSpecPreview, 'Enable', 'off');
     set(button_stopSpecPreview, 'Enable', 'on');
     set(edit_specAver, 'Enable', 'off');
	 set(edit_intTime, 'Enable', 'off');
     device = specDevices_list(get(selectSpec_popup,'Value'));
     [intTime,Averaging,response] = checkSpecValues;
     if ~response  
        while specPreviewRunnig 
          [wvl,spectrum] = getSingleSpectrum(intTime,Averaging,device);
          spectrumAxes_handle = updatePlotTitle(spectrumAxes_handle, 'Spectrum', 'Wavelength (nm)', 'Intensity (arb.un.)');
          spectrumAxes_handle = plotAddNewCurve(spectrumAxes_handle, wvl, spectrum,'-^');
          pause(intTime/1000);
        end
     end      
     end

    function stopSpecPrev_Callback(source,event)
     specPreviewRunnig = 0; 
     set(button_getSpectrum, 'Enable', 'on');
     set(button_startSpecPreview, 'Enable', 'on');
     set(edit_specAver, 'Enable', 'on');
	 set(edit_intTime, 'Enable', 'on');
     set(button_stopSpecPreview, 'Enable', 'off');  
    end

    function getSpectrum_Callback(source,event)
       set(button_getSpectrum, 'Enable', 'off');
       set(button_startSpecPreview, 'Enable', 'off');
       set(edit_specAver, 'Enable', 'off');
	   set(edit_intTime, 'Enable', 'off');
      [intTime,Averaging,response] = checkSpecValues;
      if ~response
        device = specDevices_list(get(selectSpec_popup,'Value'));   
        [wvl,spectrum] = getSingleSpectrum(intTime,Averaging,device);
        spectrumAxes_handle = updatePlotTitle(spectrumAxes_handle, 'Spectrum', 'Wavelength (nm)', 'Intensity (arb.un.)');
        spectrumAxes_handle = plotAddNewCurve(spectrumAxes_handle, wvl, spectrum,'-^');
      end      
      set(button_getSpectrum, 'Enable', 'on');
      set(button_startSpecPreview, 'Enable', 'on');
      set(edit_specAver, 'Enable', 'on');
	  set(edit_intTime, 'Enable', 'on');
    end

    function updatefields(resp)
     %%%%%% X motor values
     if resp(motorXind,currentPositionInd) ~= resp(motorXind,targetPositionInd)
        set(X_currentPos,'String','update');
     else   
        set(X_currentPos,'String',num2str(resp(motorXind,currentPositionInd)));
     end
     if abs(resp(motorXind,targetPositionInd)) ~= keyMove
        set(X_setPos,'String',num2str(resp(motorXind,targetPositionInd)));
     else   
        set(X_setPos,'String','manual');
     end   
     
     %%%%%% Y motor values
     if resp(motorYind,currentPositionInd) ~= resp(motorYind,targetPositionInd)
        set(Y_currentPos,'String','update');
     else   
        set(Y_currentPos,'String',num2str(resp(motorYind,currentPositionInd)));
     end
     if abs(resp(motorYind,targetPositionInd)) ~= keyMove
        set(Y_setPos,'String',num2str(resp(motorYind,targetPositionInd)));
     else   
        set(Y_setPos,'String','manual');
     end 
     
     %%%%%% z motor values
     if resp(motorZind,currentPositionInd) ~= resp(motorZind,targetPositionInd)
        set(Z_currentPos,'String','update');
     else   
        set(Z_currentPos,'String',num2str(resp(motorZind,currentPositionInd)));
     end
     if abs(resp(motorZind,targetPositionInd)) ~= keyMove
        set(Z_setPos,'String',num2str(resp(motorZind,targetPositionInd)));
     else   
        set(Z_setPos,'String','manual');
     end 
    end
     
   function addMarkerButton_Callback(source,eventdata) 
    [x,y] = ginput(1);
    viscircles([x,y],2,'Color','w');
   end
    
   function clearMarkerButton_Callback(source,eventdata) 
    delete(findobj(axes_handle, 'type','Line'));
    delete(findobj(axes_handle, 'type','Group'));
   end
  
   function newCalibrationButton_Callback(source,eventdata)
     calibration_list = {};
     calibration_table.Data = {};
     set(calibrationButton, 'Enable', 'off');
     set(gotoButton, 'Enable', 'off');
   end
   
   
   function calibrationButton_Callback(source,eventdata)
%    set(calibrationButton, 'Enable', 'off');
%    resp = getresponse(port);
%    check_calibration_list = check_calibration(calibration_list);
%    calibration_list{check_calibration_list,4} = resp(motorXind,currentPositionInd);
%    calibration_list{check_calibration_list,5} = resp(motorYind,currentPositionInd);
%    check_calibration_list = check_calibration(calibration_list);
%   if not(check_calibration_list)
%      [coef_X, coef_Y] = getTransformation(calibration_list);
%      set(gotoButton, 'Enable', 'on');
%    else
%      set(calibrationButton, 'Enable', 'on');  
%    end
%    calibration_table.Data = generate_tabledata(calibration_list);
   end

   
   function moveToStruct(varargin)
%     positionInMapName = varargin{1};  
%     if nargin == 1  
%      deltaX = 0;
%      deltaY = 0;
%     else
%      deltaX = varargin{2};
%      deltaY = varargin{3};
%     end 
%     moveToX=round(coef_X(1) + (map_coord(positionInMapName,:)+[deltaX,deltaY])*coef_X(2:3));
%     fprintf(port,'zl');
%     while (1)
%       fprintf(port,sprintf('m%dn%dS500\n',motorXind,moveToX));
%       while (port.BytesAvailable == 0)
%           pause (delaytime/10);
%       end    
%       if str2num(fgetl(port)) == moveToX
%           break;
%       end   
%     end  
%     set(X_setPos,'String',num2str(moveToX));
%     set(X_currentPos,'String','update');
%     moveToY = round(coef_Y(1) + (map_coord(positionInMapName,:)+[deltaX,deltaY])*coef_Y(2:3));
%     while (1)
%        fprintf(port,sprintf('m%dn%ds\n',motorYind,moveToY));
%        while (port.BytesAvailable == 0)
%           pause (delaytime/10);
%        end    
%        if str2num(fgetl(port)) == moveToY
%           break;
%        end   
%     end  
%     set(Y_setPos,'String',num2str(moveToY));
%     set(Y_currentPos,'String','update');  
%     fprintf(port,'z');
%     if nargin == 4
%       if varargin{4} == 1  
%         return
%       end 
%     end
%     while (port.BytesAvailable == 0)
%           pause(delaytime/4);
%     end
%     portout = fgetl(port);
%     if strcmp(portout(1:4),'done')
%       resp = getresponse(port); 
%       updatefields(resp)
%     else
%         disp(sprintf('Erorr: not expected response form Arduino %s',portout));
%     end   
   end    
   
   
   function gotoButton_Callback (source,eventdata)
    [foundX, ~] = find(strcmp(map_name,get(set_goto, 'String'))); 
    if foundX~=0
       moveToStruct(foundX)
    else
      msgbox(sprintf('Structure %s was not found in the name map',get(set_goto, 'String')));
    end
   end
   
   function addValuebutton_Callback (source,eventdata) 
     if source == addValueIVL_button
        edit_obj = addValueIVL_edit; 
        popup_obj = ExpTime_popup;
        list = ini.IVL_list;
        setTimeFromList = @setExpTimeFromList;
        time = cam_struct.expTime;
     end   
     if source == addValueSpectra_button
        edit_obj = addValueSpectra_edit; 
        popup_obj = IntTime_popup;
        list = ini.Spectra_list;
        setTimeFromList = @setIntTimeFromList;
        [time, ~, status] = checkSpecValues;
        if status
            return;
        end    
     end   
     if source == addValueDLT_button
        edit_obj = addValueDLT_edit; 
        popup_obj = IntTime_popup;
        list = ini.DLT_list;
        setTimeFromList = @setDLTIntTimeFromList;
        [time, ~, status] = checkSpecValues;
        if status
            return;
        end    
     end   
     add_value = str2num(get(edit_obj,'String'));
     if isempty(add_value)
      waitfor(msgbox('Can not convert the add value to number'));
      return;
     end   
     val = popup_obj.Value;
     mode = popup_obj.String;
     if strcmp(mode(val), 'auto')        
        list(size(list,1)+1,:)={add_value, false, 'auto'};  
     elseif strcmp(mode(val), 'manual')
         list(size(list,1)+1,:)={add_value, false, time};   
     else 
         list(size(list,1)+1,:)={add_value, false, time}; 
     end   
     [~,idx]=sort([list{:,1}]');
     list = list(idx,:);
     if source == addValueIVL_button
       IVL_table.Data = list;
       ini.IVL_list = list;
     end  
     if source == addValueSpectra_button
       Spectra_table.Data = list;
       ini.Spectra_list = list;  
     end    
     if source == addValueDLT_button
       DLT_table.Data = list;
       ini.DLT_list = list;  
     end    
     if strcmp(mode{val}, 'list')
      setTimeFromList();
     end
   end
   
  function step_table_modif (source,eventdata)
     if source == IVL_table
         list = ini.IVL_list;
         time = cam_struct.expTime;
     end    
     if source == Spectra_table
         list = ini.Spectra_list;
         [time, ~, status] = checkSpecValues;
         if status
            return;
         end  
     end
     if source == DLT_table
         list = ini.DLT_list;
         [time, ~, status] = checkSpecValues;
         if status
            return;
         end  
     end
     row = eventdata.Indices(1,1);
     column = eventdata.Indices(1,2);
     if column == 2
       list(row,:)=[];
     else  
     time_value = eventdata.EditData;
     if ~strcmp(time_value, 'auto')
      if ~isnumeric(time_value)
        num_time = str2num(time_value);  
        if isempty(num_time)
         msgbox('Time value is not a number');
         time_value = time;
        else
         time_value = num_time;
        end 
      end  
      if (time_value<1) || (time_value>1e6) || rem(time_value,1)~=0
       msgbox('Time value is out of range');
       time_value = time;
      end 
     end
     list{row, column} = time_value;
     end
   if source == IVL_table
     ini.IVL_list = list;
     IVL_table.Data = ini.IVL_list;
   end  
   if source == Spectra_table
     ini.Spectra_list = list;
     Spectra_table.Data = list;
   end  
   if source == DLT_table
     ini.DLT_list = list;
     DLT_table.Data = list;
   end  
  end  
   
   function calibration_table_modif (source,eventdata)
     row = eventdata.Indices(1,1);
     column = eventdata.Indices(1,2);
     if (column == table_delete) 
      if ~check_calibration(calibration_list)   
       if(size(calibration_list,1) <= min_calibration)
       answer = questdlg(sprintf('Deleting this row will require recalibration of at least one point.\n Are you sure?'), ...
	     'Delete calibration', ...
	     'Yes','No','No'); 
       switch answer
        case 'Yes'
         calibration_list(row,:)=[];
         set(gotoButton, 'Enable', 'off');
        case 'No'
         return;
       end     
       else
          calibration_list(row,:)=[];
         [coef_X, coef_Y] = getTransformation(calibration_list);  
       end
      else
        calibration_list(row,:)=[];
        if (size(calibration_list,1) >= min_calibration) && ~check_calibration(calibration_list)
        set(gotoButton, 'Enable', 'on');
        end   
      end 
     else %%% if changed 
      if ~check_calibration(calibration_list)   
       answer = questdlg(sprintf('Changing this row will require recalibration of at least one point.\n Are you sure?'), ...
	     'Change calibration', ...
	     'Yes','No','No'); 
       switch answer
        case 'Yes'
         calibration_list{row,4}=[];
         calibration_list{row,5}=[];
        case 'No'
         return;
       end     
      else
         calibration_list{row,4}=[];
         calibration_list{row,5}=[];
      end   
      set(gotoButton, 'Enable', 'off');   
      set(calibrationButton, 'Enable', 'on');  
     end
     calibration_table.Data = generate_tabledata(calibration_list);
   end
   
   function addCalibButton_Callback (source,eventdata)
    [foundX, ~] = find(strcmp(map_name,get(addCalib_edit, 'String'))); 
    if foundX~=0
     calibration_list(size(calibration_list,1)+1, 1:3) = calibrationMapping({get(addCalib_edit, 'String')});
     calibration_table.Data = generate_tabledata(calibration_list);
     if size(calibration_list,1) >= min_calibration
      set(calibrationButton, 'Enable', 'on');
      set(gotoButton, 'Enable', 'off');
     end
    else
      msgbox(sprintf('Structure %s was not found in the name map',get(addCalib_edit, 'String')));
    end  
   end
   
   function moveButton_Callback(source,eventdata)   
%     moveToStr = get(X_setPos,'String');
%     getToStr = get(X_currentPos,'String');
%     fprintf(port,'zl');
%     if (~strcmp(moveToStr, getToStr)) && (~strcmp(moveToStr, 'manual'))
%      try
%         moveToX = str2num(moveToStr);
%         while (1)
%           fprintf(port,sprintf('m%dn%dS500\n',motorXind,moveToX));
%            while (port.BytesAvailable == 0)
%             pause (delaytime/10);
%            end    
%            if str2num(fgetl(port)) == moveToX
%              break;
%            end   
%          end  
%         set(X_currentPos,'String', 'update');
%      end   
%     end 
%     
%     moveToStr = get(Y_setPos,'String');
%     getToStr = get(Y_currentPos,'String');
%     if (~strcmp(moveToStr, getToStr)) && (~strcmp(moveToStr, 'manual'))
%      try
%         moveToY = str2num(moveToStr);
%         while (1)
%           fprintf(port,sprintf('m%dn%dS500\n',motorYind,moveToY));
%           while (port.BytesAvailable == 0)
%             pause (delaytime/10);
%           end    
%           if str2num(fgetl(port)) == moveToY
%              break;
%           end     
%         end  
%         set(Y_currentPos,'String', 'update');
%      end
%     end
%     
%     moveToStr = get(Z_setPos,'String');
%     getToStr = get(Z_currentPos,'String');
%     if (~strcmp(moveToStr, getToStr)) && (~strcmp(moveToStr, 'manual'))
%      try
%         moveToZ = str2num(moveToStr);
%          while (1)
%           fprintf(port,sprintf('m%dn%dS100\n',motorZind,moveToZ));
%           while (port.BytesAvailable == 0)
%             pause (delaytime/10);
%           end    
%           if str2num(fgetl(port)) == moveToZ
%             break;
%           end  
%          end  
%          set(Z_currentPos,'String', 'update');
%      end
%     end 
%   fprintf(port,'z');  
%   while (port.BytesAvailable == 0)
%      pause(delaytime/4);
%   end
%   portout = fgetl(port);
%   if strcmp(portout(1:4),'done')
%      resp = getresponse(port); 
%      updatefields(resp)
%   else
%        disp(sprintf('Erorr: not expected response form Arduino %s',portout));
%   end  
  end  
    
   function updateButton_Callback(source,eventdata)   
     %resp = getresponse(port);
     %updatefields(resp);
   end 
    
   function blockKeyHandler(source,event)
     hManager = uigetmodemanager(fig_handle);
    [hManager.WindowListenerHandles.Enabled] = deal(false);
    set(fig_handle,'KeyPressFcn', @key_pressed_fcn);   
   end  

   function key_pressed_fcn(fig_obj,eventDat)
    if running ~= 0
        return
    end    
    keypressed = get(fig_obj, 'CurrentKey');
    if strcmp(keypressed, 'escape')
%        close_cam(fig_handle, cam_struct);
%    elseif strcmp(keypressed, 'q')  
%        fprintf(port,'q\n');
%        pause(delaytime/5);
%        resp = getresponse(port);
%        updatefields(resp);
%    elseif strcmp(keypressed, 'rightarrow')    
%        fprintf(port,sprintf('m%dn%dS500\n',motorYind,keyMove));
%        set(Y_setPos,'String', 'manual');
%        set(Y_currentPos,'String', 'update');
%    elseif strcmp(keypressed, 'leftarrow')    
%        fprintf(port,sprintf('m%dn%dS500\n',motorYind,-keyMove));
%        set(Y_setPos,'String', 'manual');
%        set(Y_currentPos,'String', 'update');
%    elseif strcmp(keypressed, 'downarrow')    
%        fprintf(port,sprintf('m%dn%dS500\n',motorXind,keyMove));
%        set(X_setPos,'String', 'manual');
%        set(X_currentPos,'String', 'update');
%    elseif strcmp(keypressed, 'uparrow')    
%        fprintf(port,sprintf('m%dn%dS500\n',motorXind,-keyMove));    
%        set(X_setPos,'String', 'manual');
%        set(X_currentPos,'String', 'update');
%    elseif strcmp(keypressed, 's')    
%        fprintf(port,sprintf('m%dn%dS100\n',motorZind,keyMove));
%        set(Z_setPos,'String', 'manual');
%        set(Z_currentPos,'String', 'update');
%    elseif strcmp(keypressed, 'x')     
%        fprintf(port,sprintf('m%dn%dS100\n',motorZind,-keyMove));    
%        set(Z_setPos,'String', 'manual');
%        set(Z_currentPos,'String', 'update');
%    elseif strcmp(keypressed, 'return')    
%        fprintf(port,'q\n');
%        pause(delaytime/5);
%        resp = getresponse(port);
%        updatefields(resp);
    end
   end
   
   function my_closereq(src,callbackdata)
   if running || specPreviewRunnig
    waitfor(msgbox(sprintf('Can not stop while running. \nStop the measurement or spectra preview and try again')));
    return;
   end  
 %  fprintf(port,'q\n');
   if ~isempty(specDevices_list)
    closeAllSpectrometers();
   end    
   runpreview('close');
   delete(Keithley.handle);
   saveinitofile(iniFileName);
   % closeport(port);
   %%%% closing the arduino port leads to lose of the position values   

   delete(gcf);    
   end
   
   function addZoneButton_Callback(source,eventdata)  
    [x,y] = ginput(2);
    regionOfInterest_handle(reg_coordX1) = round(x(1));
    regionOfInterest_handle(reg_coordY1) = round(y(1));
    regionOfInterest_handle(reg_coordX2) = round(x(2));
    regionOfInterest_handle(reg_coordY2) = round(y(2));
    rectangle('Parent', axes_handle, 'Position',[x(1),y(1), abs(x(2)-x(1)), abs(y(2)-y(1))],'EdgeColor','r');
    set(addZoneButton,'Enable', 'off');
    set(clearZoneButton,'Enable', 'on');
   end
    
   function clearZonesButton_Callback(source,eventdata) 
    recObj = findobj('type','rectangle');
    delete(recObj);
    regionOfInterest_handle = [];
    set(addZoneButton,'Enable', 'on');
    set(clearZoneButton,'Enable', 'off');
   end
   
   
   function tabChangedCB(src, eventdata)
    tabNew = eventdata.NewValue;
     if (tabNew == handle_tab_result) && (handle_tab_result ~= get (axes_handle, 'Parent'))       
       set(axes_handle, 'Parent', handle_tab_result, 'Position', [0.14 0.55 0.30 0.40]);
     elseif (tabNew == handle_tab_stage) && (handle_tab_stage ~= get (axes_handle, 'Parent'))  
       set(axes_handle, 'Parent', handle_tab_stage, 'Position', [0.05 0.05 0.7 0.9]);  
     elseif (tabNew == handle_tab_camera) && (handle_tab_camera ~= get (axes_handle, 'Parent'))  
       set(axes_handle, 'Parent', handle_tab_camera, 'Position', [0.05 0.05 0.7 0.9]); 
     end
   end
    
   function settype(source,event)
     val = source.Value;
     type = source.String;
     if strcmp(type(val), 'current')
      set(start_units,'String', 'A');
      set(end_units,'String', 'A');
      set(limit_units,'String', 'V');
      set(mixed_limit_units,'String', 'V');
     else
      set(start_units,'String', 'V');
      set(end_units,'String', 'V');
      set(limit_units,'String', 'A');   
      set(mixed_limit_units,'String', 'A');
     end    
   end
   
   function setmeasurement(source,event)
     val = source.Value;
     mode = source.String;
     if strcmp(mode(val), 'auto')
       set(measurement_duration_edit,'Enable', 'off');  
     else  
       set(measurement_duration_edit,'Enable', 'on');   
     end  
   end
   
   function expTime_popup_Callback(source,event)
     val = source.Value;
     mode = source.String;
     if strcmp(mode(val), 'auto')        
       IVL_table.ColumnEditable = [false, true, false];
       for counter=1:size(ini.IVL_list,1)
         ini.IVL_list{counter,3} = 'auto';
       end  
       IVL_table.Data = ini.IVL_list;
       set(edit_ExpTime_list,'Enable', 'off');  
       set(button_ExpTime,'Enable', 'off');  
     elseif strcmp(mode(val), 'manual')
       IVL_table.ColumnEditable = [false, true, true];  
       set(edit_ExpTime_list,'Enable', 'off');  
       set(button_ExpTime,'Enable', 'off');   
     else 
       IVL_table.ColumnEditable = [false, true, false]; 
       set(edit_ExpTime_list,'Enable', 'on');  
       set(button_ExpTime,'Enable', 'on');
       setExpTimeFromList;
     end    
   end
   
   function setExpTimeFromList
     try
       expTime_template=csvread(get(edit_ExpTime_list,'String'),1);
     catch
       msgbox('Can not read expTime template file. Check path and file format'); 
       return;
     end
     for counter=1:size(ini.IVL_list,1)
         ini.IVL_list{counter,3} = round(interp1(expTime_template(:,1),expTime_template(:,2),ini.IVL_list{counter,1}));
     end
     IVL_table.Data = ini.IVL_list;
   end  

   function setIntTimeFromList
     try
       expTime_template=csvread(get(edit_intTime_list,'String'),1);
     catch
       msgbox('Can not read intTime template file. Check path and file format'); 
       return;
     end
     for counter=1:size(ini.Spectra_list,1)
         ini.Spectra_list{counter,3} = round(interp1(expTime_template(:,1),expTime_template(:,2),ini.Spectra_list{counter,1}));
     end
     Spectra_table.Data = ini.Spectra_list;
   end 

   function setDLTIntTimeFromList
     try
       expTime_template=csvread(get(edit_intTime_list,'String'),1);
     catch
       msgbox('Can not read intTime template file. Check path and file format'); 
       return;
     end
     for counter=1:size(ini.DLT_list,1)
         ini.DLT_list{counter,3} = round(interp1(expTime_template(:,1),expTime_template(:,2),ini.DLT_list{counter,1}));
     end
     DLT_table.Data = ini.DLT_list;
   end 

   function openListButton_Callback(source,event)
     [FileName,PathName,FilterIndex] = uigetfile(strcat(get(path_edit,'String'),filesep,'*.*'),'Select list file');
     if FileName
       set(open_edit,'String', [PathName,FileName]);
       set(path_edit,'String', PathName);
     end  
   end
   
   function addressButtonDir_Callback(source,event)
    PathName = uigetdir(get(path_edit,'String'));
    if PathName
      set(open_edit,'String', strcat(PathName,filesep,'filename'));
      set(path_edit,'String', PathName);
    end  
   end
   
   function loadMask_Button_Callback(source,event)
     answer = questdlg(sprintf('Loading a new mask will delete your calibration.\n Are you sure?'), ...
	'Load a new mask file', ...
	'Yes','No','No'); 
    switch answer
     case 'Yes'
        [FileName,PathName,FilterIndex] = uigetfile(strcat(get(loadMask_edit,'String'),filesep,'*.mat'),'Select mask file'); 
        if FileName
         ini.load_mask = strcat(PathName, filesep, FileName);
         [~,mask_name]= fileparts(ini.load_mask);
         set(loadMask_edit, 'String', mask_name);
         newCalibrationButton_Callback(source,event);
         [map_name, map_coord] = getMap(ini.load_mask);
         return;
        end    
     case 'No'
        return;
     end
          
   end    
   
   
   function setpulsed(source,event)
     val = source.Value;
     mode = source.String;
     if strcmp(mode(val), 'continuous')
       set(pulsed_duration_edit,'Enable', 'off'); 
       set(mixed_limit_edit, 'Enable', 'off'); 
       set(mixed_nplc_edit, 'Enable', 'off');
     elseif strcmp(mode(val), 'pulsed')
       set(pulsed_duration_edit,'Enable', 'on');   
       set(mixed_limit_edit, 'Enable', 'off'); 
       set(mixed_nplc_edit, 'Enable', 'off');
     elseif strcmp(mode(val), 'mixed')
       set(pulsed_duration_edit,'Enable', 'on');     
       set(mixed_limit_edit, 'Enable', 'on'); 
       set(mixed_nplc_edit, 'Enable', 'on');
     end  
   end
    
   function backVoltage_Callback(source,event)
    value = get(back_checkbox,'Value');
    if value
       set(backStart_edit, 'Enable', 'on');
       set(backEnd_edit, 'Enable', 'on');
       set(backLimit_edit, 'Enable', 'on');
       set(backStep_edit, 'Enable', 'on');
    else
       set(backStart_edit, 'Enable', 'off');
       set(backEnd_edit, 'Enable', 'off');
       set(backLimit_edit, 'Enable', 'off');
       set(backStep_edit, 'Enable', 'off');
    end  
   end
   
  function sweep_Callback(source,event)
    value = get(sweep_checkbox,'Value');
    if value
       set(open_label, 'String', 'Save as');
       set(path_edit, 'Enable', 'off');
    else
       set(path_edit, 'Enable', 'on');
       set(open_label, 'String', 'Open list');
    end  
  end
  
  function useIVL_Callback(source,event)
    value = get(useIVL_checkbox,'Value');
    if value
       set(useFullIVL_button,'Enable', 'on'); 
       set(addValueIVL_edit,'Enable', 'on');  
       set(addValueIVL_button,'Enable', 'on');
       set(clearIVL_button,'Enable', 'on'); 
       set(IVL_table, 'Enable', 'on');
       set(addValueIVL_units, 'Enable', 'on');
    else
       set(useFullIVL_button,'Enable', 'off');
       set(addValueIVL_edit,'Enable', 'off');  
       set(addValueIVL_button,'Enable', 'off'); 
       set(clearIVL_button,'Enable', 'off'); 
       set(IVL_table, 'Enable', 'off');
       set(addValueIVL_units, 'Enable', 'off');
    end
    imgOperations;
  end
  
  function imgOperations
    valueIVL = get(useIVL_checkbox,'Value');  
    if valueIVL
      set(ignoreZero_label,'Enable', 'on');
      set(ignoreZero_checkbox,'Enable', 'on');
      set(saveFig_label,'Enable', 'on');
      set(saveFig_checkbox,'Enable', 'on');
    else
      set(ignoreZero_label,'Enable', 'off');
      set(ignoreZero_checkbox,'Enable', 'off');  
      set(saveFig_label,'Enable', 'off');
      set(saveFig_checkbox,'Enable', 'off');
    end    
  end   

  function [smu,out] = checkSweepLimits(smu)
     out = 0;
     steps = str2num(get(steps_edit,'String'));
     if isempty(steps)
      waitfor(msgbox('Can not convert steps value to number'));
      out = 1;
      return;
     end  
     if (rem(steps,1) ~= 0) || (steps<= 0)
      waitfor(msgbox('Steps value should be positive integer number'));
      out = 1;
      return;
     end  
     smu.steps = steps;  
      
     start_value = str2num(get(start_edit,'String'));
     if isempty(start_value)
      waitfor(msgbox('Can not convert start value to number'));
      out = 1;
      return;
     end 
	 smu.start = start_value;
     
     end_value = str2num(get(end_edit,'String'));
     if isempty(end_value)
      waitfor(msgbox('Can not convert end value to number'));
      out = 1;
      return;
     end 
	 smu.end = end_value;
     
  end

  function clearStep_Callback (source,event)
   if source == clearIVL_button
    ini.IVL_list = {};
    IVL_table.Data = ini.IVL_list;
   end 
   if source == clearSpectra_button
    ini.Spectra_list = {};  
    Spectra_table.Data = ini.Spectra_list;
   end    
   if source == clearDLT_button
    ini.DLT_list = {};  
    DLT_table.Data = ini.DLT_list;
   end    
  end    
  
  function useFullStep_Callback(source,event)   
    [Keithley,out] = checkSweepLimits(Keithley);
    if out
        return;
    end
     if source == useFullIVL_button
        popup_obj = ExpTime_popup;
        setTimeFromList = @setExpTimeFromList;
        time = cam_struct.expTime;
     end   
     if source == useFullSpectra_button   
        popup_obj = IntTime_popup;
        setTimeFromList = @setIntTimeFromList;
        [time, ~, status] = checkSpecValues;
        if status
            return;
        end    
     end
     if source == useFullDLT_button   
        popup_obj = IntTime_popup;  
        setTimeFromList = @setDLTIntTimeFromList;
        [time, ~, status] = checkSpecValues;
        if status
            return;
        end 
     end    
    list = {};
    val = popup_obj.Value;
    mode = popup_obj.String;
    for cnt=1:Keithley.steps
        list{cnt,1} = Keithley.start + ((Keithley.end-Keithley.start)/(Keithley.steps-1))*(cnt-1);
        list{cnt,2} = false;
        if strcmp(mode{val}, 'auto')
         list{cnt,3} = 'auto';
        else    
         list{cnt,3} = time;
        end
    end
    if source == useFullIVL_button
     ini.IVL_list = list;
     IVL_table.Data = list;
    end 
    if source == useFullSpectra_button
     Spectra_table.Data = list;
     ini.Spectra_list = list;   
    end
    if source == useFullDLT_button
     DLT_table.Data = list;
     ini.DLT_list = list;   
    end
    if strcmp(mode{val}, 'list')
      setTimeFromList();
    end
  end
  
  function singleCh_Callback(source,event)
    value = get(singleCh_checkbox,'Value');
    if value
       set(back_checkbox,'Value',0, 'Enable', 'off');
       backVoltage_Callback(source,event);
    else
       set(back_checkbox, 'Enable', 'on');
       backVoltage_Callback(source,event);
    end  
  end 
  
  
        
   function postProc_Button_Callback(source,event)
     [FileName,PathName,FilterIndex] = uigetfile(strcat(get(postProc_edit,'String'),filesep,'*.m'),'Select *.m file with IV post processing function'); 
        if FileName
         ini.load_postProc = strcat(PathName, filesep, FileName);
         [~,postProc_name]= fileparts(ini.load_postProc);
         set(postProc_edit, 'String', postProc_name);
         eval(sprintf('IVanalysis = @(pathAnalysis, filenameAnalysis, handleAnalysis)%s(pathAnalysis, filenameAnalysis, handleAnalysis);',FileName));
        end              
   end 
  
  function usePostProc_Callback(source,event)
    value = get(usePostProc_checkbox,'Value');
    if value
       set(postProc_edit,'Enable', 'on');
       set(postProc_Button,'Enable', 'on');
       eval(sprintf('IVanalysis = @(pathAnalysis, filenameAnalysis, handleAnalysis)%s(pathAnalysis, filenameAnalysis, handleAnalysis);',get(postProc_edit, 'String')));
    else
       IVanalysis = @(pathAnalysis, filenameAnanlysis, handleAnalysis){}; 
       set(postProc_edit,'Enable', 'off');
       set(postProc_Button,'Enable', 'off');
    end  
  end 

    function inProc_Button_Callback(source,event)
     [FileName,PathName,FilterIndex] = uigetfile(strcat(get(inProc_edit,'String'),filesep,'*.m'),'Select *.m file with IV post processing function'); 
        if FileName
         ini.load_inProc = strcat(PathName, FileName);
         [~,inProc_name]= fileparts(ini.load_inProc);
         set(inProc_edit, 'String', inProc_name);
         eval(sprintf('IVinProc = @(IVdata)%s(IVdata);',FileName));
        end              
   end 

   function useInProc_Callback(source,event)
    value = get(useInProc_checkbox,'Value');
    if value
       set(inProc_edit,'Enable', 'on');
       set(inProc_Button,'Enable', 'on');
       eval(sprintf('IVinProc = @(in_data)%s(in_data);',get(inProc_edit, 'String')));
    else
       IVinProc = @(in_data)dummy_func(in_data);
       set(inProc_edit,'Enable', 'off');
       set(inProc_Button,'Enable', 'off');
    end  
  end 
  
  function useFullImage_Callback(source,event)
    value = get(useFullImg_checkbox,'Value');
    clearZonesButton_Callback(source,event);
    if value
       set(addZoneButton,'Enable', 'off');
       set(clearZoneButton,'Enable', 'off');
    else
       set(addZoneButton,'Enable', 'on');
    end  
  end 
  
  function set_intTimeList_Callback(source,event)
     [FileName,PathName,FilterIndex] = uigetfile(strcat(get(edit_intTime_list,'String'),filesep,'*.*'),'Select template for IntTime');
     if FileName 
      set(edit_intTime_list,'String', [PathName,FileName]);
     end 
     setIntTimeFromList;
   end
 

   function set_expTimeList_Callback(source,event)
     [FileName,PathName,FilterIndex] = uigetfile(strcat(get(edit_ExpTime_list,'String'),filesep,'*.*'),'Select template for ExpTime');
     if FileName 
      set(edit_ExpTime_list,'String', [PathName,FileName]);
     end 
     setExpTimeFromList;
   end
   
  function [cam_out, response] = read_CamSettings(camera)
%    imgSize_value = str2num(get(edit_img_size,'String'));
%     if isempty(imgSize_value)
%      msgbox('Can not imgSize value to number');
%      response = 1;
%      return;
%     end  
%     if (imgSize_value<1) || (imgSize_value>2048) || rem(imgSize_value,64)~=0
%      msgbox(sprintf('imgSize value is out of range.\nNote: size can only be changed in increments of 64'));
%      response = 2;
%      return;
%     end   
%    imgOffset_value = str2num(get(edit_img_offset,'String'));
%     if isempty(imgOffset_value)
%      msgbox('Can not imgOffset value to number');
%      response = 3;
%      return;
%     end  
%     if (imgOffset_value<0) || (imgOffset_value+imgSize_value>2048) || rem(imgOffset_value,1)~=0
%      msgbox('imgOffset value is out of range');
%      response = 4;
%      return;
%     end   
%    ExpTime_value = str2num(get(edit_setExpTime,'String'));
%     if isempty(ExpTime_value)
%      msgbox('Can not ExpTime value to number');
%      response = 5;
%      return;
%     end  
%     if (ExpTime_value<1) || (ExpTime_value>1e6) || rem(ExpTime_value,1)~=0
%      msgbox('ExpTime values is out of range');
%      response = 6;
%      return;
%     end 
%   response =0;  
%   cam_out =camera;  
%   cam_out.expTime = ExpTime_value;
%   cam_out.reverseX = get(checkbox_imgX,'Value');
%   cam_out.reverseY = get(checkbox_imgY,'Value');
%   cam_out.imgSize = imgSize_value;
%   cam_out.imgOffset = imgOffset_value;
  cam_out = camera;
  response = 0;				   
  end    
   
   
   function setimg_controls_Callback(source,eventdata)
%   if running == 1
%       return;
%   end    
%   [cam_struct, response] = read_CamSettings(cam_struct);
%   if response 
%      return;
%   end     
%   set(fig_handle,'CurrentAxes',axes_handle);
%   cam_struct = set_cam(cam_struct);
   end
   
   
   function runButton_Callback(source,event)
     moveZ = 500;
     setRunningState;  
     running = 1;
     just_sweep = get(sweep_checkbox,'Value');
%%%%%
%%%%% routine checks for stupidity of user
     
    if just_sweep
      pathToSaveResult = get(open_edit,'String');
      find_delimeters = strfind(pathToSaveResult,filesep);
      pathToSaveResult = pathToSaveResult(1:find_delimeters(length(find_delimeters)));
      tmpString = get(open_edit,'String');
      num = 1;
      run_list{num, 1} = tmpString(find_delimeters(length(find_delimeters))+1:end);
      run_list{num, 2} = 0; %displacement X for position
      run_list{num, 3} = 0; %displacement Y for position
    else    
     pathToSaveResult = get(path_edit,'String');   
     
     if check_calibration(calibration_list)
       waitfor(msgbox('Calibration is not done yet'));
       setIdleState;
       return;  
     end   
     
     try 
      fid = fopen(get(open_edit, 'String'), 'r');
      num = 0;
       while ~feof(fid)
         num = num+1;
         run_struct_string = strsplit(fgetl(fid)); 
         run_list{num, 1} = run_struct_string{1};
         run_list{num, 2} = 0; %displacement X for position
         run_list{num, 3} = 0; %displacement Y for position
         num_split = 1;
         while num_split < size(run_struct_string,2)
          num_split = num_split + 1;   
          run_keyword = strsplit(run_struct_string{num_split},'=');
          if strcmp(run_keyword{1}, 'deltaX')
              run_list{num,2} = str2num(run_keyword{2});
          elseif strcmp(run_keyword{1}, 'deltaY')
              run_list{num,3} = str2num(run_keyword{2});
          end
         end    
         [foundX, ~] = find(strcmp(map_name,run_list{num, 1})); 
         if foundX == 0
           waitfor(msgbox(sprintf('Structure to measure %s not found in sample map', run_list{num, 1})));
           setIdleState;
           return;  
         end
       end
       fclose(fid);
     catch
      waitfor(msgbox('Can not open list file'));
      setIdleState;
      return;
     end
    end 
    
     [Keithley, status] = checkSweepLimits(Keithley);
      if status
       setIdleState;
       return;
     end  
	 
     repeat = str2num(get(repeat_edit,'String'));
     if isempty(repeat)
      waitfor(msgbox('Can not convert repeat value to number'));
      setIdleState;
      return;
     end  
     if rem(repeat,1) ~= 0 || repeat<= 0
      waitfor(msgbox('Repeat value should be positive integer number'));
      setIdleState;
      return;
     end
	 Keithley.repeat = repeat;
     
     limit_value = str2num(get(limit_edit,'String'));
     if isempty(limit_value)
      waitfor(msgbox('Can not convert limit value value to number'));
      setIdleState;
      return;
     end 
     
     popup_value = get(measurement_popup, 'Value');
     popup_str = get(measurement_popup, 'String');
     
     if strcmp(popup_str{popup_value},'manual')
       measurement_duration = str2num(get(measurement_duration_edit,'String'));
       measure_delay = get(measurement_duration_edit,'String');
       if isempty(measurement_duration)
         waitfor(msgbox('Can not convert measurement time value to number'));
         setIdleState;
        return;
       end  
       if measurement_duration < 0
        waitfor(msgbox('Measurement time value should be not negative'));
        setIdleState;
       return;
       end
     else   
      measurement_duration = -1;  
      measure_delay = 'off';
     end
	 Keithley.delay = measure_delay;
     
     nplc_str = get(measurement_nplc_edit,'String');
     nplc_value = str2num(nplc_str);
     if isempty (nplc_value)
      waitfor(msgbox('Can not convert NPLC value to number'));
      setIdleState;
      return;
     end  
     if nplc_value < 0
      waitfor(msgbox('NPLC value should be not negative'));
      setIdleState;
      return;
     end
	 
     popup_value = get(pulsed_popup, 'Value');
     popup_str = get(pulsed_popup, 'String');
     
     if ~strcmp(popup_str{popup_value},'continuous')
       pulse_duration = str2num(get(pulsed_duration_edit,'String'));
       pulse_delay = get(pulsed_duration_edit,'String');
       if isempty(pulse_duration)
         waitfor(msgbox('Can not convert pulse duration value to number'));
         setIdleState;
        return;
       end  
       if pulse_duration < 0
        waitfor(msgbox('Pulse duration value should be not negative'));
        setIdleState;
       return;
       end
     else   
      pulse_duration = -1; 
      pulse_delay = 'off';
     end
	 Keithley.pulse = pulse_delay;
         
     if strcmp(popup_str{popup_value},'mixed')
       mixed_limit = str2num(get(mixed_limit_edit,'String'));
       nplc_mixed_str = get(mixed_nplc_edit,'String');
       mixed_nplc = str2num(nplc_mixed_str);
       if isempty(mixed_limit)
         waitfor(msgbox('Can not convert mixed measurement limit value to number'));
         setIdleState;
        return;
       end  
       if mixed_limit < 0
        waitfor(msgbox('Mixed measurement limit value should be not negative'));
        setIdleState;
       return;
       end
       if isempty(mixed_nplc)
         waitfor(msgbox('Can not convert mixed measurement NPLC value to number'));
         setIdleState;
        return;
       end  
       if mixed_nplc < 0
        waitfor(msgbox('Mixed measurement NPLC value should be not negative'));
        setIdleState;
       return;
       end
     end
        
     contents = get(source_popup,'String'); 
     source_ch = contents{get(source_popup,'Value')};
	 Keithley.source = source_ch;
	 if strcmp(source_ch,'smua')
         Keithley.drain = 'smub';
     else
         Keithley.drain = 'smua';
     end 
	 
	 
     contents = get(type_popup,'String');
     type_ch = contents{get(type_popup,'Value')};
	 if strcmp(type_ch, 'current')
	   Keithley.type = 'i';
	 else
	   Keithley.type = 'v';
	 end  
     
    backCheck = get(back_checkbox,'Value');
    if backCheck
     backStart_value = str2num(get(backStart_edit,'String'));
     set_backVoltage = get(backStart_edit,'String');
     if isempty(backStart_value)
      waitfor(msgbox('Can not convert back voltage start value to number'));
      setIdleState;
      return;
     end 
     
     backEnd_value = str2num(get(backEnd_edit,'String'));
     if isempty(backEnd_value)
      waitfor(msgbox('Can not convert back voltage end value to number'));
      setIdleState;
      return;
     end 
     
     backLimit_value = str2num(get(backLimit_edit,'String'));
     set_backLimit = get(backLimit_edit,'String');
     if isempty(backLimit_value)
      waitfor(msgbox('Can not convert back voltage limit value to number'));
      setIdleState;
      return;
     end 
	 Keithley.drainLimit = set_backLimit;
            
     backSteps_value = str2num(get(backStep_edit,'String'));
     if isempty(backSteps_value)
      waitfor(msgbox('Can not convert back voltage steps value to number'));
      setIdleState;
      return;
     end  
     if (rem(backSteps_value,1) ~= 0) || (backSteps_value<= 0)
      waitfor(msgbox(' Back voltage steps value should be positive integer number'));
      setIdleState;
      return;
     end
     if backSteps_value>1
      backStep_change =  (backEnd_value - backStart_value)/(backSteps_value-1);
     else
      backStep_change = 0;
     end 
    else
     backSteps_value = 1;
     set_backVoltage = 'off';
     set_backLimit = 'off';
     Keithley.drainLimit = 'off';
    end  

    val = sense_popup.Value;
    mode = sense_popup.String;
    if strcmp(mode(val), '2&4 wire')
        senseSelectArray = [false, true];
    elseif strcmp(mode(val), '4 wire')
        senseSelectArray = [true];
    else
        senseSelectArray = [false];
    end
    
    ini.senseDrain_value =  get(sense_drainCheckbox, 'Value');
    Keithley.sense_drain = ini.senseDrain_value;
    
    singleCh_value = get(singleCh_checkbox,'Value');
	Keithley.single_ch = singleCh_value;
    
   [cam_struct, response] = read_CamSettings(cam_struct);
%   if response
%      setIdleState;
%      return;
%   end
   
    
  repeat_value = str2num(get(edit_repeat_img,'String'));
  if isempty(repeat_value)
    waitfor(msgbox('Can not convert number of snapshot repetitions'));
    setIdleState;
    return;
  end  
    if (rem(repeat_value,1) ~= 0) || (repeat_value <= 0)
    waitfor(msgbox(' Image repeat should be a positive integer number'));
    setIdleState;
    return;
  end 
  
  ini.ignoreZero_value = get(ignoreZero_checkbox, 'Value');
  useIVL_value = get(useIVL_checkbox, 'Value');
  
  ini.unitsIVL_value =  get(addValueIVL_units, 'Value');
  tmp_str = get(addValueIVL_units, 'String');
  if strcmp(tmp_str{ini.unitsIVL_value}, 'A')
   IVLSourceType = 'current';
  else 
   IVLSourceType = 'voltage';
  end 
  
  ini.unitsSpectra_value =  get(addValueSpectra_units, 'Value');
  tmp_str = get(addValueSpectra_units, 'String');
  if strcmp(tmp_str{ini.unitsSpectra_value}, 'A')
   spectraSourceType = 'current';
  else 
   spectraSourceType = 'voltage';
  end 
  clearvars tmp_str;
  
  ini.useFullImg_value = get(useFullImg_checkbox, 'Value');
  if (size(regionOfInterest_handle,1) == 0) && (ini.useFullImg_value == false) && useIVL_value
         msgbox('Select region of interest or use full image');
         setIdleState;
         return;
  end 
  
  val = ExpTime_popup.Value;
  mode = ExpTime_popup.String;
  if strcmp(mode(val), 'list')
    try
     expTime_template=csvread(get(edit_ExpTime_list,'String'),1);
    catch
      msgbox('Can not read expTime template file. Check path and  file format'); 
	  setIdleState;
    return;
    end	
  end

  if useIVL_value && isempty(ini.IVL_list)
     msgbox('There are no IVL points to measure. Check the IVL table'); 
	 setIdleState;  
     return;
  end   
  
  useSpectra_value = get(checkbox_useSpec, 'Value') && (get(useSpectra_checkbox, 'Value') || get(useDLT_checkbox, 'Value'));
  
  if useSpectra_value 
     spmeter.device = specDevices_list(get(selectSpec_popup,'Value'));
     [spmeter.time,spmeter.averaging,response] = checkSpecValues;
     if response
       setIdleState; 
       return;
     end     
  end  
  
  if specPreviewRunnig 
     msgbox('Spectral preview is running. Stop it first'); 
	 setIdleState;  
     return;
  end
  useSpectra_value = get(useSpectra_checkbox, 'Value') && get(checkbox_useSpec, 'Value');
  
  if useSpectra_value && isempty(ini.Spectra_list)
     msgbox('There are no points to measure for spectral measurements. Check the table'); 
	 setIdleState;  
     return;
  end
 
  useDLT_value = get(useDLT_checkbox, 'Value') && get(checkbox_useSpec, 'Value');
  if useDLT_value && isempty(ini.DLT_list)
     msgbox('There are no points to measure for DLT. Check the table'); 
	 setIdleState;  
  end 
  
  tmp_str = get(addValueDLT_units, 'String');
  if strcmp(tmp_str{get(addValueDLT_units,'Value')}, 'A')
   DLTSourceType = 'current';
  else 
   DLTSourceType = 'voltage';
  end 
  clearvars tmp_str;
  
 ini.spectralROIStart_value = str2num(get(edit_startSpectralROI, 'String'));
 ini.spectralROIEnd_value = str2num(get(edit_endSpectralROI, 'String'));
 ini.spectralROIFull =  get(checkbox_fullROI, 'Value');
 ini.darkSpectrum_value = get(useDarkSpectrum_checkbox, 'Value');
 ini.darkSpectrumStep_value = get(useDarkSpectrumStep_checkbox, 'Value');  
  
  if useSpectra_value && ~(ini.spectralROIFull)
   startSpectralROI_value = str2num(get(edit_startSpectralROI,'String'));
     if isempty(startSpectralROI_value)
      waitfor(msgbox('Can not convert to number start value of spectral ROI'));
      setIdleState;
      return;
     end  
   endSpectralROI_value = str2num(get(edit_endSpectralROI,'String'));
     if isempty(endSpectralROI_value)
      waitfor(msgbox('Can not convert to number end value of spectral ROI'));
      setIdleState;
      return;
     end       
  end    
  
  DLTref_value = str2num(get(DLTref_edit,'String'));
  if isempty(DLTref_value)
    waitfor(msgbox('Can not convert DLT reference to number'));
    setIdleState;
    return;
  end 
  
  DLTstabilization_value = str2num(get(DLTstabilization_edit,'String'));
  if isempty(DLTstabilization_value)
    waitfor(msgbox('Can not convert DLT stabilization period to a number'));
    setIdleState;
    return;
  end  
    if DLTstabilization_value < 0
    waitfor(msgbox(' DLT stabilization period should not be negative'));
    setIdleState;
    return;
    end 
  
  
  DLTrepeat_value = str2num(get(DLTrepeat_edit,'String'));
  if isempty(DLTrepeat_value)
    waitfor(msgbox('Can not convert number of repetaitions for DLT'));
    setIdleState;
    return;
  end  
  if (rem(DLTrepeat_value,1) ~= 0) || (DLTrepeat_value <= 0)
    waitfor(msgbox(' Number of repetitions for DLT should be a positive integer number'));
    setIdleState;
    return;
  end 
    
  DLTrefTime_value = str2num(get(DLTref_edit_time, 'String'));
   if isempty(DLTrefTime_value)
           DLTrefTime_value = get(DLTref_edit_time, 'String');
           if ~strcmp(DLTrefTime, 'auto')
              waitfor(msgbox('DLT reference integration time value should be either "auto" or a positive number'));               
              setIdleState;
              return;
           end   
   else
           if (rem(DLTrefTime_value,1) ~= 0) || (DLTrefTime_value <= 0)
              waitfor(msgbox('DLT integration time should is not a positive integer number'));
              setIdleState;
              return;
           end
           DLTrefTime_value = get(DLTref_edit_time, 'String');
   end
           
  if get(useAutoSave_checkbox ,'Value') && get(saveFull_checkbox,'Value')
  autoSave_value = str2num(get(autoSave_edit,'String'));    
  if isempty(autoSave_value)
    waitfor(msgbox('Auto save interval can not be converted to number'));
    setIdleState;
    return;
  end  
  if (rem(autoSave_value,1) ~= 0) || (autoSave_value <= 0)
    waitfor(msgbox('Use a positive integer number for autosave interval'));
    setIdleState;
    return;
  end 
  end  
    
    
  Keithley.highC = get(highC_checkbox, 'Value');
  
      
  saveinitofile(iniFileName);  
%%%% end of routine checks
%%%%

     ONtime = datetime('now');

       Keithley.handle=setupKeithley(KeithleyAddress, KeithleyPort);  
       pause(delaytime);
       fprintf(Keithley.handle,'print(localnode.linefreq)');
       Keithley.freq = str2num(fscanf(Keithley.handle));
         
     nplc_string_value = num2str((nplc_value/1000)*Keithley.freq, '%.3f');
     
     popup_value = get(pulsed_popup, 'Value');
     popup_str = get(pulsed_popup, 'String');
     if strcmp(popup_str{popup_value}, 'mixed')
     mixed_nplc_string = num2str((mixed_nplc/1000)*Keithley.freq, '%.3f');  
     end       
     
     %%%%%%%%%%%%%%%%%%%% bug fix
     %%%%%%%%%%%looks that there's some trouble reading current value
     %%%%%%%%%%%%%%%%%%fix does not really work should be replaced with
     %%%%%%%%%%%%%%%%%%something more complicated
%     resp = getresponse(port);
%     moveToZ = resp(motorZind,currentPositionInd);
%     while(1)
%      if moveToZ == resp(motorZind,currentPositionInd)
%        break;
%      else
%        moveToZ = resp(motorZind,currentPositionInd);
%      end   
%     end     
     for num = 1:size(run_list,1)
       %%%% verification if stage is not moving and needle is in contact with sample should be added  
% % %        resp = getresponse(port);
% % %        moveTo = resp(motorZind,currentPositionInd) -  moveZ;
      if ~just_sweep
%       moveTo = moveToZ -  moveZ;
%       fprintf(port,'zl');
%       while (1)
%         fprintf(port,sprintf('m%dn%dS100\n',motorZind,moveTo));
%         while (port.BytesAvailable == 0)
%           pause (delaytime/10);
%         end    
%         if str2num(fgetl(port)) == moveTo
%           break;
%         end   
%       end
%       fprintf(port,'z');
%       set(Z_setPos,'String',num2str(moveTo));
%       set(Z_currentPos,'String', 'update');
%       
%       pause(delaytime/5);
%       while(1)
%         if running == 0
%           fprintf(port,sprintf('q\n'));
%           pause(delaytime/5);
%           fclose(Keithley.handle);
%           resp = getresponse(port);
%           updatefields(resp);
%           setIdleState;
%           return;
%         end    
%         if port.BytesAvailable > 0
%           portout = fgetl(port);
%           if ~strcmp(portout(1:4),'done')
%            disp(sprintf('Erorr: not expected response form Arduino %s',portout));
%           end
%           break;
%         end  
%       end   
%       set(Z_currentPos,'String',num2str(moveTo));
             
%      [foundX, ~] = find(strcmp(map_name,run_list{num, 1})); 
%      moveToStruct(foundX,run_list{num, 2}, run_list{num, 3},1);
       
%       pause(delaytime/5);
%       while(1)
%          if running == 0
%           fprintf(port,sprintf('q\n'));
%           pause(delaytime/5);
%           fclose(Keithley.handle);
%           resp = getresponse(port);
%           updatefields(resp);
%           setIdleState;
%           return;
 %        end   
%         if port.BytesAvailable > 0
%           portout = fgetl(port);
%           if ~strcmp(portout(1:4),'done')
%            disp(sprintf('Erorr: not expected response form Arduino %s',portout));
%           end
%           break;
%         end  
%       end
%       resp = getresponse(port);
%       updatefields(resp);  
       
%       moveTo = moveToZ;
%       fprintf(port,'zl');
%       while (1)
%         fprintf(port,sprintf('m%dn%dS100\n',motorZind,moveTo));
%         while (port.BytesAvailable == 0)
%           pause (delaytime/10);
%         end    
%         if str2num(fgetl(port)) == moveTo
%           break;
%         end   
%       end
%       fprintf(port,'z');
%       set(Z_setPos,'String',num2str(moveTo));
%       set(Z_currentPos,'String', 'update');
%       
%       pause(delaytime/5);
%       while(1)
%         if running == 0
%           fprintf(port,sprintf('q\n'));
%           pause(delaytime/5);
%           fclose(Keithley.handle);
%           resp = getresponse(port);
%           updatefields(resp);
%           setIdleState;
%           return;
%         end    
%         if port.BytesAvailable > 0
%           portout = fgetl(port);
%           if ~strcmp(portout(1:4),'done')
%               
%            disp(sprintf('Erorr: not expected response form Arduino %s',portout));
%           end
%           break;
%         end  
%       end
%       set(Z_currentPos,'String',num2str(moveTo));
       
    end   
       
      backstep = 1; 
      while  (backSteps_value >= backstep)
       if ~strcmp(set_backVoltage,'off')
         set_backVoltage = num2str(backStart_value + (backstep-1)* backStep_change, '%.3f');
         Keithley.drainVoltage = set_backVoltage;
         save_filename = strcat(run_list{num, 1},'_',set_backVoltage);
       else
         save_filename = run_list{num, 1};
         Keithley.drainVoltage = 'off';
       end
       backstep = backstep + 1;    
       
       
       %%%%%%%%% header for IV *.dat file
       
       comment = '######################';
       comment = sprintf('%s\n#\n# measurement of %s\n#\n',comment, run_list{num, 1}); 
       comment = sprintf('%s#date %s\n',comment, datetime('now')); 
       comment = sprintf('%s#Keithley source %s\n',comment, source_ch); 
       comment = sprintf('%s#Source in %s injection mode\n',comment, type_ch);
       comment = sprintf('%s#Steps in sweep %s \n',comment, get(steps_edit,'String'));
       comment = sprintf('%s#Sweep repeat for %s times \n',comment, get(repeat_edit,'String'));
       comment = sprintf('%s#Start value for sweep %s %s\n',comment, get(start_edit,'String'),get(start_units,'String'));
       comment = sprintf('%s#End value for sweep %s %s\n',comment, get(end_edit,'String'), get(end_units,'String'));
       comment = sprintf('%s#Limit for sweep step %s %s\n',comment, get(limit_edit,'String'), get(limit_units,'String'));
       if strcmp(get(measurement_duration_edit,'Enable'),'off')
        comment = sprintf('%s#Measurement acquisition period is done in AUTO mode\n',comment);
       else
        comment = sprintf('%s#Measurement acquisition period is %s s\n',comment, measure_delay);   
       end
       comment = sprintf('%s#NPLC value %d ms (for detected line frequency %d Hz is %s)\n',comment, nplc_value, Keithley.freq, nplc_string_value); 
	   comment = sprintf('%s#\n#\n',comment);
	   
       val = pulsed_popup.Value;
       mode = pulsed_popup.String;
       if strcmp(mode(val), 'continuous')
        comment = sprintf('%s#Continuous operation of the source\n#\n#\n',comment);   
	   elseif strcmp(mode(val), 'pulsed')	
		comment = sprintf('%s#Pulse operation of the source with delays of %s s\n#\n#\n',comment, pulse_delay);
       elseif strcmp(mode(val), 'mixed')
        comment = sprintf('%s#Mixed operation of the source with delays of %s s\n',comment, pulse_delay);   
        comment = sprintf('%s#NPLC value for continuous operation arm %d ms (for detected line frequency %d Hz is %s)\n',comment, mixed_nplc, Keithley.freq, mixed_nplc_string); 
        comment = sprintf('%s#Limit voltage for continuous operation arm %s %s\n',comment, get(mixed_limit_edit,'String'), get(mixed_limit_units,'String'));
	   end	
	   comment = sprintf('%s#\n#\n',comment);
	   
	   if ~strcmp(set_backVoltage,'off')
         comment = sprintf('%s#Back voltage to PD %s V\n',comment, set_backVoltage);
       else
         comment = sprintf('%s#\n',comment);   
       end
	   comment = sprintf('%s#\n#\n',comment);	
		
       comment = sprintf('%s#Comment: %s\n',comment, get(edit_Comment, 'String'));
	   comment = sprintf('%s#\n#\n',comment);


       comment = sprintf('%s#\n',comment);
       comment = sprintf('%s#\n#\n',comment);
	   
       if Keithley.highC && Keithley.single_ch
	 comment = sprintf('%s#High capacitance mode is enabled\n',comment);
       elseif Keithley.highC
	 comment = sprintf('%s#High capacitance mode is enabled for both channels\n',comment);
       else
	 comment = sprintf('%s#High capacitance mode is disabled (normal operation)\n',comment);
       end

       comment = sprintf('%s#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n',comment);

       if Keithley.single_ch
         comment = sprintf('%s#\n',comment);
       else
         if Keithley.sense_drain
           comment = sprintf('%s#Drain sense follows source \n',comment);
         else
           comment = sprintf('%s#Drain uses local sense (i.e. 2 probe measurement)\n',comment);
         end
       end

       if senseSelectArray == [false, true]
         comment = sprintf('%s#Both 2 and 4 wire measurements\n',comment);
	   elseif senseSelectArray == [false]
	     comment = sprintf('%s#2 wire measurements\n',comment);
	   else  
         comment = sprintf('%s#4 wire measurements\n',comment);
	   end 

       headerLine = '';
       if size(senseSelectArray,2)==2
         add_pr = {'_4pr','_2pr'};
		 pr_cnt = 1;
	   else
         add_pr = {'',''};
		 pr_cnt = 2;
	   end 
   
       if singleCh_value
         add_src={'',''};
		 ch_cnt = 2;
         ch_cnt_init = 2;
	   else 
		 add_src={'S','D'};
		 ch_cnt = 1;
         ch_cnt_init = 1;
       end	 
       
       val = pulsed_popup.Value;
       mode = pulsed_popup.String;
       if strcmp(mode(val), 'mixed')
           add_mx = {'_puls','_cont'};
           mx_cnt = 1;
           mx_cnt_init = 1;
       else
           add_mx = {'',''};
           mx_cnt = 2;
           mx_cnt_init = 2;
       end    
		
       while pr_cnt<=2
	    while mx_cnt<=2
	     while ch_cnt <=2
		   headerLine = sprintf('%sI%s%s%s, V%s%s%s', headerLine, add_src{ch_cnt},add_pr{pr_cnt}, add_mx{mx_cnt}, add_src{ch_cnt},add_pr{pr_cnt},add_mx{mx_cnt});
		   ch_cnt = ch_cnt+1;
           if ch_cnt<=2
		     headerLine = sprintf('%s, ',headerLine);
		   end 
         end  
           ch_cnt = ch_cnt_init;
		   mx_cnt = mx_cnt + 1;
		   if mx_cnt<=2
		     headerLine = sprintf('%s, ',headerLine);
           end 
        end
        mx_cnt = mx_cnt_init;
        pr_cnt = pr_cnt + 1;
		if pr_cnt<=2
		     headerLine = sprintf('%s, ',headerLine);
        end
       end
       comment = sprintf('%s%s\n', comment, headerLine);
	   %%%%%%%%% end of header for *.dat file    
       
      if useIVL_value 
       
       %%%%%%%%% header for IVL *.dat file
       
       comment_IVL = '######################';
       comment_IVL = sprintf('%s\n#\n# measurement of %s\n#\n',comment_IVL, run_list{num, 1}); 
       comment_IVL = sprintf('%s#date %s\n',comment_IVL, datetime('now')); 
       comment_IVL = sprintf('%s#Keithley source %s\n',comment_IVL, source_ch); 
       comment_IVL = sprintf('%s#Source in %s injection mode\n',comment_IVL, IVLSourceType);
       comment_IVL = sprintf('%s#Steps in sweep %s \n',comment_IVL, num2str(size(ini.IVL_list,1)));       
       comment_IVL = sprintf('%s#\n',comment_IVL);
       if strcmp(IVLSourceType,'current')
        comment_IVL = sprintf('%s#Start value for sweep %s A\n',comment_IVL, num2str(ini.IVL_list{1,1}));
        comment_IVL = sprintf('%s#End value for sweep %s A\n',comment_IVL, num2str(ini.IVL_list{size(ini.IVL_list,1),1}));
       else
        comment_IVL = sprintf('%s#Start value for sweep %s V\n',comment_IVL, num2str(ini.IVL_list{1,1}));
        comment_IVL = sprintf('%s#End value for sweep %s V\n',comment_IVL, num2str(ini.IVL_list{size(ini.IVL_list,1),1}));
       end     
       if strcmp(Keithley.type, 'v')
           comment_IVL = sprintf('%s#Limit for sweep step %s %s and %s %s\n',comment_IVL, get(limit_edit,'String'), get(limit_units,'String'), get(end_edit,'String'), get(end_units,'String'));
       else
           comment_IVL = sprintf('%s#Limit for sweep step %s %s and %s %s\n',comment_IVL, get(end_edit,'String'), get(end_units,'String'), get(limit_edit,'String'), get(limit_units,'String'));
       end    
       if strcmp(get(measurement_duration_edit,'Enable'),'off')
        comment_IVL = sprintf('%s#Measurement acquisition period is done in AUTO mode\n',comment_IVL);
       else
        comment_IVL = sprintf('%s#Measurement acquisition period is %s s\n',comment_IVL, measure_delay);   
       end
       comment_IVL = sprintf('%s#NPLC value %d ms (for detected line frequency %d Hz is %s)\n',comment_IVL, nplc_value, Keithley.freq, nplc_string_value); 
	   comment_IVL = sprintf('%s#\n#\n',comment_IVL);
	   
       val = pulsed_popup.Value;
       mode = pulsed_popup.String;
       if strcmp(mode(val), 'continuous')
        comment_IVL = sprintf('%s#Continuous operation of the source\n#\n#\n',comment_IVL);   
	   elseif strcmp(mode(val), 'pulsed')	
		comment_IVL = sprintf('%s#Pulse operation of the source with delays of %s s\n#\n#\n',comment_IVL, pulse_delay);
       elseif strcmp(mode(val), 'mixed')
        comment_IVL = sprintf('%s#Mixed operation of the source with delays of %s s\n',comment_IVL, pulse_delay);   
        comment_IVL = sprintf('%s#NPLC value for continuous operation arm %d ms (for detected line frequency %d Hz is %s)\n',comment_IVL, mixed_nplc, Keithley.freq, mixed_nplc_string); 
        if strcmp(Keithley.type, 'v')
            comment_IVL = sprintf('%s#Limit for continuous operation arm %s %s and %s %s\n',comment_IVL, get(mixed_limit_edit,'String'), get(mixed_limit_units,'String'), get(end_edit,'String'), get(end_units,'String'));
        else
            comment_IVL = sprintf('%s#Limit for continuous operation arm %s %s and %s %s\n',comment_IVL, get(end_edit,'String'), get(end_units,'String'), get(mixed_limit_edit,'String'), get(mixed_limit_units,'String'));
        end    
	   end	
	   comment_IVL = sprintf('%s#\n#\n',comment_IVL);
	   
	   if ~strcmp(set_backVoltage,'off')
         comment_IVL = sprintf('%s#Back voltage to PD %s V\n',comment_IVL, set_backVoltage);
       else
         comment_IVL = sprintf('%s#\n',comment_IVL);   
       end
	   comment_IVL = sprintf('%s#\n#\n',comment_IVL);	
		
       comment_IVL = sprintf('%s#Comment: %s\n',comment_IVL, get(edit_Comment, 'String'));
	   comment_IVL = sprintf('%s#\n#\n',comment_IVL);


       comment_IVL = sprintf('%s#Snapshot averaging %d\n',comment_IVL, repeat_value);
       comment_IVL = sprintf('%s#\n#\n',comment_IVL);

       if Keithley.highC && Keithley.single_ch
	 comment_IVL = sprintf('%s#High capacitance mode is enabled\n',comment_IVL);
       elseif Keithley.highC
	 comment_IVL = sprintf('%s#High capacitance mode is enabled for both channels\n',comment_IVL);
       else
	 comment_IVL = sprintf('%s#High capacitance mode is disabled (normal operation)\n',comment_IVL);
       end
	   
	   comment_IVL = sprintf('%s#\n#\n#\n#\n#\n#\n#\n#\n#\n#\n',comment_IVL);

       if Keithley.single_ch
         comment_IVL = sprintf('%s#\n',comment_IVL);
       else
         if Keithley.sense_drain
           comment_IVL = sprintf('%s#Drain sense follows source \n',comment_IVL);
         else
           comment_IVL = sprintf('%s#Drain uses local sense (i.e. 2 probe measurement)\n',comment_IVL);
         end
       end

       if senseSelectArray == [false, true]
         comment_IVL = sprintf('%s#Both 2 and 4 wire measurements\n',comment_IVL);
	   elseif senseSelectArray == [false]
	     comment_IVL = sprintf('%s#2 wire measurements\n',comment_IVL);
	   else  
         comment_IVL = sprintf('%s#4 wire measurements\n',comment_IVL);
	   end 

       headerLine = '';
       if size(senseSelectArray,2)==2
         add_pr = {'_4pr','_2pr'};
		 pr_cnt = 1;
	   else
         add_pr = {'',''};
		 pr_cnt = 2;
	   end 
   
       if singleCh_value
         add_src={'',''};
		 ch_cnt = 2;
		 ch_cnt_init = 2;
	   else 
		 add_src={'S','D'};
		 ch_cnt = 1;
		 ch_cnt_init = 1;
	   end	 
	
       val = pulsed_popup.Value;
       mode = pulsed_popup.String;
       if strcmp(mode(val), 'mixed')
           add_mx = {'_puls','_cont'};
           mx_cnt = 1;
           mx_cnt_init = 1;
       else
           add_mx = {'',''};
           mx_cnt = 2;
           mx_cnt_init = 2;
       end  
	
       while pr_cnt<=2
	    while mx_cnt<=2
	     while ch_cnt <=2
		   headerLine = sprintf('%sI%s%s%s, V%s%s%s, ', headerLine, add_src{ch_cnt},add_pr{pr_cnt}, add_mx{mx_cnt}, add_src{ch_cnt},add_pr{pr_cnt},add_mx{mx_cnt});
		   ch_cnt = ch_cnt+1;
         end  
           ch_cnt = ch_cnt_init;
           headerLine = sprintf('%sExpTime%s%s, Value%s%s',headerLine, add_pr{pr_cnt}, add_mx{mx_cnt}, add_pr{pr_cnt},add_mx{mx_cnt});
		   mx_cnt = mx_cnt + 1;
		   if mx_cnt<=2
		     headerLine = sprintf('%s, ',headerLine);
           end 
        end
        mx_cnt = mx_cnt_init;
        pr_cnt = pr_cnt + 1;
		if pr_cnt<=2
		     headerLine = sprintf('%s, ',headerLine);
        end
       end 
       comment_IVL = sprintf('%s%s\n', comment_IVL, headerLine);
       
      end 
	   %%%%%%%%% end of header for IVL *.dat file  
   
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% loops for 2 vs 4 wire
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% measurements and
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% mixed/cont/pulsed
    output_data_sweep = [];
    output_data_IVL = [];
    if strcmp(mode(val), 'continuous')
        cont_puls_array = [0];
        nplc_array = {nplc_string_value};
        limit_array = {limit_value};
    elseif strcmp(mode(val), 'pulsed')
        cont_puls_array = [1];
        nplc_array = {nplc_string_value};
        limit_array = {limit_value};
    elseif strcmp(mode(val), 'mixed')    
        cont_puls_array = [0,1];
        nplc_array = {mixed_nplc_string, nplc_string_value};
        limit_array = {mixed_limit, limit_value};
    end    
    for senseSelect = senseSelectArray
     for cont_puls = cont_puls_array  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% add core functionality here
 index = find(cont_puls_array == cont_puls);
 Keithley.nplc = nplc_array{index};
 Keithley.limit = limit_array{index};
 Keithley.sense =  senseSelect;
 if ini.senseDrain_value
   Keithley.sense_drain = Keithley.sense;
 else  
   Keithley.sense_drain = false;
 end  
 if cont_puls == 0
     cont_puls = 'off';
     Keithley.pulse = 'off';
 else
     cont_puls = 'pulsed';
     Keithley.pulse = pulse_delay;
 end   
 
 
  % IV - IV data from Keithlei both channels A (to TPX LED) and B (to TPX PD)
 currenta = 1; %position of I in IV setsmu array
 voltagea = 2; %position of V in IV setsmu array
 currentb = 3; %position of I in IV readsmu array
 voltageb = 4; %position of V in IV readsmu array
 IVpos_start = 1;
 wvlPos = 1;
 spectrumPos = 2;
 wvlPosDark = 3;
 spectrumPosDark = 4;
 if singleCh_value
   expTimePos = 3;
   averValuePos = 4;
   IVpos_end = 2;
 else
   expTimePos = 5;
   averValuePos = 6;
   IVpos_end = 4;
 end 

 %%%% start of sweepIV
 IV_sweep = [];
 if Keithley.single_ch 
   KeithleyInitSingleCh(Keithley);
   result_handles.resultTR_handle = updatePlotTitle(result_handles.resultTR_handle, 'I-V', 'Voltage (V)', 'Current (A)');
   IV_sweep = KeithleyRunSingleChSweep(Keithley);
   if checkRunning(Keithley)
     return;
   end
   result_handles.resultTR_handle = updatePlotTitle(result_handles.resultTR_handle, 'I-V', 'Voltage (V)', 'Current (A)');
   result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, IV_sweep(:,voltagea), IV_sweep(:,currenta),'-^');
 else
   KeithleyInitDualCh(Keithley);  
   result_handles.resultTR_handle = updatePlotTitle(result_handles.resultTR_handle, 'I-V Source', 'Voltage (V)', 'Current (A)');
   result_handles.resultBL_handle = updatePlotTitle(result_handles.resultBL_handle, 'I-V Drain', 'Voltage (V)', 'Current (A)');
   result_handles.resultBR_handle = updatePlotTitle(result_handles.resultBR_handle, 'I_S / I_D', 'Voltage source (V)', 'I_S / I_D');   
   IV_sweep = KeithleyRunDualChSweep(Keithley);
   if checkRunning(Keithley)
     return;
   end
   result_handles.resultTR_handle = updatePlotTitle(result_handles.resultTR_handle, 'I-V Source', 'Voltage (V)', 'Current (A)');
   result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, IV_sweep(:,voltagea), IV_sweep(:,currenta),'-^');
   result_handles.resultBL_handle = updatePlotTitle(result_handles.resultBL_handle, 'I-V Drain', 'Voltage (V)', 'Current (A)');
   result_handles.resultBL_handle = plotAddNewCurve(result_handles.resultBL_handle, IV_sweep(:,voltageb), IV_sweep(:,currentb),'-^');
   result_handles.resultBR_handle = updatePlotTitle(result_handles.resultBR_handle, 'I_S / I_D', 'Voltage source (V)', 'I_S / I_D');
   result_handles.resultBR_handle = plotAddNewCurve(result_handles.resultBR_handle, IV_sweep(:,voltagea), IV_sweep(:,currentb)./IV_sweep(:,currentb),'-^');
 end    
 %%%%end of sweepIV
 
 %%% save and PostProc sweepIV
 
    if isempty(output_data_sweep)  
         output_data_sweep = IV_sweep;
        else    
         output_data2 = IV_sweep;
		 output_data_sweep = padding(output_data_sweep, output_data2);
     end
   savedatatofile(strcat(pathToSaveResult,save_filename,'.dat'), comment, output_data_sweep);
   try
    if ~exist('fit_handle')
        fit_handle = IVanalysis(pathToSaveResult, strcat(save_filename,'.dat'),'');
    else    
        fit_handle = IVanalysis(pathToSaveResult, strcat(save_filename,'.dat'),fit_handle);
    end
   catch
    disp('Error in PostProc analysis. Check data');
    % rethrow(error)
   end
 %%%end of save and PostProc sweepIV
 
 %%% set dummies for autosave
 
 if useSpectra_value
     spectra_curves = {};
     spectra = []; end    
 
  if useDLT_value
     DLT_ref = {};
     DLT_out = {};
 end 
 
 %%% end of set dummies for autosave
 
 %%%%start of sweepIVL 
 if useIVL_value
 
 Keithley_storage.type = Keithley.type;
 Keithley_storage.limit = Keithley.limit;
 if strcmp(IVLSourceType, 'current') && strcmp(Keithley.type, 'v')
   Keithley.type = 'i';
   Keithley.limit = Keithley.end;
 elseif strcmp(IVLSourceType, 'voltage') && strcmp(Keithley.type, 'i')
   Keithley.type = 'v';
   Keithley.limit = Keithley.end;
 end   
     
     
 KeithleyInitSweep(Keithley); 
 IV = [];
 img = [];
 %%%% variables
 % img - array of images
 % time - timestamp of snapshot 
 
 for step = 1:size(ini.IVL_list,1) %counting every step in the measurement
      
   if (strcmp(Keithley.type, Keithley_storage.type) && (Keithley.end<ini.IVL_list{step,1})) || (~strcmp(Keithley.type, Keithley_storage.type) && (Keithley_storage.limit<ini.IVL_list{step,1}))
      step = step - 1;
      break;
   end   

   measure_cnt = 0;
   IV(step, currentb) = 0;
   IV(step, voltageb) = 0;
   IV(step, currenta) = 0;
   IV(step, voltagea) = 0;
   tmpIV = [];
   IV(step,IVpos_start:IVpos_end) = zeros(1,IVpos_end-IVpos_start+1);     
   fprintf(Keithley.handle,strcat(Keithley.source,'.source.level', Keithley.type, ' = ', num2str(ini.IVL_list{step,1})));       
   
   if strcmp(Keithley.pulse,'off')
       fprintf(Keithley.handle,strcat(Keithley.source,'.source.output =', Keithley.source,'.OUTPUT_ON'));
       if ~Keithley.single_ch 
         fprintf(Keithley.handle,strcat(Keithley.drain,'.source.output =', Keithley.drain,'.OUTPUT_ON'));
	   end
       tmpIV = KeithleyGetIV(Keithley);
       if checklimits(Keithley, tmpIV) 
           IV(step,:,:)=[];
           step = step-1;
           break;
       end    
       IV(step,IVpos_start:IVpos_end) = IV(step,IVpos_start:IVpos_end) + tmpIV;
       measure_cnt = 1;
   else
       measure_cnt = 0;
   end 
   
  if checkRunning(Keithley)
    return;
  end  
   
%%%%%%%%%% get working expTime   
   
 if strcmp(ini.IVL_list{step,3},'auto')
 %%%% auto adjust of expTime
    [cam_struct, status] = getAutoExpTime(cam_struct,Keithley);
    if status
       if bitand(status,1)
        return;
       end
       if bitand(status,2)
        IV(step,:,:)=[];
        step = step - 1;   
        break;
       end
    end    
 %%%% end of auto adjust of expTime  
 else
   cam_struct.expTime = ini.IVL_list{step,3};
   try
     set(cam_struct.handle, 'ExposureTime', cam_struct.expTime);
     pause(0.5);
   catch
     set(fig_handle,'CurrentAxes',axes_handle);
     cam_struct = set_cam(cam_struct);
   end
 end    
 
%%%%%%%%%% end of get working expTime

%%%%%%%%%% take images
     img(step,:,:) = zeros(cam_struct.imgSize, cam_struct.imgSize);
     tmpIMG = zeros(cam_struct.imgSize, cam_struct.imgSize);
     for rep = 1:repeat_value
        if checkRunning(Keithley)
          return;
        end
        
       [tmpIV, tmpIMG, status, cam_struct] = getOneIVLStep(cam_struct, Keithley); 
       if status
          if bitand(status,1)
           return;
          end
          if bitand(status,2)
            IV(step,:) =[];
            img(step,:,:) = [];
            step = step - 1;
            break;
          end
       end  
       if ~isempty(tmpIV)
         IV(step,IVpos_start:IVpos_end) = IV(step,IVpos_start:IVpos_end) + tmpIV;
         measure_cnt = measure_cnt + 1;
       end   
       img = addMatrix(img, tmpIMG, step);
     end    
     img(step,:,:) = img(step,:,:)./repeat_value;
%%%%%% end of take mages


%%%%%% take zero img as reference
     if checkRunning(Keithley)
          return;
     end
        
     if strcmp(Keithley.pulse,'off')
       fprintf(Keithley.handle,strcat(Keithley.source,'.source.output =', Keithley.source,'.OUTPUT_OFF'));
	    if ~Keithley.single_ch 
         fprintf(Keithley.handle,strcat(Keithley.drain,'.source.output =', Keithley.drain,'.OUTPUT_OFF'));
	    end 
     end   
     
     tmpIMG = zeros(cam_struct.imgSize, cam_struct.imgSize);
     if ~(ini.ignoreZero_value)
      for rep = 1:repeat_value
       try  
         tmpIMG = tmpIMG + single(snapshot(cam_struct.handle));
       catch
           set(fig_handle,'CurrentAxes',axes_handle);
           cam_struct = set_cam(cam_struct);
           tmpIMG = tmpIMG + single(snapshot(cam_struct.handle));
       end    
       if checkRunning(Keithley)
          return;
       end
     end   
     tmpIMG = tmpIMG./repeat_value;
     end
%%%%%% end of take zero img as reference


     if ini.useFullImg_value
         averValue = mean2(squeeze(img(step,:,:))-tmpIMG(:,:))/cam_struct.expTime;
     else
         averValue = mean2(squeeze(img(step,regionOfInterest_handle(reg_coordY1):regionOfInterest_handle(reg_coordY2),regionOfInterest_handle(reg_coordX1):regionOfInterest_handle(reg_coordX2)))-tmpIMG(regionOfInterest_handle(reg_coordY1):regionOfInterest_handle(reg_coordY2),regionOfInterest_handle(reg_coordX1):regionOfInterest_handle(reg_coordX2)))/cam_struct.expTime;
     end    
     IV(step,currenta) = IV(step,currenta)/measure_cnt;
     IV(step,voltagea) = IV(step,voltagea)/measure_cnt;
     if ~singleCh_value 
       IV(step,currentb) = IV(step,currentb)/measure_cnt;
       IV(step,voltageb) = IV(step,voltageb)/measure_cnt;
     end  
     IV(step, expTimePos) = cam_struct.expTime;
     IV(step, averValuePos) = averValue;
        
     if step == 1
        result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, squeeze(IV(:,voltagea)), squeeze(IV(:,currenta)), '-^');
     else
        result_handles.resultTR_handle = updatePlotCurve(result_handles.resultTR_handle, squeeze(IV(end,voltagea)), squeeze(IV(end,currenta))); 
     end
         
     result_handles.resultBL_handle = updatePlotTitle(result_handles.resultBL_handle, 'Lum-V', 'Voltage (V)', 'Lum (a.u.)');
     result_handles.resultBL_handle = plotAddNewCurve(result_handles.resultBL_handle, squeeze(IV(:,voltagea)), squeeze(IV(:,averValuePos)), '-o');
     
     result_handles.resultBR_handle = updatePlotTitle(result_handles.resultBR_handle, 'Lum-I', 'Current (A)', 'Lum (a.u.)');
     result_handles.resultBR_handle = plotAddNewCurve(result_handles.resultBR_handle, squeeze(IV(:,currenta)), squeeze(IV(:,averValuePos)), '-o');
 
     
 if get(useAutoSave_checkbox, 'Value') && get(saveFull_checkbox, 'Value')
   if autoSave_value <= diff(datenum([ONtime;datetime('now')]))*24*60
      ONtime = datetime('now');
      saveFullData;
   end   
 end  
     
 end
 Keithley.type = Keithley_storage.type;
 Keithley.limit = Keithley_storage.limit;
 clearvars Keithley_storage;
 end
 if exist('step')
  step_IVL_final = step;
 end 
 
 if useSpectra_value
   
 Keithley_storage.type = Keithley.type;
 Keithley_storage.limit = Keithley.limit;
 if strcmp(spectraSourceType, 'current') && strcmp(Keithley.type, 'v')
   Keithley.type = 'i';
   Keithley.limit = Keithley.end;
 elseif strcmp(spectraSourceType, 'voltage') && strcmp(Keithley.type, 'i')
   Keithley.type = 'v';
   Keithley.limit = Keithley.end;
 end      
     
   KeithleyInitSweep(Keithley); 
   spectra = [];
   
   for step = 1:size(ini.Spectra_list,1) %counting every step in the measurement

  if (strcmp(Keithley.type, Keithley_storage.type) && (Keithley.end<ini.Spectra_list{step,1})) || (~strcmp(Keithley.type, Keithley_storage.type) && (Keithley_storage.limit<ini.Spectra_list{step,1}))
      step = step - 1;
      break;
   end      
       
       
   measure_cnt = 0;
   spectra(step, currentb) = 0;
   spectra(step, voltageb) = 0;
   spectra(step, currenta) = 0;
   spectra(step, voltagea) = 0;
   
   tmpIV = [];
   spectra(step,IVpos_start:IVpos_end) = zeros(1,IVpos_end-IVpos_start+1);
   fprintf(Keithley.handle,strcat(Keithley.source,'.source.level', Keithley.type, ' = ', num2str(ini.Spectra_list{step,1})));       
   
   if strcmp(Keithley.pulse,'off')
       fprintf(Keithley.handle,strcat(Keithley.source,'.source.output =', Keithley.source,'.OUTPUT_ON'));
       if ~Keithley.single_ch 
         fprintf(Keithley.handle,strcat(Keithley.drain,'.source.output =', Keithley.drain,'.OUTPUT_ON'));
	   end
       tmpIV = KeithleyGetIV(Keithley);
       if checklimits(Keithley, tmpIV)
           step = step - 1;
           break;
       end    
       spectra(step,IVpos_start:IVpos_end) = spectra(step,IVpos_start:IVpos_end) + tmpIV;
       measure_cnt = 1;
   else
       measure_cnt = 0;
   end 
   
  if checkRunning(Keithley)
    return;
  end  
   
%%%%%%%%%% get working integration Time   
   
 if strcmp(ini.Spectra_list{step,3},'auto')
 %%%% auto adjust of integration Time 
    [spmeter,status] = getAutoIntTime(Keithley,spmeter);
    if status
       if bitand(status,1)
        return;
       end
       if bitand(status,2)
        spectra(step,:,:)=[];
        step = step - 1;   
        break;
       end
    end    
 %%%% end of auto adjust of expTime  
 else
   spmeter.time = ini.Spectra_list{step,3};
 end    
 getSingleSpectrum(spmeter.time,1, spmeter.device);
%%%%%%%%%% end of get get working integration Time  

%%%%%%%%%% take images


       [tmpIV, spectrum, wvl, status] = getOneSpectraStep(Keithley, spmeter);
       if status
          if bitand(status,1)
           return;
          end
          if bitand(status,2)
            spectra(step,:) =[];
            step = step - 1;
            break;
          end
       end  
       if ~isempty(tmpIV)
         spectra(step,IVpos_start:IVpos_end) = spectra(step,IVpos_start:IVpos_end) + tmpIV;
         measure_cnt = measure_cnt + 1;
       end   

%%%%%% end of take mages


     if checkRunning(Keithley)
          return;
     end
             
     if strcmp(Keithley.pulse,'off') && (((ini.darkSpectrumStep_value || step == 1) && ini.darkSpectrum_value) || step == size(ini.Spectra_list,1))
       fprintf(Keithley.handle,strcat(Keithley.source,'.source.output =', Keithley.source,'.OUTPUT_OFF'));
	    if ~Keithley.single_ch 
         fprintf(Keithley.handle,strcat(Keithley.drain,'.source.output =', Keithley.drain,'.OUTPUT_OFF'));
	    end 
     end   
     
   %%%%%%% get dark spectrum
   if  ini.darkSpectrum_value &&  (step == size(ini.Spectra_list,1) || step ==1 || ini.darkSpectrumStep_value)
      [wvlDark, spectrumDark] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
      spectra_curves{step,wvlPosDark} = wvlDark;
      spectra_curves{step,spectrumPosDark} = spectrumDark;
      spectrumDark = spectrumDark./spmeter.time;
   end
   %%%%%%% end of get dark spectrum
     
     
%%%%%%% save data
       
     spectra(step,currenta) = spectra(step,currenta)/measure_cnt;
     spectra(step,voltagea) = spectra(step,voltagea)/measure_cnt;
     if ~singleCh_value 
       spectra(step,currentb) = spectra(step,currentb)/measure_cnt;
       spectra(step,voltageb) = spectra(step,voltageb)/measure_cnt;
     end  
     spectra(step, expTimePos) = spmeter.time;

     if ini.spectralROIFull
       if ini.darkSpectrum_value      
         spectra(step, averValuePos) = max(spectrum./spmeter.time - spectrumDark);
       else
         spectra(step, averValuePos) = max(spectrum)./spmeter.time;
       end  
     else
       ROIindex = find(wvl>=startSpectralROI_value & wvl<=endSpectralROI_value);
       if ini.darkSpectrum_value      
         spectra(step, averValuePos) = max(spectrum(ROIindex)./spmeter.time - spectrumDark(ROIindex));
       else
         spectra(step, averValuePos) = max(spectrum(ROIindex))./spmeter.time;
       end 
     end    
     spectra_curves{step,wvlPos} = wvl;
     spectra_curves{step,spectrumPos} = spectrum;
        
     if step == 1
        result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, squeeze(spectra(:,voltagea)), squeeze(spectra(:,currenta)), '-x');
     else
        result_handles.resultTR_handle = updatePlotCurve(result_handles.resultTR_handle, squeeze(spectra(end,voltagea)), squeeze(spectra(end,currenta))); 
     end
     
     if (~useIVL_value)&&(step == 1)
         result_handles.resultBL_handle = updatePlotTitle(result_handles.resultBL_handle, 'Lum-V', 'Voltage (V)', 'Lum (a.u.)');
     end    
     
     if step == 1
        result_handles.resultBL_handle = plotAddNewCurve(result_handles.resultBL_handle, squeeze(spectra(:,voltagea)), squeeze(spectra(:,averValuePos)), '-x');
     else
        result_handles.resultBL_handle = updatePlotCurve(result_handles.resultBL_handle, squeeze(spectra(end,voltagea)), squeeze(spectra(end,averValuePos))); 
     end 
     
     result_handles.resultBR_handle = updatePlotTitle(result_handles.resultBR_handle, 'Spectrum', 'Wavelength (nm)', 'Intensity (a.u.)');
     result_handles.resultBR_handle = plotAddNewCurve(result_handles.resultBR_handle, wvl, spectrum, '-o');
     %%%%%%%%%%% save single spectum in dat file here
    
     if get(useAutoSave_checkbox, 'Value') && get(saveFull_checkbox, 'Value')
      if autoSave_value <= diff(datenum([ONtime;datetime('now')]))*24*60
        ONtime = datetime('now');
        saveFullData;
      end   
     end
     
   end
 Keithley.type = Keithley_storage.type;
 Keithley.limit = Keithley_storage.limit;
 clearvars Keithley_storage;
 end
 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%   DLT use
  if useDLT_value
  
  DLT_IV_pos = 1;    
  DLT_wvl_pos = 2;
  DLT_spectrum_pos = 3;
  DLTref_IV_pos = 4;
  DLTref_wvl_pos = 5;
  DLTref_spectrum_pos = 6; 
  
 Keithley_storage.type = Keithley.type;
 Keithley_storage.limit = Keithley.limit;
 if strcmp(DLTSourceType, 'current') && strcmp(Keithley.type, 'v')
   Keithley.type = 'i';
   Keithley.limit = Keithley.end;
 elseif strcmp(DLTSourceType, 'voltage') && strcmp(Keithley.type, 'i')
   Keithley.type = 'v';
   Keithley.limit = Keithley.end;
 end      
     
   KeithleyInitSweep(Keithley); 
   DLT_ref = {};
   fprintf(Keithley.handle,strcat(Keithley.source,'.source.level', Keithley.type, ' = ', num2str(DLTref_value)));       
   fprintf(Keithley.handle,strcat(Keithley.source,'.source.output =', Keithley.source,'.OUTPUT_ON'));
       if ~Keithley.single_ch 
         fprintf(Keithley.handle,strcat(Keithley.drain,'.source.output =', Keithley.drain,'.OUTPUT_ON'));
       end
   for rep = 1:DLTrepeat_value
       waitStartTime = datetime('now');
       disp(strcat('Reference measurement: rep ', num2str(rep),' at ',string(datetime('now'))));
       
       
       %%%%%%%%%% get working integration Time   
   
         if strcmp(DLTrefTime_value,'auto')
         %%%% auto adjust of integration Time 
           [spmeter,status] = getAutoIntTime(Keithley,spmeter);
           if status
             if bitand(status,1)
              return;
             end
             if bitand(status,2)
              if rep == 1
                  DLT_ref = NaN;
              else    
                  DLT_ref = DLT_ref([1:rep-1],:);
              end    
              rep = rep - 1;   
              break;
             end
           end    
         %%%% end of auto adjust of expTime  
         else
          spmeter.time = str2num(DLTrefTime_value);
         end    
         getSingleSpectrum(spmeter.time,1, spmeter.device);
       %%%%%%%%%% end of get get working integration Time  
       
       
       DLTtest = {}; %% to check stabilization time
       test_cnt = 1; %% to check stabilization time
       while DLTstabilization_value > diff(datenum([waitStartTime;datetime('now')]))*24*60
         pause(10);
         if checkRunning(Keithley)
          return;
         end
        
         tmpIV = KeithleyGetIV(Keithley); %% to check stabilization time
         if checklimits(Keithley, tmpIV) %% to check stabilization time
           rep = rep - 1; %% to check stabilization time
           break; %% to check stabilization time
         end    %% to check stabilization time
         DLTtest{test_cnt,DLT_IV_pos} = tmpIV; %% to check stabilization time
         [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);%% to check stabilization time
         DLTtest{test_cnt,DLT_wvl_pos} = wvl;%% to check stabilization time
         DLTtest{test_cnt,DLT_spectrum_pos} = spectrum;%% to check stabilization time
         test_cnt = test_cnt+1;%% to check stabilization time
       end
       
         save(strcat(pathToSaveResult,'ref_rep',num2str(rep),'.mat'), 'DLTtest'); %% to check stabilization time
         clearvars DLTtest test_cnt; %% to check stabilization time
       
       tmpIV = KeithleyGetIV(Keithley);
       if checklimits(Keithley, tmpIV)
           rep = rep - 1;
           break;
       end    
       DLT_ref{rep,DLT_IV_pos} = tmpIV;
       [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
       DLT_ref{rep,DLT_wvl_pos} = wvl;
       DLT_ref{rep,DLT_spectrum_pos} = spectrum;
       
       if autoSave_value <= diff(datenum([ONtime;datetime('now')]))*24*60
        ONtime = datetime('now');
        saveFullData;
       end  
      
       if checkRunning(Keithley)
          return;
       end
   end    
   
   if rep == DLTrepeat_value
   DLT_out = {};
   for step = 1:size(ini.DLT_list,1) %counting every step in the measurement
 
    if (strcmp(Keithley.type, Keithley_storage.type) && (Keithley.end<ini.DLT_list{step,1})) || (~strcmp(Keithley.type, Keithley_storage.type) && (Keithley_storage.limit<ini.DLT_list{step,1}))
      step = step - 1;
      break;
    end      
    
    for rep = 1:DLTrepeat_value
    
    fprintf(Keithley.handle,strcat(Keithley.source,'.source.level', Keithley.type, ' = ', num2str(ini.DLT_list{step,1})));       
    
    waitStartTime = datetime('now');
    disp(strcat('DLT measurement: step ', num2str(step), ' rep ', num2str(rep),' at ',string(datetime('now'))));
    
    %%%%%%%%%% get working integration Time   
   
         if strcmp(ini.DLT_list{step,3},'auto')
         %%%% auto adjust of integration Time 
           [spmeter,status] = getAutoIntTime(Keithley,spmeter);
           if status
             if bitand(status,1)
              return;
             end
             if bitand(status,2)
              if step == 1
                  DLT_out = NaN;
              else    
                  DLT_out = DLT_out([1:step-1],:);
              end    
              step = step - 1;   
              break;
             end
           end    
         %%%% end of auto adjust of expTime  
         else
          spmeter.time = ini.DLT_list{step,3};
         end    
         getSingleSpectrum(spmeter.time,1, spmeter.device);
%%%%%%%%%% end of get get working integration Time  
    
       DLTtest = {}; %% to check stabilization time
       test_cnt = 1; %% to check stabilization time

       while DLTstabilization_value > diff(datenum([waitStartTime;datetime('now')]))*24*60
         pause(10);
         if checkRunning(Keithley)
          return;
        end
       tmpIV = KeithleyGetIV(Keithley); %% to check stabilization time
         if checklimits(Keithley, tmpIV) %% to check stabilization time
           rep = rep - 1; %% to check stabilization time
           break; %% to check stabilization time
         end    %% to check stabilization time
         DLTtest{test_cnt,DLT_IV_pos} = tmpIV; %% to check stabilization time
         [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);%% to check stabilization time
         DLTtest{test_cnt,DLT_wvl_pos} = wvl;%% to check stabilization time
         DLTtest{test_cnt,DLT_spectrum_pos} = spectrum;%% to check stabilization time
         test_cnt = test_cnt+1;%% to check stabilization time
       end
       
         save(strcat(pathToSaveResult,'step',num2str(step),'_rep',num2str(rep),'.mat'), 'DLTtest'); %% to check stabilization time
         clearvars DLTtest test_cnt; %% to check stabilization time 
  
       tmpIV = KeithleyGetIV(Keithley);
       if checklimits(Keithley, tmpIV)
           step = step - 1;
           break;
       end    
       DLT_out{step, rep, DLT_IV_pos} = tmpIV;
       
       [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
       DLT_out{step,rep,DLT_wvl_pos} = wvl;
       DLT_out{step,rep,DLT_spectrum_pos} = spectrum;
       
       if checkRunning(Keithley)
          return;
       end
       
       fprintf(Keithley.handle,strcat(Keithley.source,'.source.level', Keithley.type, ' = ', num2str(DLTref_value)));       
       pause(spmeter.time*4/1000); %%%%%% looks like it takes 2 spectra for spmeter to set a proper value, so lets wait for 4 spectra to be on the save side
       if strcmp(DLTrefTime_value,'auto')
         %%%% auto adjust of integration Time 
           [spmeter,status] = getAutoIntTime(Keithley,spmeter);
           if status
             if bitand(status,1)
              return;
             end
             if bitand(status,2)
              if step == 1
                  DLT_out = NaN;
              else    
                  DLT_out = DLT_out([1:step-1],:);
              end    
              step = step - 1;   
              break;
             end
           end    
         %%%% end of auto adjust of expTime  
         else
          spmeter.time = str2num(DLTrefTime_value);
       end    
         getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
%%%%%%%%%% end of get get working integration Time  
       [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
       DLT_out{step,rep,DLTref_wvl_pos} = wvl;
       DLT_out{step,rep,DLTref_spectrum_pos} = spectrum;
       
       tmpIV = KeithleyGetIV(Keithley);
       if checklimits(Keithley, tmpIV)
           step = step - 1;
           break;
       end    
       DLT_out{step, rep, DLTref_IV_pos} = tmpIV;
       
       if autoSave_value <= diff(datenum([ONtime;datetime('now')]))*24*60
        ONtime = datetime('now');
        saveFullData;
       end  
      
       if checkRunning(Keithley)
          return;
       end
         
    end   
  
%%%%%%% plot data ----- to be checked what will be needed to plot
       
        
% % % % %      if step == 1
% % % % %         result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, squeeze(spectra(:,voltagea)), squeeze(spectra(:,currenta)), '-x');
% % % % %      else
% % % % %         result_handles.resultTR_handle = updatePlotCurve(result_handles.resultTR_handle, squeeze(spectra(end,voltagea)), squeeze(spectra(end,currenta))); 
% % % % %      end
% % % % %      
% % % % %      if (~useIVL_value)&&(step == 1)
% % % % %          result_handles.resultBL_handle = updatePlotTitle(result_handles.resultBL_handle, 'Lum-V', 'Voltage (V)', 'Lum (a.u.)');
% % % % %      end    
% % % % %      
% % % % %      if step == 1
% % % % %         result_handles.resultBL_handle = plotAddNewCurve(result_handles.resultBL_handle, squeeze(spectra(:,voltagea)), squeeze(spectra(:,averValuePos)), '-x');
% % % % %      else
% % % % %         result_handles.resultBL_handle = updatePlotCurve(result_handles.resultBL_handle, squeeze(spectra(end,voltagea)), squeeze(spectra(end,averValuePos))); 
% % % % %      end 
% % % % %      
% % % % %      result_handles.resultBR_handle = updatePlotTitle(result_handles.resultBR_handle, 'Spectrum', 'Wavelength (nm)', 'Intensity (a.u.)');
% % % % %      result_handles.resultBR_handle = plotAddNewCurve(result_handles.resultBR_handle, wvl, spectrum, '-o');
%%%%%%%%%%% end of plot data

   end
   end %end of skip if DLT_ref not measured fully
 fprintf(Keithley.handle,strcat(Keithley.source,'.source.output =', Keithley.source,'.OUTPUT_OFF'));
     if ~Keithley.single_ch 
         fprintf(Keithley.handle,strcat(Keithley.drain,'.source.output =', Keithley.drain,'.OUTPUT_OFF'));
     end  
 Keithley.type = Keithley_storage.type;
 Keithley.limit = Keithley_storage.limit;
 clearvars Keithley_storage;
 end
 
 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%   end of DLT use
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% end of core functionality


%%%%%%%%%%%%%% save data

   saveFullData;
     
   if (useIVL_value) 
     if isempty(output_data_IVL)  
         output_data_IVL = IV;
        else    
         output_data2 = IV;
		 output_data_IVL = padding(output_data_IVL, output_data2);
     end
     savedatatofile(strcat(pathToSaveResult,save_filename,'-IVL.dat'), comment_IVL, output_data_IVL); 
   end 
     
%%%%%%%%%%%end of save data
     
     end %%%%cont_plus 
    end %%%% sense select
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  end of
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% loops for 2 vs 4 wire
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% measurements and
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% mixed/cont/pulsed


  end
      
  end 
   running = 0;
   fclose(Keithley.handle);
   setIdleState;
  
   function saveFullData
   
       if get(saveFull_checkbox, 'Value') || ( get(saveFig_checkbox, 'Value') && useIVL_value)
     
     addFileName = '';
     if size(senseSelectArray, 2) > 1 
         if senseSelect
             addFileName=sprintf('%s%s',addFileName,'_4pr');
         else    
             addFileName=sprintf('%s%s',addFileName,'_2pr');
         end
     end
     if size(cont_puls_array, 2) > 1 
         if ~strcmp(cont_puls,'off')
             addFileName=sprintf('%s%s',addFileName,'_puls');
         else    
             addFileName=sprintf('%s%s',addFileName,'_cont');
         end
     end
     
     if ( get(saveFig_checkbox, 'Value') && useIVL_value && step_IVL_final>0)
       tmp_fig = figure('Visible', 'off');
       imagesc(squeeze(img(step_IVL_final,:,:)));
       saveas(tmp_fig,strcat(pathToSaveResult,save_filename,addFileName,'.jpg'));
       delete(tmp_fig);
     end  
     
     if get(saveFull_checkbox, 'Value')
      if ~exist(strcat(pathToSaveResult,save_filename,'.mat'), 'file')
           save(strcat(pathToSaveResult,save_filename,'.mat'), 'ini');
      end   
      if useIVL_value
       newName = strcat('IVL',addFileName);
       a.(newName)=IV;    
       newName = strcat('img',addFileName);
       a.(newName)=img;    
       save(strcat(pathToSaveResult,save_filename,'.mat'),'-append','-struct','a');
       clearvars a newName;
      end 
      if useSpectra_value
       newName = strcat('spectraIV',addFileName);
       a.(newName)=spectra;
       newName = strcat('spectraCurves',addFileName);
       a.(newName)=spectra_curves;
       save(strcat(pathToSaveResult,save_filename,'.mat'),'-append','-struct','a');
       clearvars a newName;
      end 
      if useDLT_value
       newName = strcat('DLT_ref',addFileName);
       a.(newName)=DLT_ref;
       newName = strcat('DLT_out',addFileName);
       a.(newName)=DLT_out;
       save(strcat(pathToSaveResult,save_filename,'.mat'),'-append','-struct','a');
       clearvars a newName;
      end    
       newName = strcat('IVsweep',addFileName);
       a.(newName)=IV_sweep;
       save(strcat(pathToSaveResult,save_filename,'.mat'),'-append','-struct','a');
       clearvars a newName;
     end
     
     end 
   
   end 
   
  function stat = checkRunning(smu)
     stat = 0;
     if running == 0
       fprintf(smu.handle,'smua.source.output = smua.OUTPUT_OFF');  
       fprintf(smu.handle,'smub.source.output = smub.OUTPUT_OFF'); 
       fclose(smu.handle);
       setIdleState;
       stat = 1;
       return;
     end  
  end    
           
  function stat = checklimits(smu, IV)
     stat = 0;
     if (strcmp(smu.type,'v') && (IV(currenta)>=0.98*smu.limit)) || (strcmp(smu.type,'i') && (IV(voltagea)>=0.98*smu.limit))
         stat = 1;
     end
     if ~smu.single_ch
      if strcmp(smu.drainLimit, 'off')
       if strcmp(smu.type,'i')
         drainLimit = smu.end;
       else
         drainLimit = smu.limit;  
       end  
      else
       drainLimit = smu.drainLimit;   
      end    
      if IV(currentb)>=0.98*drainLimit
         stat = 1;  
      end
     end
     if stat
       fprintf(smu.handle,'smua.source.output = smua.OUTPUT_OFF');  
       fprintf(smu.handle,'smub.source.output = smub.OUTPUT_OFF');
     end
     return;
  end 
 
  function [tempIV, tempIMG, out, cam_out] = getOneIVLStep(cam, smu)
     out = 0; 
     if ~strcmp(smu.pulse,'off')
         [tempIV, tempIMG, stat] = getPulseSnapshot(cam, smu);
         if stat
           set(fig_handle,'CurrentAxes',axes_handle);
           cam = set_cam(cam);
           [tempIV, tempIMG, ~] = getPulseSnapshot(cam, smu);
         end
         if checklimits(smu, tempIV)
             out = 2;
             cam_out = cam;
             return;
         end    
     else
         try
           tempIMG = single(snapshot(cam.handle));
         catch
           set(fig_handle,'CurrentAxes',axes_handle);
           cam = set_cam(cam);
           tempIMG = single(snapshot(cam.handle));
         end 
         tempIV = KeithleyGetIV(smu);
      end 
     cam_out = cam;
  end
  
    function [tempIV, spectrum, wvl, out] = getOneSpectraStep(smu, spmeter)
     out = 0; 
     if ~strcmp(smu.pulse,'off')
         [tempIV, wvl, spectrum] = getPulseSpectra(smu, spmeter);
         if checklimits(smu, tempIV)
             out = 2;
             return;
         end    
     else
         [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
         tempIV = KeithleyGetIV(smu);
      end 
  end
  
  
   
 function [spmeter, status] = getAutoIntTime(smu,spmeter)
   
     status = 0;
   
     for intTime = intTimeSwap  
       spmeter.time = intTime;
       getSingleSpectrum(spmeter.time,1, spmeter.device);
       if checkRunning(smu)
        status = 1;
        return;
       end    
     
    [~, spec, ~, status] = getOneSpectraStep(smu, spmeter);
    
    status = status + checkRunning(smu);
    if status
       return
    end   
          
      maxValue =  max(spec);
      if maxValue>=60000
        break  
      end  
    end
    difTime = round(intTime/10);
     while (((spmeter.time-difTime)>1) && (maxValue>=50000))
        spmeter.time = spmeter.time-difTime;
        getSingleSpectrum(spmeter.time,1, spmeter.device);
       if checkRunning(smu)
         status = 1;
         return;
       end
        
       [~, spec, ~, status] = getOneSpectraStep(smu, spmeter); 
       
       status = status + checkRunning(smu);
       if status
         return;
       end  
        maxValue =  max(spec);             
     end
  end 
  
  
  
  function [out, status] = getAutoExpTime(cam,smu)
   
     status = 0;
     out = cam;
      
     for expTime = expTimeSwap
      cam.expTime = expTime;   
      try
       set(cam.handle, 'ExposureTime', expTime);
       pause(0.5);
      catch
       set(fig_handle,'CurrentAxes',axes_handle);
       cam = set_cam(cam);
      end
 
    if checkRunning(smu)
        status = 1;
        return;
    end    
     
    [~, tempIMG, status, cam] = getOneIVLStep(cam, smu);
    
    status = status + checkRunning(smu);
    if status
       out = cam;
       return
    end   
          
      maxValue =  max(max(tempIMG));
      if maxValue>=220
        break  
      end  
    end
    difexptime = round(expTime/10);
     while (((expTime-difexptime)>1) && (maxValue>=220))
        expTime = expTime-difexptime;
        cam.expTime = expTime;
        try
         set(cam.handle, 'ExposureTime', expTime);
         pause(0.5);
        catch
         set(fig_handle,'CurrentAxes',axes_handle);
         cam = set_cam(cam);
        end
        
       if checkRunning(smu)
         status = 1;
         return;
       end
        
       [~, tempIMG, status, cam] = getOneIVLStep(cam, smu); 
       
       status = bitand(status,checkRunning(smu));
       if status
        out = cam;
        return
       end 
       
       maxValue =  max(max(tempIMG));
                  
     end
     cam.expTime = expTime;
     out = cam;
  end
   
   function out_array = padding(in_array1, in_array2)
     if size(in_array1,1)>size(in_array2,1)
          outputsize = size(in_array2,1);
          for addrow = outputsize + 1:size(in_array1,1)
            in_array2(addrow,:) = in_array2(outputsize,:);
          end
     elseif size(in_array1,1)<size(in_array2,1)  
          outputsize = size(in_array1,1);
          for addrow = outputsize + 1:size(in_array2,1)
            in_array1(addrow,:) = in_array1(outputsize,:);
          end  
     end
     out_array = [in_array2,in_array1];   
   end 
   
   function setRunningState
      
     set(X_setPos, 'Enable', 'off');
	 set(Y_setPos, 'Enable', 'off');
	 set(Z_setPos, 'Enable', 'off');
	 set(updateButton, 'Enable', 'off');  
     set(moveButton, 'Enable', 'off'); 
	 set(loadMask_edit, 'Enable', 'off');
	 set(loadMask_Button, 'Enable', 'off');
	 set(newCalibrationButton, 'Enable', 'off');
	 set(gotoButton, 'Enable', 'off');
	 set(addCalib_edit, 'Enable', 'off');
	 set(addcalib_Button, 'Enable', 'off');
	 set(calibration_table, 'Enable', 'off');
     set(set_goto,  'Enable', 'off');
	 
	 set(source_popup, 'Enable', 'off');
	 set(type_popup, 'Enable', 'off');
	 set(steps_edit, 'Enable', 'off');
	 set(repeat_edit, 'Enable', 'off');
	 set(start_edit, 'Enable', 'off');
	 set(end_edit, 'Enable', 'off');
	 set(limit_edit, 'Enable', 'off');
	 set(measurement_popup, 'Enable', 'off'); 
	 set(measurement_duration_edit, 'Enable', 'off'); %%%requires callback 
	 set(measurement_nplc_edit, 'Enable', 'off');
	 set(pulsed_popup, 'Enable', 'off');
	 set(pulsed_duration_edit, 'Enable', 'off');%%%requires callback 
	 set(mixed_limit_edit, 'Enable', 'off');%%%requires callback 
	 set(mixed_nplc_edit, 'Enable', 'off');%%%requires callback 
	 set(back_checkbox, 'Enable', 'off');
	 set(backStart_edit, 'Enable', 'off'); %%%requires callback 
	 set(backEnd_edit, 'Enable', 'off'); %%%requires callback 
	 set(backLimit_edit, 'Enable', 'off'); %%%requires callback 
	 set(backStep_edit, 'Enable', 'off'); %%%requires callback 
	 set(highC_checkbox, 'Enable', 'off');
	 set(sweep_checkbox, 'Enable', 'off');
	 set(sense_popup, 'Enable', 'off');
	 set(sense_drainCheckbox, 'Enable', 'off');
	 set(singleCh_checkbox, 'Enable', 'off');
	 
     set(edit_img_size, 'Enable', 'off');
     set(edit_img_offset, 'Enable', 'off');
     set(checkbox_imgX, 'Enable', 'off');
     set(checkbox_imgY, 'Enable', 'off');
     set(edit_setExpTime, 'Enable', 'off');
	 set(button_setcontrols, 'Enable', 'off');
	 set(ExpTime_popup, 'Enable', 'off');
	 set(edit_ExpTime_list, 'Enable', 'off');  %%%requires callback
	 set(button_ExpTime, 'Enable', 'off');  %%%requires callback
	 set(edit_repeat_img, 'Enable', 'off'); 
     set(addZoneButton, 'Enable', 'off');  %%%requires callback
	 set(clearZoneButton, 'Enable', 'off');  %%%requires callback
     set(useFullImg_checkbox, 'Enable', 'off'); 
  
     set(checkbox_useSpec, 'Enable', 'off');
     set(selectSpec_popup, 'Enable', 'off'); %%%requires callback
     set(edit_specAver, 'Enable', 'off'); %%%requires callback
     set(edit_intTime, 'Enable', 'off'); %%%requires callback
     set(button_getSpectrum, 'Enable', 'off'); %%%requires callback
	 set(button_startSpecPreview, 'Enable', 'off'); %%%requires callback
	 set(button_stopSpecPreview, 'Enable', 'off'); %%%requires callback
	 set(IntTime_popup, 'Enable', 'off'); %%%requires callback
	 set(edit_intTime_list, 'Enable', 'off'); %%%requires callback
	 set(button_intTime, 'Enable', 'off'); %%%requires callback
     set(edit_startSpectralROI, 'Enable', 'off'); %%%requires callback
     set(edit_endSpectralROI, 'Enable', 'off'); %%%requires callback
     set(checkbox_fullROI, 'Enable', 'off'); %%%requires callback
     set(useDarkSpectrum_checkbox, 'Enable', 'off'); %%%requires callback
     set(useDarkSpectrumStep_checkbox, 'Enable', 'off'); %%%requires callback
	 
	 set(ignoreZero_checkbox, 'Enable', 'off'); %%%requires callback
     set(saveFig_checkbox, 'Enable', 'off'); %%%requires callback
     set(saveFull_checkbox, 'Enable', 'off');
     set(usePostProc_checkbox, 'Enable', 'off');
     set(useInProc_checkbox, 'Enable', 'off');
     set(postProc_edit, 'Enable', 'off');  %%%requires callback
     set(inProc_edit, 'Enable', 'off');  %%%requires callback
	 set(postProc_Button, 'Enable', 'off'); %%%requires callback
     set(inProc_Button, 'Enable', 'off'); %%%requires callback
	 set(edit_Comment, 'Enable', 'off');
	 set(open_button, 'Enable', 'off');
	 set(open_dir_button, 'Enable', 'off');
	 set(open_edit, 'Enable', 'off');
	 set(path_edit, 'Enable', 'off'); %%%requires callback
	 set(useSpectra_checkbox, 'Enable', 'off'); %%%requires callback
	 set(useIVL_checkbox, 'Enable', 'off');
	 set(clearIVL_button, 'Enable', 'off'); %%%requires callback
	 set(clearSpectra_button, 'Enable', 'off'); %%%requires callback
	 set(useFullIVL_button, 'Enable', 'off'); %%%requires callback
	 set(useFullSpectra_button, 'Enable', 'off'); %%%requires callback
	 set(addValueIVL_edit, 'Enable', 'off'); %%%requires callback
	 set(addValueSpectra_edit, 'Enable', 'off'); %%%requires callback
     set(addValueIVL_units, 'Enable', 'off'); %%%requires callback
     set(addValueSpectra_units, 'Enable', 'off'); %%%requires callback
	 set(addValueIVL_button, 'Enable', 'off'); %%%requires callback
	 set(addValueSpectra_button, 'Enable', 'off'); %%%requires callback
	 set(IVL_table, 'Enable', 'off'); %%%requires callback
	 set(Spectra_table, 'Enable', 'off'); %%%requires callback
	 set(run_button, 'Enable', 'off');
     set(stop_button, 'Enable', 'on');
     
     set(label_useAutoSave, 'Enable', 'off');
     set(useAutoSave_checkbox, 'Enable', 'off');
     set(autoSave_edit, 'Enable', 'off');
     set(autoSave_units, 'Enable', 'off');
     
     set(label_useDLT, 'Enable', 'off');
     set(useDLT_checkbox, 'Enable', 'off');
     set(clearDLT_button, 'Enable', 'off');
     set(useFullDLT_button, 'Enable', 'off');
     set(addValueDLT_edit, 'Enable', 'off');
     set(addValueDLT_units, 'Enable', 'off');
     set(addValueDLT_button, 'Enable', 'off');
     set(DLT_table, 'Enable', 'off');
     set(label_DLTref, 'Enable', 'off');
     set(DLTref_edit, 'Enable', 'off');
     set(DLTref_units, 'Enable', 'off');
     set(label_DLTstabilization, 'Enable', 'off');
     set(DLTstabilization_edit, 'Enable', 'off');
     set(DLTstabilization_units, 'Enable', 'off');
     set(label_DLTrepeat, 'Enable', 'off');
     set(DLTrepeat_edit, 'Enable', 'off');
     set(label_DLTref_time, 'Enable', 'off');
     set(DLTref_edit_time, 'Enable', 'off');
     
     
     
   end
   
   function setIdleState  
%     set(X_setPos, 'Enable', 'on');
%	 set(Y_setPos, 'Enable', 'on');
%	 set(Z_setPos, 'Enable', 'on');
%	 set(updateButton, 'Enable', 'on');  
%     set(moveButton, 'Enable', 'on'); 
	 set(loadMask_edit, 'Enable', 'on');
	 set(loadMask_Button, 'Enable', 'on');
	 set(newCalibrationButton, 'Enable', 'on');
	 set(gotoButton, 'Enable', 'on');
	 set(addCalib_edit, 'Enable', 'on');
	 set(addcalib_Button, 'Enable', 'on');
	 set(calibration_table, 'Enable', 'on');
%     set(set_goto,  'Enable', 'on');
	 
	 set(source_popup, 'Enable', 'on');
	 set(type_popup, 'Enable', 'on');
	 set(steps_edit, 'Enable', 'on');
	 set(repeat_edit, 'Enable', 'on');
	 set(start_edit, 'Enable', 'on');
	 set(end_edit, 'Enable', 'on');
	 set(limit_edit, 'Enable', 'on');
	 set(measurement_popup, 'Enable', 'on'); 
	 setmeasurement(measurement_popup,NaN);
	 set(measurement_nplc_edit, 'Enable', 'on');
	 set(pulsed_popup, 'Enable', 'on');
     setpulsed(pulsed_popup,NaN);
	 singleCh_Callback(singleCh_checkbox,NaN);
	 backVoltage_Callback(back_checkbox,NaN);
	 set(highC_checkbox, 'Enable', 'on');
	 set(sweep_checkbox, 'Enable', 'on');
	 set(sense_popup, 'Enable', 'on');
	 set(sense_drainCheckbox, 'Enable', 'on');
	 set(singleCh_checkbox, 'Enable', 'on');
	 
%     set(edit_img_size, 'Enable', 'on');
%     set(edit_img_offset, 'Enable', 'on');
%     set(checkbox_imgX, 'Enable', 'on');
%     set(checkbox_imgY, 'Enable', 'on');
%     set(edit_setExpTime, 'Enable', 'on');
%	 set(button_setcontrols, 'Enable', 'on');
%	 set(ExpTime_popup, 'Enable', 'on');
%     expTime_popup_Callback(ExpTime_popup,NaN);
%     set(edit_repeat_img, 'Enable', 'on');	 
%	 set(useFullImg_checkbox, 'Enable', 'on'); 
%	 if ~get(useFullImg_checkbox, 'Value')     
%	   	 set(clearZoneButton, 'Enable', 'on');
%     end	 
  
     set(checkbox_useSpec, 'Enable', 'on');
     useSpectrometer_Callback(checkbox_useSpec,NaN)
	 
     set(saveFull_checkbox, 'Enable', 'on');
     useSaveFull_Callback(saveFull_checkbox,NaN);
     set(usePostProc_checkbox, 'Enable', 'on');
     usePostProc_Callback(usePostProc_checkbox,NaN);
     set(useInProc_checkbox, 'Enable', 'on');
     useInProc_Callback(useInProc_checkbox,NaN);
	 set(edit_Comment, 'Enable', 'on');
	 set(open_button, 'Enable', 'on');
	 set(open_dir_button, 'Enable', 'on');
	 set(open_edit, 'Enable', 'off');
	 sweep_Callback(sweep_checkbox,NaN);
	 
     set(open_edit, 'Enable', 'on');
	 set(useIVL_checkbox, 'Enable', 'on');
     useIVL_Callback(useIVL_checkbox,NaN);
	 set(run_button, 'Enable', 'on');
     set(stop_button, 'Enable', 'off');
   end 
   
   end
     
   function handlerOut = updatePlotTitle(plotHandler, title, Xtitle, Ytitle)
     cla(plotHandler);
     plotHandler.Title.String = title;
     plotHandler.YLabel.String = Ytitle;
     plotHandler.XLabel.String = Xtitle;
     handlerOut = plotHandler;
   end
       
   function handlerOut = updatePlotCurve(plotHandler, Xdata, Ydata)
         hChildren = findobj(plotHandler, 'Type', 'Line');
         set(hChildren(1),'XData',[get(hChildren(1),'XData'), Xdata]);
         set(hChildren(1),'YData',[get(hChildren(1),'YData'), Ydata]);
         handlerOut = plotHandler;
   end
   
   function handlerOut = plotAddNewCurve(plotHandler, Xdata, Ydata, param)
         axes(plotHandler);
         hold on;
         plot(plotHandler, Xdata, Ydata, param);
         handlerOut = plotHandler;
   end
   
   function stopButton_Callback(source,event)
     running = 0;
   end
   
   function output = addMatrix(in1, in2, step)
     for i=1:size(in2,1)
       for j=1:size(in2,2)
           in1(step,i,j) =in1(step,i,j) + in2(i,j);
       end
     end
     output = in1;
   end
   
   function saveinitofile(filename)
      ini.sourcePopup_value = get(source_popup, 'Value');
      ini.typePopup_value =  get(type_popup, 'Value');
      ini.stepsEdit_value = get(steps_edit,'String');
      ini.repeatEdit_value = get(repeat_edit,'String');
      ini.startEdit_value = get(start_edit, 'String');
      ini.endEdit_value = get(end_edit, 'String');
      ini.limitEdit_value = get(limit_edit, 'String');
      ini.measurementPopup_value =  get(measurement_popup, 'Value');
      ini.measurementDurationEdit_value = get(measurement_duration_edit, 'String');
      ini.measurementNPLCEdit_value = get(measurement_nplc_edit, 'String');
      ini.pulsedPopup_value =  get(pulsed_popup, 'Value');
      ini.pulsedDurationEdit_value = get(pulsed_duration_edit, 'String');
      ini.mixedLimitEdit_value = get(mixed_limit_edit, 'String');
      ini.mixedNPLCEdit_value = get(mixed_nplc_edit, 'String');
      ini.backCheckbox_value =  get(back_checkbox, 'Value');
      ini.backStartEdit_value = get(backStart_edit, 'String');
      ini.backEndEdit_value = get(backEnd_edit, 'String');
      ini.backLimitEdit_value = get(backLimit_edit, 'String');
      ini.backStepEdit_value = get(backStep_edit, 'String');
      ini.sweepCheckbox_value =  get(sweep_checkbox, 'Value');
      ini.sensePopup_value =  get(sense_popup, 'Value');
      ini.senseDrain_value =  get(sense_drainCheckbox, 'Value');
      ini.singleChCheckbox_value =  get(singleCh_checkbox, 'Value');
      ini.imgSize_value = str2num(get(edit_img_size, 'String'));
      ini.imgOffset_value = str2num(get(edit_img_offset, 'String'));
      ini.reverseX_value =  get(checkbox_imgX, 'Value');
      ini.reverseY_value =  get(checkbox_imgY, 'Value');
      ini.setExpTime_value = str2num(get(edit_setExpTime, 'String'));
      ini.expTimePopup_value =  get(ExpTime_popup, 'Value');
      ini.expTimeListEdit_value =  get(edit_ExpTime_list, 'String');
      ini.repeatImgEdit_value =  get(edit_repeat_img, 'String');
      ini.commentEdit_value = get(edit_Comment, 'String');
      ini.openEdit_value = get(open_edit, 'String');
      ini.pathEdit_value = get(path_edit, 'String');  
      ini.saveFigCheckbox_value = get(saveFig_checkbox, 'Value');  
      ini.saveFullCheckbox_value = get(saveFull_checkbox, 'Value'); 
      ini.usePostProcCheckbox_value = get(usePostProc_checkbox, 'Value'); 
      ini.useInProcCheckbox_value = get(useInProc_checkbox, 'Value');
      ini.calibration_list = calibration_list;
      ini.ignoreZero_value = get(ignoreZero_checkbox, 'Value');
      ini.useFullImg_value = get(useFullImg_checkbox, 'Value');   
      ini.useIVLCheckbox_value = get(useIVL_checkbox, 'Value');
      ini.setIntTime_value = str2num(get(edit_intTime, 'String'));
      ini.setIntTime_value = str2num(get(edit_intTime, 'String'));
      ini.setSpecAver_value = str2num(get(edit_specAver, 'String'));
      ini.intTimePopup_value = get(IntTime_popup, 'Value');
      ini.expIntListEdit_value = get(edit_intTime_list, 'String');
      ini.highCCheckbox_value =  get(highC_checkbox, 'Value');
      ini.useSpectraCheckbox_value = get(useSpectra_checkbox, 'Value');
      ini.useDLTCheckbox_value = get(useDLT_checkbox, 'Value');
      ini.unitsIVL_value =  get(addValueIVL_units, 'Value');
      ini.unitsSpectra_value =  get(addValueSpectra_units, 'Value');
      ini.unitsDLT_value =  get(addValueDLT_units, 'Value');
      ini.spectralROIStart_value = str2num(get(edit_startSpectralROI, 'String'));
      ini.spectralROIEnd_value = str2num(get(edit_endSpectralROI, 'String'));
      ini.spectralROIFull =  get(checkbox_fullROI, 'Value');
      ini.darkSpectrum_value = get(useDarkSpectrum_checkbox, 'Value');
      ini.darkSpectrumStep_value = get(useDarkSpectrumStep_checkbox, 'Value');
      ini.DLTref_value =  str2num(get(DLTref_edit, 'String'));
      ini.DLTstabilization_value =  str2num(get(DLTstabilization_edit, 'String'));
      ini.DLTrepeat_value =  str2num(get(DLTrepeat_edit, 'String'));
      ini.DLTrefTime_value = get(DLTref_edit_time, 'String');
      ini.useAutoSave_value = get(useAutoSave_checkbox, 'Value');
      ini.autoSave_value =  str2num(get(autoSave_edit, 'String'));
      save(filename, '-struct', 'ini');  
   end 
   
   function iv = KeithleyRunDualChSweep(smu)
     readsteps = smu.steps;
     if ~strcmp(smu.pulse,'off')
         waitDelay = str2num(smu.pulse);
     else
         waitDelay = 1;        
     end  
     fprintf(smu.handle,strcat(smu.source,'.nvbuffer1.clear()'));   
     fprintf(smu.handle,strcat(smu.source,'.nvbuffer2.clear()'));   
     fprintf(smu.handle,strcat(smu.drain,'.nvbuffer1.clear()'));
     fprintf(smu.handle,strcat(smu.drain,'.nvbuffer2.clear()')); 
     fprintf(smu.handle,strcat(smu.source,'.trigger.count =',num2str(smu.steps)));
     fprintf(smu.handle,strcat(smu.source,'.trigger.arm.count =',num2str(smu.repeat)));
     fprintf(smu.handle,strcat(smu.drain,'.trigger.count =',num2str(smu.steps)));
     fprintf(smu.handle,strcat(smu.drain,'.trigger.arm.count =',num2str(smu.repeat)));
     fprintf(smu.handle,strcat('display.',smu.drain,'.measure.func = display.MEASURE_DCAMPS'));
	 fprintf(smu.handle,strcat(smu.source,'.trigger.source.linear',smu.type,'(',num2str(smu.start),',',num2str(smu.end),',',num2str(smu.steps),')'));
     if strcmp(smu.type,'i')
       if strcmp(smu.pulse, 'off') || (abs(smu.start) < 1.5 && abs(smu.end) < 1.5)
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limitv=',num2str(smu.limit)));
        fprintf(smu.handle,strcat(smu.source,'.source.limitv=',num2str(smu.limit)));
       else
        fprintf(smu.handle,'smua.measure.filter.enable = smua.FILTER_OFF');
        fprintf(smu.handle,'smub.measure.filter.enable = smub.FILTER_OFF');
        fprintf(smu.handle,strcat(smu.source,'.source.autorangei =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangev =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangei =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangev =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.measure.rangei = 10'));
        fprintf(smu.handle,strcat(smu.drain,'.measure.rangei = 10')) 
        fprintf(smu.handle,strcat(smu.source,'.source.delay = 100e-6'));
        fprintf(smu.handle,strcat(smu.source,'.measure.autozero =',smu.source,'.AUTOZERO_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.rangei = 10'));
        fprintf(smu.handle,strcat(smu.source,'.source.leveli = 0'));
        fprintf(smu.handle,strcat(smu.source,'.source.limitv = 6'));
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limiti = 10'));   
       end
       fprintf(smu.handle,strcat('display.',smu.source,'.measure.func = display.MEASURE_DCVOLTS'));
     else  
       if strcmp(smu.pulse, 'off')  || abs(smu.limit) < 1.5
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limiti=',num2str(smu.limit)));
        fprintf(smu.handle,strcat(smu.source,'.source.limiti=',num2str(smu.limit)));
       else
        fprintf(smu.handle,'smua.measure.filter.enable = smua.FILTER_OFF');
        fprintf(smu.handle,'smub.measure.filter.enable = smub.FILTER_OFF');
        fprintf(smu.handle,strcat(smu.source,'.source.autorangei =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangev =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangei =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangev =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.measure.rangei = 10'));
        fprintf(smu.handle,strcat(smu.drain,'.measure.rangei = 10')) 
        fprintf(smu.handle,strcat(smu.source,'.source.delay = 100e-6'));
        fprintf(smu.handle,strcat(smu.source,'.measure.autozero =',smu.source,'.AUTOZERO_OFF'));   
        fprintf(smu.handle,strcat(smu.source,'.source.rangev = 6'));
        fprintf(smu.handle,strcat(smu.source,'.source.levelv = 0'));
        fprintf(smu.handle,strcat(smu.source,'.source.limiti = 0.1'));
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limiti = 10'));
       end    
       fprintf(smu.handle,strcat('display.',smu.source,'.measure.func = display.MEASURE_DCAMPS'));
     end  
     if ~strcmp(smu.drainVoltage, 'off')
      fprintf(smu.handle,strcat(smu.drain,'.source.func = ',smu.drain,'.OUTPUT_DCVOLTS'));
      fprintf(smu.handle,strcat(smu.drain,'.source.levelv = ', smu.drainVoltage));
      fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', smu.drainLimit));
	    drainLimitVoltage = str2num(smu.drainLimit);
     else
      fprintf(smu.handle,strcat(smu.drain,'.source.func = ',smu.drain,'.OUTPUT_DCVOLTS'));
      fprintf(smu.handle,strcat(smu.drain,'.source.levelv = 0'));
      %fprintf(smu.handle,strcat(smu.drain,'.source.func = ',smu.drain,'.OUTPUT_DCAMPS'));
      %fprintf(smu.handle,strcat(smu.drain,'.source.leveli = 0'));
      if strcmp(smu.type,'v') && (smu.limit > 1.5)
       fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', num2str(1.5)));  
       drainLimitVoltage = 1.5;
      else 
       fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', num2str(smu.limit))); 
       drainLimitVoltage = smu.limit;
      end 
      if strcmp(smu.type,'i') 
       fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', num2str(smu.end))); 
       drainLimitVoltage = smu.end;
      end  
     end
     fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_ON'));
     fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_ON'));
     fprintf(smu.handle,strcat(smu.drain,'.trigger.initiate()'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.initiate()'));
     pause(waitDelay);
	 buffer_prev = 0;
     while(1)
       if running == 0
         fprintf(smu.handle,strcat(smu.source,'.abort()'));
         fprintf(smu.handle,strcat(smu.drain,'.abort()'));
         iv=[];
         pause(0.5);
         fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_OFF'));
         fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_OFF'));
         return;
       end  
       fprintf(smu.handle,strcat('print(',smu.source,'.nvbuffer2.n)'));
       buffern = str2num(fscanf(smu.handle));
       if buffern>= smu.steps*smu.repeat
           break;
       end
       if buffern>buffer_prev
         fprintf(smu.handle,strcat('printbuffer(',num2str(buffern),', ',num2str(buffern),', ',smu.source,'.nvbuffer1)'));  
         i_tmp_source = str2num(fscanf(smu.handle));
         fprintf(smu.handle,strcat('printbuffer(',num2str(buffern),', ',num2str(buffern),', ',smu.source,'.nvbuffer2)'));  
         v_tmp_source = str2num(fscanf(smu.handle)); 	
		 fprintf(smu.handle,strcat('printbuffer(',num2str(buffern),', ',num2str(buffern),', ',smu.drain,'.nvbuffer1)'));  
		 i_tmp_drain = str2num(fscanf(smu.handle));
         fprintf(smu.handle,strcat('printbuffer(',num2str(buffern),', ',num2str(buffern),', ',smu.drain,'.nvbuffer2)'));  
         v_tmp_drain = str2num(fscanf(smu.handle));
	 
	     if (strcmp(smu.type,'i') && (abs(v_tmp_source)> 0.95*abs(smu.limit)) ) || (strcmp(smu.type,'v') && (abs(i_tmp_source)> 0.95*abs(smu.limit))) || (abs(i_tmp_drain)> 0.95*abs(drainLimitVoltage))
          fprintf(smu.handle,strcat(smu.source,'.abort()'));
		  fprintf(smu.handle,strcat(smu.drain,'.abort()'));
          break;
         end 
		 
		 if buffer_prev == 0
            result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, v_tmp_source, i_tmp_source,'-o');
			result_handles.resultBL_handle = plotAddNewCurve(result_handles.resultBL_handle, v_tmp_drain, i_tmp_drain,'-o');
            if i_tmp_source~=0			
	          result_handles.resultBR_handle = plotAddNewCurve(result_handles.resultBR_handle, v_tmp_source, i_tmp_drain/i_tmp_source,'-o');
			else  
			  result_handles.resultBR_handle = plotAddNewCurve(result_handles.resultBR_handle, v_tmp_source, i_tmp_drain/1e-10,'-o');
			end  
         else
           if buffern > bufreadn
               iv_tmp_buf = [];
               fprintf(smu.handle,strcat('printbuffer(',num2str(buffern-bufreadn),', ',num2str(buffern),', ',smu.source,'.nvbuffer1)'));
               iv_tmp_buf(:,1) = str2num(fscanf(smu.handle));
               fprintf(smu.handle,strcat('printbuffer(',num2str(buffern-bufreadn),', ',num2str(buffern),', ',smu.source,'.nvbuffer2)'));
               iv_tmp_buf(:,2) = str2num(fscanf(smu.handle));
               fprintf(smu.handle,strcat('printbuffer(',num2str(buffern-bufreadn),', ',num2str(buffern),', ',smu.drain,'.nvbuffer1)'));
               iv_tmp_buf(:,3) = str2num(fscanf(smu.handle));
               fprintf(smu.handle,strcat('printbuffer(',num2str(buffern-bufreadn),', ',num2str(buffern),', ',smu.drain,'.nvbuffer2)'));
               iv_tmp_buf(:,4) = str2num(fscanf(smu.handle));
               stop_condition = IVinProc({iv_tmp_buf, save_filename});
               if stop_condition
                  fprintf(smu.handle,strcat(smu.source,'.abort()'));
		          fprintf(smu.handle,strcat(smu.drain,'.abort()'));
                  break;
               end 
           end   
            result_handles.resultTR_handle = updatePlotCurve(result_handles.resultTR_handle, v_tmp_source, i_tmp_source);
			result_handles.resultBL_handle = updatePlotCurve(result_handles.resultBL_handle, v_tmp_drain, i_tmp_drain);
			if i_tmp_source~=0	
			  result_handles.resultBR_handle = updatePlotCurve(result_handles.resultBR_handle, v_tmp_source, i_tmp_drain/i_tmp_source);
			else
              result_handles.resultBR_handle = updatePlotCurve(result_handles.resultBR_handle, v_tmp_source, i_tmp_drain/1e-10);
            end  			
         end 
		 
	     buffer_prev = buffern;
	   
        end
       pause(0.5);
       end
       pause(0.1);
 
       pause(waitDelay*1.2);  
     %%%%in case some additional delays for source/measure action will be
     %%%%used a pause should be added here to prevent Keithley 5042 error
     fprintf(smu.handle,strcat('print(',smu.source,'.nvbuffer2.n)'));
     readsteps = str2num(fscanf(smu.handle));
     fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_OFF'));
     fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_OFF'));
     fprintf(smu.handle,strcat('printbuffer(1, ',num2str(readsteps),', ',smu.source,'.nvbuffer1)'));
     iv(:,1) = str2num(fscanf(smu.handle));
     fprintf(smu.handle,strcat('printbuffer(1, ',num2str(readsteps),', ',smu.source,'.nvbuffer2)'));
     iv(:,2) = str2num(fscanf(smu.handle));
     fprintf(smu.handle,strcat('printbuffer(1, ',num2str(readsteps),', ',smu.drain,'.nvbuffer1)'));
     iv(:,3) = str2num(fscanf(smu.handle));
     fprintf(smu.handle,strcat('printbuffer(1, ',num2str(readsteps),', ',smu.drain,'.nvbuffer2)'));
     iv(:,4) = str2num(fscanf(smu.handle));
    end
   
   function iv = KeithleyRunSingleChSweep(smu)
     % % % Keithley.handle = [];
     % % % Keithley.steps %%int
     % % % Keithley.repeat %%int
     % % % Keithley.start %%int
     % % % Keithley.end %%int
     % % % Keithley.limit %%float
     % % % Keithley.delay %%str "off"/time in sec before measurement
     % % % Keithley.pulse %%str "off"/time in sec pause between pulses
     % % % Keithley.source %%str "smua"/"smub"
     % % % Keithley.drain %%str "smua"/"smub"
     % % % Keithley.type %%str "i"/"v"
     % % % Keithley.drainLimit %% str
     % % % Keithley.freq %% float
     % % % Keithley.drainVoltage %% str "off"/value
     % % % Keithley.nplc %% str
     % % % Keithley.sense %% true/false
     % % % Keithley.sense_drain %% true/false
     % % % Keithley.single_ch %% true/false 
     % % % Keithley.highC %% true/false
     readsteps = smu.steps;
     if ~strcmp(smu.pulse,'off')
         waitDelay = str2num(smu.pulse);
     else
         waitDelay = 1;        
     end 
     fprintf(smu.handle,strcat(smu.source,'.nvbuffer1.clear()'));   
     fprintf(smu.handle,strcat(smu.source,'.nvbuffer2.clear()'));   
     fprintf(smu.handle,strcat(smu.source,'.trigger.count =',num2str(smu.steps)));
     fprintf(smu.handle,strcat(smu.source,'.trigger.arm.count =',num2str(smu.repeat)));
     fprintf(smu.handle,strcat(smu.source,'.trigger.source.linear',smu.type,'(',num2str(smu.start),',',num2str(smu.end),',',num2str(smu.steps),')'));
     if strcmp(smu.type,'i')  
%        if strcmp(smu.pulse, 'off') || (abs(smu.start) < 1.5 && abs(smu.end) < 1.5)
       if (abs(smu.start) < 1.5 && abs(smu.end) < 1.5)
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limitv=',num2str(smu.limit)));
        fprintf(smu.handle,strcat(smu.source,'.source.limitv=',num2str(smu.limit)));
       else
        fprintf(smu.handle,strcat(smu.source,'.measure.filter.enable = ',smu.source,'.FILTER_OFF')); 
        fprintf(smu.handle,strcat(smu.source,'.source.autorangei =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangev =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.delay = 100e-6'));
        fprintf(smu.handle,strcat(smu.source,'.measure.autozero =',smu.source,'.AUTOZERO_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.rangei = 10'));
        fprintf(smu.handle,strcat(smu.source,'.source.leveli = 0'));
        fprintf(smu.handle,strcat(smu.source,'.source.limitv = 6'));
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limiti = 10'));   
       end
       fprintf(smu.handle,strcat('display.',smu.source,'.measure.func = display.MEASURE_DCVOLTS'));
     else  
   %    if strcmp(smu.pulse, 'off')  || abs(smu.limit) < 1.5
       if abs(smu.limit) < 1.5
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limiti=',num2str(smu.limit)));
        fprintf(smu.handle,strcat(smu.source,'.source.limiti=',num2str(smu.limit)));
       else
        fprintf(smu.handle,strcat(smu.source,'.measure.filter.enable = ',smu.source,'.FILTER_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangei =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangev =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.measure.rangei = 10'));
        fprintf(smu.handle,strcat(smu.source,'.source.delay = 100e-6'));
        fprintf(smu.handle,strcat(smu.source,'.measure.autozero =',smu.source,'.AUTOZERO_OFF'));   
        fprintf(smu.handle,strcat(smu.source,'.source.rangev = 6'));
        fprintf(smu.handle,strcat(smu.source,'.source.levelv = 0'));
        fprintf(smu.handle,strcat(smu.source,'.source.limiti = ',num2str(smu.limit)));
        fprintf(smu.handle,strcat(smu.source,'.trigger.source.limiti = ',num2str(smu.limit)));
       end    
       fprintf(smu.handle,strcat('display.',smu.source,'.measure.func = display.MEASURE_DCAMPS'));
     end  
     fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_ON'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.initiate()'));
     pause(waitDelay);
     buffer_prev = 0;
     while(1)
       if running == 0
         fprintf(smu.handle,strcat(smu.source,'.abort()'));
         iv=[];
         pause(0.5);
         fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_OFF'));
         return;
       end  
       fprintf(smu.handle,strcat('print(',smu.source,'.nvbuffer2.n)'));
       buffern = str2num(fscanf(smu.handle));
       if buffern>= smu.steps*smu.repeat
           break;
       end
       if buffern>buffer_prev
           
         fprintf(smu.handle,strcat('printbuffer(',num2str(buffern),', ',num2str(buffern),', ',smu.source,'.nvbuffer1)'));  
         i_tmp = str2num(fscanf(smu.handle));
         fprintf(smu.handle,strcat('printbuffer(',num2str(buffern),', ',num2str(buffern),', ',smu.source,'.nvbuffer2)'));  
         v_tmp = str2num(fscanf(smu.handle));
         
         if buffer_prev == 0
            result_handles.resultTR_handle = plotAddNewCurve(result_handles.resultTR_handle, v_tmp, i_tmp,'-o');
         else
            result_handles.resultTR_handle = updatePlotCurve(result_handles.resultTR_handle, v_tmp, i_tmp);
         end   
         
       if (strcmp(smu.type,'i') && (abs(v_tmp)> 0.95*abs(smu.limit)) ) || (strcmp(smu.type,'v') && (abs(i_tmp)> 0.95*abs(smu.limit))) 
          fprintf(smu.handle,strcat(smu.source,'.abort()'));
          readsteps = buffern;
          break;
       end 
       buffer_prev = buffern;
       
       end
       pause(0.5);
       end
       pause(0.1);
 
       pause(waitDelay*1.2); 
     %%%%in case some additional delays for source/measure action will be
     %%%%used a pause should be added here to prevent Keithley 5042 error
     fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_OFF'));
     fprintf(smu.handle,strcat('printbuffer(1, ',num2str(readsteps),', ',smu.source,'.nvbuffer1)'));
     iv(:,1) = str2num(fscanf(smu.handle))';
     fprintf(smu.handle,strcat('printbuffer(1, ',num2str(readsteps),', ',smu.source,'.nvbuffer2)'));
     iv(:,2) = str2num(fscanf(smu.handle))';
    end 
   
    %end  %%%%%%%%%% end of action Move


 %%%%%%%%%%%
 %%% function that runs sweep and presents results in the way similar to
 %%% probestation
 %%%%%%%%%%%   
 

   %%%%%%%%%%%
   %%% function that recieves motors state information and puts it into a
   %%% readeble array
   %%%%%%%%%%%
   function resp = getresponse(port)
%      fprintf(port,'r\n');
%      pause(delaytime);
%      resp = port.BytesAvailable;
%      if resp > 0 
%        resp = zeros(size(motors,2),size(parameters,2));  
%        for motorNum = 1:size(motors,2)
%           for parameterNum = 1:size(parameters,2)
%               resp(motorNum, parameterNum) = str2double(fgetl(port));
%           end
%        end
%      end 
   end
 
   %%%%%%%%%%%
   %%% get mask map and calibration mapping
   %%%%%%%%%%%
   
    function [name, coord] = getMap(pathToMask)
      name = load(pathToMask,'map_name');
      name =  name.map_name;
      coord = load(pathToMask,'map_coord');
      coord = coord.map_coord;  
    end   
   
    function mapping = calibrationMapping(input)
        for counter = 1:size(input,1)
         [foundX, ~] = find(strcmp(map_name,input(counter,1)));  
         input(counter,2) = {map_coord(foundX,1)};
         input(counter,3) = {map_coord(foundX,2)};
       end  
       mapping = input; 
    end    

    function checked = check_calibration(input)
    %%%% checking if calibration was already done for all lines of calibration_list
    %%%% if not returns the first line to calibrate
    %%%% if calibrated returns 0;
        if isempty(input)
            checked = -1;
            return;
        end    
        if size(input,2)<5
           checked = 1;
           return;
        end
        for counter = 1:size(input,1)
         if isempty(input{counter,4})|| isempty(input{counter,5})
           checked = counter;
           return;
         end  
        end
        checked = 0;
        return;
    end  

    function output = generate_tabledata(input)
      %%%% generates data to display in calibration table
       tab_out = {};
       for counter = 1:size(input,1)
        tab_out {counter,table_struct} = input{counter,1};
        if size(input,2) == 5
         if isempty(input{counter,table_X}) || isempty(input{counter,table_X})
          tab_out {counter,table_calib} = false;
          tab_out {counter,table_X} = NaN;
          tab_out {counter,table_Y} = NaN;
         else
          tab_out {counter,table_calib} = true;  
          tab_out {counter,table_X} = input{counter,4};
          tab_out {counter,table_Y} = input{counter,5};
         end 
        else  
         tab_out {counter,table_calib} = false;
         tab_out {counter,table_X} = NaN;
         tab_out {counter,table_X} = NaN; 
        end
        tab_out {counter,3} = false;
        tab_out {counter,4} = false;
       end 
       output = tab_out;
    end    


   %%%%%%%%%%%
   %%% get transformation
   %%%%%%%%%%%

    function [transformationX, transformationY] = getTransformation(input)
      arg_vector = [ones(size(input,1),1), cell2mat(input(:,2:3))];
      func_vector = cell2mat(input(:,4));
      transformationX = (arg_vector'*arg_vector)\arg_vector' * func_vector;
      func_vector = cell2mat(input(:,5));
      transformationY = (arg_vector'*arg_vector)\arg_vector' * func_vector;      
    end    

   %%%%%%%%%%%
   %%% open port 
   %%%%%%%%%%%
   
   function port = openport(name, rate)
%     port = serial(name);
%     set(port ,'BaudRate', rate);
%     fopen(port);
%     pause(delaytime);
   end
 
   %%%%%%%%%%%
   %%% close port 
   %%%%%%%%%%%
   
   function closeport(port)
%     fclose(port);
   end
 
   %%%%%%%%%%%
   %%% Keithley sweep initialization 
   %%%%%%%%%%%
   #NOTE IMPLEMENT THIS DOTHIS DOTHIS DO THIS DOTHIS DO DO THIS THIS
  function KeithleyInitDualCh(smu)
      
     % % % Keithley.handle = [];
     % % % Keithley.steps %%int
     % % % Keithley.repeat %%int
     % % % Keithley.start %%int
     % % % Keithley.end %%int
     % % % Keithley.limit %%float
     % % % Keithley.delay %%str "off"/time in sec before measurement
     % % % Keithley.pulse %%str "off"/time in sec pause between pulses
     % % % Keithley.source %%str "smua"/"smub"
     % % % Keithley.drain %%str "smua"/"smub"
     % % % Keithley.type %%str "i"/"v"
     % % % Keithley.drainLimit %% str
     % % % Keithley.freq %% float
     % % % Keithley.drainVoltage %% str "off"/value
     % % % Keithley.nplc %% str
     % % % Keithley.sense %% true/false
     % % % Keithley.sense_drain %% true/false
     % % % Keithley.single_ch %% true/false  
     % % % Keithley.highC %% true/false
     
     fprintf(smu.handle,'reset()'); 
     fprintf(smu.handle,'beeper.enable=0');
     fprintf(smu.handle,strcat(smu.source,'.reset()')); 
     fprintf(smu.handle,strcat(smu.drain,'.reset()'));  
     if smu.sense 
         fprintf(smu.handle,strcat(smu.source,'.sense = ',smu.source,'.SENSE_REMOTE'));
     else    
         fprintf(smu.handle,strcat(smu.source,'.sense = ',smu.source,'.SENSE_LOCAL'));
     end
     if (smu.sense_drain) && (smu.sense)
         fprintf(smu.handle,strcat(smu.drain,'.sense = ',smu.drain,'.SENSE_REMOTE'));
     else    
         fprintf(smu.handle,strcat(smu.drain,'.sense = ',smu.drain,'.SENSE_LOCAL'));
     end       
     
     %%%%%%%%%%%%%%%%%%consider to move this to gui
     fprintf(smu.handle,'smua.measure.filter.count = 4');
     fprintf(smu.handle,'smub.measure.filter.count = 4');
     fprintf(smu.handle,'smua.measure.filter.enable = smua.FILTER_ON');
     fprintf(smu.handle,'smub.measure.filter.enable = smub.FILTER_ON');
     fprintf(smu.handle,'smua.measure.filter.type = smua.FILTER_REPEAT_AVG');
     fprintf(smu.handle,'smub.measure.filter.type = smub.FILTER_REPEAT_AVG');
     %%%%%%%%%%%%%%%%%%end of consider to move this to gui
     
     
     fprintf(smu.handle,strcat(smu.source,'.measure.autorangei =', smu.source,'.AUTORANGE_ON'));    
     fprintf(smu.handle,strcat(smu.source,'.measure.autorangev =', smu.source,'.AUTORANGE_ON')); 
     fprintf(smu.handle,strcat(smu.drain,'.measure.autorangei =', smu.drain,'.AUTORANGE_ON'));    
     fprintf(smu.handle,strcat(smu.drain,'.measure.autorangev =', smu.drain,'.AUTORANGE_ON')); 
     %see ranges on 2-83 (108) of the manual

%      fprintf(smu.handle,strcat(smu.source,'.measure.autorangei =', smu.source,'.AUTORANGE_OFF'));    
%      fprintf(smu.handle,strcat(smu.source,'.measure.autorangev =', smu.source,'.AUTORANGE_OFF')); 
%      fprintf(smu.handle,strcat(smu.drain,'.measure.autorangei =', smu.drain,'.AUTORANGE_OFF'));    
%      fprintf(smu.handle,strcat(smu.drain,'.measure.autorangev =', smu.drain,'.AUTORANGE_OFF'));  
%      fprintf(smu.handle,strcat(smu.source,'.measure.rangei = 0.1'));    
%      fprintf(smu.handle,strcat(smu.source,'.measure.rangev = 2')); 
%      fprintf(smu.handle,strcat(smu.drain,'.measure.rangei = 0.1'));    
%      fprintf(smu.handle,strcat(smu.drain,'.measure.rangev = 2')); 
     
% % %
     
     
% % %      fprintf(smu.handle,strcat(smu.source,'.measure.autorangei =', smu.source,'.AUTORANGE_FOLLOW_LIMIT'));    
% % %      fprintf(smu.handle,strcat(smu.source,'.measure.autorangev =', smu.source,'.AUTORANGE_FOLLOW_LIMIT')); 
% % %      fprintf(smu.handle,strcat(smu.drain,'.measure.autorangei =', smu.drain,'.AUTORANGE_FOLLOW_LIMIT'));    
% % %      fprintf(smu.handle,strcat(smu.drain,'.measure.autorangev =', smu.drain,'.AUTORANGE_FOLLOW_LIMIT')); 
     if strcmp(smu.pulse, 'off')
      fprintf(smu.handle,strcat(smu.source,'.trigger.endpulse.action =', smu.source,'.SOURCE_HOLD'));
     else   
      fprintf(smu.handle,strcat(smu.source,'.trigger.endpulse.action =', smu.source,'.SOURCE_IDLE'));
      fprintf(smu.handle,strcat('trigger.timer[1].delay =', smu.pulse));
      fprintf(smu.handle,'trigger.timer[1].passthrough = false');
      fprintf(smu.handle,'trigger.timer[1].count = 1');
      fprintf(smu.handle,'trigger.blender[1].orenable = true');
      fprintf(smu.handle,strcat('trigger.blender[1].stimulus[1] =',smu.source,'.trigger.SWEEPING_EVENT_ID'));
      fprintf(smu.handle,strcat('trigger.blender[1].stimulus[2] =',smu.source,'.trigger.PULSE_COMPLETE_EVENT_ID'));
      fprintf(smu.handle,'trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID');
      fprintf(smu.handle,strcat(smu.source,'.trigger.source.stimulus = trigger.timer[1].EVENT_ID'));
     end
     fprintf(smu.handle,'smua.source.settling = smua.SETTLE_FAST_RANGE');
     fprintf(smu.handle,'smub.source.settling = smub.SETTLE_FAST_RANGE');

     fprintf(smu.handle,'display.screen = display.SMUA_SMUB');
     fprintf(smu.handle,'format.data = format.ASCII');
     if strcmp(smu.delay, 'off')
       fprintf(smu.handle,strcat(smu.source,'.measure.delay = ', smu.source,'.DELAY_AUTO')); 
       if strcmp(smu.pulse, 'off')  
        fprintf(smu.handle,strcat(smu.source,'.measure.delayfactor = 28.0'));
       else
        fprintf(smu.handle,strcat(smu.source,'.measure.delayfactor = 1.0'));
       end 
     else
       fprintf(smu.handle,strcat(smu.source,'.measure.delay = ', smu.delay));  
     end 
            
     fprintf(smu.handle,strcat(smu.source,'.trigger.measure.iv(', smu.source,'.nvbuffer1, ', smu.source,'.nvbuffer2)'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.measure.action = ', smu.source,'.ENABLE'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.source.action = ', smu.source,'.ENABLE'));       
     fprintf(smu.handle,strcat(smu.drain,'.trigger.measure.iv(', smu.drain,'.nvbuffer1, ', smu.drain,'.nvbuffer2)'));
     fprintf(smu.handle,strcat(smu.drain,'.trigger.measure.action = ', smu.drain,'.ENABLE'));
     fprintf(smu.handle,strcat(smu.drain,'.trigger.source.action = ', smu.drain,'.DISABLE')); 
    
     fprintf(smu.handle,strcat(smu.source,'.measure.nplc = ', smu.nplc));
     fprintf(smu.handle,strcat(smu.source,'.trigger.endsweep.action = ', smu.source,'.SOURCE_IDLE'));
     if strcmp(smu.delay, 'off')
       fprintf(smu.handle,strcat(smu.drain,'.measure.delay = ', smu.drain,'.DELAY_AUTO'))
       if strcmp(smu.pulse, 'off')  
        fprintf(smu.handle,strcat(smu.drain,'.measure.delayfactor = 28.0'));
       else
        fprintf(smu.handle,strcat(smu.drain,'.measure.delayfactor = 1.0'));
       end 
     else
       fprintf(smu.handle,strcat(smu.drain,'.measure.delay = ', smu.delay));  
     end
     fprintf(smu.handle,strcat(smu.drain,'.measure.nplc = ', smu.nplc));
     fprintf(smu.handle,strcat(smu.drain,'.trigger.measure.stimulus = ', smu.source, '.trigger.SOURCE_COMPLETE_EVENT_ID'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.measure.stimulus = ', smu.source, '.trigger.SOURCE_COMPLETE_EVENT_ID'));
     fprintf(smu.handle,'trigger.blender[2].orenable = false');
     fprintf(smu.handle,strcat('trigger.blender[2].stimulus[1] =',smu.source,'.trigger.MEASURE_COMPLETE_EVENT_ID'));
     fprintf(smu.handle,strcat('trigger.blender[2].stimulus[2] =',smu.drain,'.trigger.MEASURE_COMPLETE_EVENT_ID'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.endpulse.stimulus = trigger.blender[2].EVENT_ID'));
     
     if smu.highC
        fprintf(smu.handle,strcat(smu.source,'.source.highc = ',smu.source,'.ENABLE')); 
        fprintf(smu.handle,strcat(smu.drain,'.source.highc = ',smu.drain,'.ENABLE')); 
     end   
    end 
   
  function KeithleyInitSingleCh(smu)
     % % % Keithley.handle = [];
     % % % Keithley.steps %%int
     % % % Keithley.repeat %%int
     % % % Keithley.start %%int
     % % % Keithley.end %%int
     % % % Keithley.limit %%float
     % % % Keithley.delay %%str "off"/time in sec before measurement
     % % % Keithley.pulse %%str "off"/time in sec pause between pulses
     % % % Keithley.source %%str "smua"/"smub"
     % % % Keithley.drain %%str "smua"/"smub"
     % % % Keithley.type %%str "i"/"v"
     % % % Keithley.drainLimit %% str
     % % % Keithley.freq %% float
     % % % Keithley.drainVoltage %% str "off"/value
     % % % Keithley.nplc %% str
     % % % Keithley.sense %% true/false
     % % % Keithley.sense_drain %% true/false
     % % % Keithley.single_ch %% true/false 
     fprintf(smu.handle,'reset()'); 
     fprintf(smu.handle,'beeper.enable=0');
     fprintf(smu.handle,strcat(smu.source,'.reset()')); 
     if smu.sense 
         fprintf(smu.handle,strcat(smu.source,'.sense = ',smu.source,'.SENSE_REMOTE'));
     else    
         fprintf(smu.handle,strcat(smu.source,'.sense = ',smu.source,'.SENSE_LOCAL'));
     end    
     
     %%%%%%%%%%%%%%%%%%consider to move this to gui
     fprintf(smu.handle,strcat(smu.source,'.measure.filter.count = 4')); 
     fprintf(smu.handle,strcat(smu.source,'.measure.filter.enable = ',smu.source,'.FILTER_ON')); 
     fprintf(smu.handle,strcat(smu.source,'.measure.filter.type = ',smu.source,'.FILTER_REPEAT_AVG')); 
     fprintf(smu.handle,strcat(smu.source,'.measure.autorangei =', smu.source,'.AUTORANGE_ON'));    
     fprintf(smu.handle,strcat(smu.source,'.measure.autorangev =', smu.source,'.AUTORANGE_ON')); 
     %%%%%%%%%%%%%%%%%%end of consider to move this to gui
     
     if strcmp(smu.pulse, 'off')
      fprintf(smu.handle,strcat(smu.source,'.trigger.endpulse.action =', smu.source,'.SOURCE_HOLD'));
     else   
      fprintf(smu.handle,strcat(smu.source,'.trigger.endpulse.action =', smu.source,'.SOURCE_IDLE'));
      fprintf(smu.handle,strcat('trigger.timer[1].delay =', smu.pulse));
      fprintf(smu.handle,'trigger.timer[1].passthrough = false');
      fprintf(smu.handle,'trigger.timer[1].count = 1');
      fprintf(smu.handle,'trigger.blender[1].orenable = true');
      fprintf(smu.handle,strcat('trigger.blender[1].stimulus[1] =',smu.source,'.trigger.SWEEPING_EVENT_ID'));
      fprintf(smu.handle,strcat('trigger.blender[1].stimulus[2] =',smu.source,'.trigger.PULSE_COMPLETE_EVENT_ID'));
      fprintf(smu.handle,'trigger.timer[1].stimulus = trigger.blender[1].EVENT_ID');
      fprintf(smu.handle,strcat(smu.source,'.trigger.source.stimulus = trigger.timer[1].EVENT_ID'));
     end 
     fprintf(smu.handle,strcat(smu.source,'.source.settling = ',smu.source,'.SETTLE_FAST_RANGE'));

     fprintf(smu.handle,'display.screen = display.SMUA_SMUB');
     fprintf(smu.handle,'format.data = format.ASCII');
     if strcmp(smu.delay, 'off')
       fprintf(smu.handle,strcat(smu.source,'.measure.delay = ', smu.source,'.DELAY_AUTO')); 
       if strcmp(smu.pulse, 'off')  
        fprintf(smu.handle,strcat(smu.source,'.measure.delayfactor = 28.0'));
       else
        fprintf(smu.handle,strcat(smu.source,'.measure.delayfactor = 1.0'));
       end 
     else
       fprintf(smu.handle,strcat(smu.source,'.measure.delay = ', smu.delay));  
     end  
            
     fprintf(smu.handle,strcat(smu.source,'.trigger.measure.iv(', smu.source,'.nvbuffer1, ', smu.source,'.nvbuffer2)'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.measure.action = ', smu.source,'.ENABLE'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.source.action = ', smu.source,'.ENABLE'));       
     fprintf(smu.handle,strcat(smu.source,'.measure.nplc = ', smu.nplc));
     fprintf(smu.handle,strcat(smu.source,'.trigger.endsweep.action = ', smu.source,'.SOURCE_IDLE'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.measure.stimulus = ', smu.source, '.trigger.SOURCE_COMPLETE_EVENT_ID'));
     fprintf(smu.handle,strcat(smu.source,'.trigger.endpulse.stimulus = ',smu.source,'.trigger.MEASURE_COMPLETE_EVENT_ID'));
     if smu.highC
        fprintf(smu.handle,strcat(smu.source,'.source.highc = ',smu.source,'.ENABLE')); 
     end
    end      
   
  
    function KeithleyInitSweep(smu)
% % % Keithley.handle = [];
% % % Keithley.steps %%int
% % % Keithley.repeat %%int
% % % Keithley.start %%int
% % % Keithley.end %%int
% % % Keithley.limit %%float
% % % Keithley.delay %%str "off"/time in sec before measurement
% % % Keithley.pulse %%str "off"/time in sec pause between pulses
% % % Keithley.source %%str "smua"/"smub"
% % % Keithley.drain %%str "smua"/"smub"
% % % Keithley.type %%str "i"/"v"
% % % Keithley.drainLimit %% str
% % % Keithley.freq %% float
% % % Keithley.drainVoltage %% str "off"/value
% % % Keithley.nplc %% str
% % % Keithley.sense %% true/false
% % % Keithley.sense_drain %% true/false
% % % Keithley.single_ch %% true/false

     fprintf(smu.handle,'reset()'); 
     fprintf(smu.handle,'beeper.enable=0');
     fprintf(smu.handle,strcat(smu.source,'.reset()')); 
     fprintf(smu.handle,strcat(smu.drain,'.reset()'));  
     if smu.sense 
         fprintf(smu.handle,strcat(smu.source,'.sense = ',smu.source,'.SENSE_REMOTE'));
     else    
         fprintf(smu.handle,strcat(smu.source,'.sense = ',smu.source,'.SENSE_LOCAL'));
     end    
     
     if (smu.sense_drain) && (smu.sense)
         fprintf(smu.handle,strcat(smu.drain,'.sense = ',smu.drain,'.SENSE_REMOTE'));
     else    
         fprintf(smu.handle,strcat(smu.drain,'.sense = ',smu.drain,'.SENSE_LOCAL'));
     end    
     
     %%%%% it may be smart to put this to GUI at some point
     fprintf(smu.handle,'smua.measure.filter.count = 4');
     fprintf(smu.handle,'smub.measure.filter.count = 4');
     fprintf(smu.handle,'smua.measure.filter.enable = smua.FILTER_ON');
     fprintf(smu.handle,'smub.measure.filter.enable = smub.FILTER_ON');
     fprintf(smu.handle,'smua.measure.filter.type = smua.FILTER_REPEAT_AVG');
     fprintf(smu.handle,'smub.measure.filter.type = smub.FILTER_REPEAT_AVG');
	 %%%%% end of add to GUI
	 
     fprintf(smu.handle,strcat(smu.source,'.measure.autorangei =', smu.source,'.AUTORANGE_ON'));    
     fprintf(smu.handle,strcat(smu.source,'.measure.autorangev =', smu.source,'.AUTORANGE_ON')); 
     fprintf(smu.handle,strcat(smu.drain,'.measure.autorangei =', smu.drain,'.AUTORANGE_ON'));    
     fprintf(smu.handle,strcat(smu.drain,'.measure.autorangev =', smu.drain,'.AUTORANGE_ON')); 
	 
	 fprintf(smu.handle,'format.data = format.ASCII');
	 	 
     if strcmp(smu.delay, 'off')
       fprintf(smu.handle,strcat(smu.source,'.measure.delay = ', smu.source,'.DELAY_AUTO')); 
       fprintf(smu.handle,strcat(smu.drain,'.measure.delay = ', smu.drain,'.DELAY_AUTO'))
       if strcmp(smu.pulse, 'off')  
        fprintf(smu.handle,strcat(smu.source,'.measure.delayfactor = 28.0'));
        fprintf(smu.handle,strcat(smu.drain,'.measure.delayfactor = 28.0'));
       else
        fprintf(smu.handle,strcat(smu.source,'.measure.delayfactor = 1.0'));
        fprintf(smu.handle,strcat(smu.drain,'.measure.delayfactor = 1.0'));
       end 
     else
       fprintf(smu.handle,strcat(smu.source,'.measure.delay = ', smu.delay));  
       fprintf(smu.handle,strcat(smu.drain,'.measure.delay = ', smu.delay)); 
     end
     fprintf(smu.handle,strcat(smu.source,'.measure.nplc = ', smu.nplc));
     fprintf(smu.handle,strcat(smu.drain,'.measure.nplc = ', smu.nplc));
     
	 fprintf(smu.handle,strcat(smu.source,'.nvbuffer1.clear()'));   
     fprintf(smu.handle,strcat(smu.source,'.nvbuffer2.clear()'));   
     fprintf(smu.handle,strcat(smu.drain,'.nvbuffer1.clear()'));
     fprintf(smu.handle,strcat(smu.drain,'.nvbuffer2.clear()')); 
	 
     fprintf(smu.handle,strcat('display.',smu.drain,'.measure.func = display.MEASURE_DCAMPS'));
     
	 if strcmp(smu.type,'i')
       fprintf(smu.handle,strcat(smu.source,'.source.func = ',smu.source,'.OUTPUT_DCAMPS'))
       if strcmp(smu.pulse, 'off') || (abs(smu.start) < 1.5 && abs(smu.end) < 1.5)
        fprintf(smu.handle,strcat(smu.source,'.source.limitv=',num2str(smu.limit)));
       else
        fprintf(smu.handle,'smua.measure.filter.enable = smua.FILTER_OFF');
        fprintf(smu.handle,'smub.measure.filter.enable = smub.FILTER_OFF');
        fprintf(smu.handle,strcat(smu.source,'.source.autorangei =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangev =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangei =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangev =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.measure.rangei = 10'));
        fprintf(smu.handle,strcat(smu.drain,'.measure.rangei = 10')) 
        fprintf(smu.handle,strcat(smu.source,'.source.delay = 100e-6'));
        fprintf(smu.handle,strcat(smu.source,'.measure.autozero =',smu.source,'.AUTOZERO_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.rangei = 10'));
        fprintf(smu.handle,strcat(smu.source,'.source.leveli = 0'));
        fprintf(smu.handle,strcat(smu.source,'.source.limitv = 6'));
       end
       fprintf(smu.handle,strcat('display.',smu.source,'.measure.func = display.MEASURE_DCVOLTS'));
     else 
       fprintf(smu.handle,strcat(smu.source,'.source.func = ',smu.source,'.OUTPUT_DCVOLTS'))  
       if strcmp(smu.pulse, 'off') || abs(smu.limit) < 1.5
        fprintf(smu.handle,strcat(smu.source,'.source.limiti=',num2str(smu.limit)));
       else
        fprintf(smu.handle,'smua.measure.filter.enable = smua.FILTER_OFF');
        fprintf(smu.handle,'smub.measure.filter.enable = smub.FILTER_OFF');
        fprintf(smu.handle,strcat(smu.source,'.source.autorangei =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.source.autorangev =',smu.source,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangei =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.drain,'.source.autorangev =',smu.drain,'.AUTORANGE_OFF'));
        fprintf(smu.handle,strcat(smu.source,'.measure.rangei = 10'));
        fprintf(smu.handle,strcat(smu.drain,'.measure.rangei = 10')) 
        fprintf(smu.handle,strcat(smu.source,'.source.delay = 100e-6'));
        fprintf(smu.handle,strcat(smu.source,'.measure.autozero =',smu.source,'.AUTOZERO_OFF'));   
        fprintf(smu.handle,strcat(smu.source,'.source.rangev = 6'));
        fprintf(smu.handle,strcat(smu.source,'.source.levelv = 0'));
        fprintf(smu.handle,strcat(smu.source,'.source.limiti = 1.5'));
       end    
       fprintf(smu.handle,strcat('display.',smu.source,'.measure.func = display.MEASURE_DCAMPS'));
     end  
     if ~strcmp(smu.drainVoltage, 'off')
      fprintf(smu.handle,strcat(smu.drain,'.source.func = ',smu.drain,'.OUTPUT_DCVOLTS'));
      fprintf(smu.handle,strcat(smu.drain,'.source.levelv = ', smu.drainVoltage));
      fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', smu.drainLimit));
     else
      fprintf(smu.handle,strcat(smu.drain,'.source.func = ',smu.drain,'.OUTPUT_DCVOLTS'));
      fprintf(smu.handle,strcat(smu.drain,'.source.levelv = 0'));
      if strcmp(smu.type,'v') && (smu.limit > 1.5)
       fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', num2str(1.5)));   
      else 
       fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', num2str(smu.limit)));      
      end 
      if strcmp(smu.type,'i') 
       fprintf(smu.handle,strcat(smu.drain,'.source.limiti = ', num2str(smu.end)));      
      end 
     end
     fprintf(smu.handle,strcat('startvalue = ' , num2str(smu.start)));
     fprintf(smu.handle,strcat('endvalue = ' , num2str(smu.end)));
     fprintf(smu.handle,strcat('points = ' , num2str(smu.steps-1)));
     
     if smu.highC
        fprintf(smu.handle,strcat(smu.source,'.source.highc = ',smu.source,'.ENABLE')); 
        fprintf(smu.handle,strcat(smu.drain,'.source.highc = ',smu.drain,'.ENABLE')); 
     end
    end     
    
   function val_out = KeithleyGetIV(smu)
    if ~smu.single_ch 
     fprintf(smu.handle,strcat('print (', smu.drain,'.measure.iv())'));
     if ~strcmp(smu.delay,'off')
        pause(str2num(smu.delay)*0.8);
     end
     [keithleyresponse,n] = str2num(fscanf(smu.handle));
     while n<1
       pause(1);  
       [keithleyresponse,n] = str2num(fscanf(smu.handle));
     end
     val_out(3) = keithleyresponse(1);
     val_out(4) = keithleyresponse(2);
    end
    fprintf(smu.handle,strcat('print (',smu.source,'.measure.iv())'));
    if ~strcmp(smu.delay,'off')
        pause(str2num(smu.delay)*0.8);
    end
    [keithleyresponse,n] = str2num(fscanf(smu.handle));
    while n<1
       pause(1);  
       [keithleyresponse,n] = str2num(fscanf(smu.handle));
    end
    val_out(1) = keithleyresponse(1);
    val_out(2) = keithleyresponse(2);   
   end

    function [val_out, image, status] = getPulseSnapshot(cam, smu)
       status = 0;
       %%%%% the snapshot function extracs the last image from camera
       %%%%% stack, so it may be taken before the Keithley was turned on.
       %%%%% Here we will check that the time from the moment when Keithley was
       %%%%% turned on until the snapshot was taken is larger than the
       %%%%% expTime. NOTE: 1e11 is a coefficient to transform output of
       %%%%% the datenum to microsec
       fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_ON'));
       if ~smu.single_ch 
         fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_ON'));
       end
       ONtime = datetime('now', 'Format', 'dd-MMM-yyyy HH:mm:ss.SSS');
       IMGtime = ONtime;
       val_out = KeithleyGetIV(smu);     
       
       while ((datenum(char(IMGtime), 'dd-mmm-yyyy HH:MM:SS.FFF') - datenum(char(ONtime), 'dd-mmm-yyyy HH:MM:SS.FFF'))*1e11 < cam.expTime)
        try
         [tmpIMG, IMGtime] = snapshot(cam.handle);   
         image = single(tmpIMG);
        catch
         status = 1;
         break;
        end  
       end 
       fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_OFF'));
	    if ~smu.single_ch 
         fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_OFF'));
	    end	
        
       if strcmp(smu.pulse, 'off')
           pause(1);
       else    
           pause(str2num(smu.pulse));
       end    
    end


    function [val_out, wvl, spectrum] = getPulseSpectra(smu, spmeter)
       fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_ON'));
       if ~smu.single_ch 
         fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_ON'));
	   end
       val_out = KeithleyGetIV(smu);
       [wvl, spectrum] = getSingleSpectrum(spmeter.time,spmeter.averaging, spmeter.device);
       
       fprintf(smu.handle,strcat(smu.source,'.source.output =', smu.source,'.OUTPUT_OFF'));
	    if ~smu.single_ch 
         fprintf(smu.handle,strcat(smu.drain,'.source.output =', smu.drain,'.OUTPUT_OFF'));
	    end	
        
       if strcmp(smu.pulse, 'off')
           pause(1);
       else    
           pause(str2num(smu.pulse));
       end    
  end

   %%%%%%%%%%%
   %%% setup Keithley communication 
   %%%%%%%%%%%
   function K=setupKeithley(KeithleyAddress, KeithleyPort)
    K = tcpip(KeithleyAddress, KeithleyPort);
        set(K, 'InputBufferSize', 300000); 
        set(K, 'OutputBufferSize', 300000); 
        fopen(K); 
    fprintf(K,'beeper.enable=0'); 
   end
 
    function savedatatofile (filename, comment, datatosave)
     fid = fopen(filename,'w');
     fprintf(fid, comment);
     fclose(fid);   
     dlmwrite(filename, datatosave,'-append');
    end

    function [handle_fig, camera_out] = start_camera(camera)    
      
%       delete(camera.handle);
       
%       camera.handle = gigecam(camera.address);
       handle_fig = figure('Toolbar','none',...
       'Menubar', 'none',...
       'NumberTitle','Off',...
       'Name','IVL GUI');   
%       UseSnapshot = true; % disable this option for the gigecam interface
       hImage = image(zeros(camera.imgSize, camera.imgSize));
	   camera_out = set_cam(camera);
    end
    
    function close_cam(handle_fig,camera)
        delete(camera.handle);
        close(handle_fig);
    end    
    
    function camera_out = set_cam(camera)     
%             current_axes = gca;
%             oldobj = findobj('type','rectangle','-or','type','Group','-or','type','Line');
%             if ~isempty(oldobj)
%              tmp_ax = axes('Parent',gcf, 'Visible', 'off');
%              newobj = copyobj(oldobj, tmp_ax);
%              set(gcf,'CurrentAxes',current_axes);
%             end        
%             
%             delete(camera.handle);
%             camera.handle = gigecam(camera.address);
%             set(camera.handle, 'Width', camera.imgSize);
%             set(camera.handle, 'AoiHeight', camera.imgSize);
%             set(camera.handle, 'AoiOffsetY', camera.imgOffset);
%             set(camera.handle, 'OffsetX', camera.imgOffset);
%             if camera.reverseX
%              set(camera.handle, 'ReverseX', 'True');
%             else  
%              set(camera.handle, 'ReverseX', 'False');   
%             end 
%             if camera.reverseY
%              set(camera.handle, 'ReverseY', 'True');
%             else  
%              set(camera.handle, 'ReverseY', 'False');   
%             end 
%             set(camera.handle, 'ExposureTime', camera.expTime);  
%           hImage = image( zeros(camera.imgSize, camera.imgSize) );  
%           preview(camera.handle, hImage); 
%           pause((camera.expTime/1000000)*1.5);
%           
%           if exist('newobj')
% 		    set(newobj, 'Parent', gca);
%             delete(tmp_ax);
%           end  
		  camera_out = camera;
    end
    
end
