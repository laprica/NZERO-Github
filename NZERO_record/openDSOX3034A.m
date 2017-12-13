function obj1=openDSOX3034A()

% Find a VISA-USB object.
obj1 = instrfind('Type', 'visa-usb', 'RsrcName', 'USB0::0x0957::0x1796::MY54101159::0::INSTR', 'Tag', '');

% Create the VISA-USB object if it does not exist
% otherwise use the object that was found.
if isempty(obj1)
    obj1 = visa('NI', 'USB0::0x0957::0x1796::MY54101159::0::INSTR');
else
    fclose(obj1);
    obj1 = obj1(1)
end

% Set Input buffer size
set(obj1, 'InputBufferSize', 1000000);

% Connect to instrument object, obj1.
fopen(obj1);
end