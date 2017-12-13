% test_SAWsParameterMeas01_saveRaw
%   Sweep frequency, read SAW output, save raw data
% Visarute Pinrod
% SonicMEMS Laboratory, ECE, Cornell University, Ithaca, NY, USA
% October 26, 2016
% ========================================================================

% ************************* For testing  *********************************
    close all                                                           %*
    clear all                                                           %*
% ************************************************************************


%% Measurement detail
% AC couple, 1x probe
% v1 Drive in from fgen
% v3 Sense: S1-S2 from diff amp (+20 dB gain)
% v4 Drive out


%% Change default font
% Change default axes fonts.
set(0,'DefaultAxesFontName', 'Times New Roman')
set(0,'DefaultAxesFontSize', 12)
set(0,'DefaultAxesFontWeight', 'Bold')

% Change default text fonts.
set(0,'DefaultTextFontname', 'Times New Roman')
set(0,'DefaultTextFontSize', 12)
set(0,'DefaultAxesFontWeight', 'Bold')

%% Connect tools
% Open oscilloscope
scope = openDSOX3034A();

% Open rate table
fgen = openSMC100A();


%% Define variable
% Parameter
figPlot = figure;

% Sweep parameter
vsweep = [0.1 ];
fsweep = [200E6];
point=1;
%% Main loop
xOr = str2double(query(scope, ':WAVeform:XORigin?'));
pause(3);
xRef = str2double(query(scope, ':WAVeform:XREFerence?'));
pause(3);
xInc = str2double(query(scope, ':WAVeform:XINCrement?'));
pause(3);
time = (xRef-(1:50000))*xInc-xOr;
% 
% fprintf(fgen, 'OUTP ON');
% fprintf(fgen, 'OUTP OFF');
% setVrmsSMC100A(fgen,0.00001)

%% Sweep magnetic field
for vi = 1:length(fsweep)
    % Set function generator output
    v = vsweep(vi)
    setVrmsSMC100A(fgen,v)
    pause(1)
    
    % Zooa and read data from oscilloscope
    %         zoomScopeY1x(scope,1)
    %         zoomScopeY1x(scope,2)
    fprintf(scope, ':SINGLE');
    pause(1)
    v2 = readDSOX3034A(scope,2)';
    pause(10)
%     v3 = readDSOX3034A(scope,3)';
%     v4 = readDSOX3034A(scope,4)';
    fprintf(scope, ':RUN');

    plot(time,v2,'.r')
%     hold on
%     plot(time,v3,'.g')
%     plot(time,v4,'.b')
    hold off
    
    save(['test_NZEROFsweep_Meas01' num2str(point,'%05d') '_raw' num2str(f) 'Hz.mat'],'time','v2');
    point=point+1;
end


