function zoomScopeOutY(scope,channel)
v = readScope(scope,channel);
pause(2)
a = query(scope,)
if
if(scale < 0.02)
    scale = 0.02;
end
fprintf(scope, [':CHANnel' num2str(channel) ':SCALe ' num2str(scale)]);
pause(0.3)
end