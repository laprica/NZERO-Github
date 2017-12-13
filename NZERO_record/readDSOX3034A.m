function v=readDSOX3034A(scope,channel)
% fprintf(scope, [':WAVeform:SOURce CHANnel' num2str(channel)]);
% fprintf(scope, ':WAVeform:FORMat BYTE');
% yOr = str2double(query(scope, ':WAVeform:YORigin?'));
% yRef = str2double(query(scope, ':WAVeform:YREFerence?'));
% yInc = str2double(query(scope, ':WAVeform:YINCrement?'));
% pause(0.5);
% dataVal = double(uint8(query(scope, ':WAVeform:DATA?')));
% pause(0.5);
% v = (yRef-dataVal(13:end))*yInc-yOr;


fprintf(scope, [':WAVeform:SOURce CHANnel' num2str(channel)]);
fprintf(scope, ':WAVeform:FORMat ASCII');
pause(0.5);
a = query(scope, ':WAVeform:DATA?');
pause(2);

b = textscan(a(11:end),'%f,');
v = b{1};
end