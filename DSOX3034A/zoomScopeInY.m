function zoomScopeInY(scope,channel)
v = readScope(scope,channel);
pause(2)
scale = 0.85*(max(v)-min(v))/8;
if(scale < 0.02)
    scale = 0.02;
end
fprintf(scope, [':CHANnel' num2str(channel) ':SCALe ' num2str(scale)]);
pause(0.3)
end