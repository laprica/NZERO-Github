function zoomScopeY(scope,channel)
v = readScope(scope,channel);
pause(2)
a = query(scope,[':CHANnel' num2str(channel) ':SCALe?']);
b = textscan(a,'%f');
scaleOld = b{1};
disp(['scaleOld' num2str(scaleOld) 'new' num2str(0.9*(max(v)-min(v))/8)])
% Zoom out loop
while(scaleOld < (1/0.9)*(max(v)-min(v))/8)
    scale = 2*scaleOld;
    disp(['zoom out channel' num2str(channel) 'to ' num2str(scale)])
    fprintf(scope, [':CHANnel' num2str(channel) ':SCALe ' num2str(scale)]);
    pause(2)
    scaleOld = scale;
    v = readScope(scope,channel);
    pause(2)
end

scale = (1/0.85)*(max(v)-min(v))/8;
% Zoom back in
if(scale < 0.02)
    scale = 0.02;
end
fprintf(scope, [':CHANnel' num2str(channel) ':SCALe ' num2str(scale)]);
disp(['zoom in channel' num2str(channel) 'to ' num2str(scale)])
pause(2)
end