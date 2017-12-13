function setupScope1(scope)
% fprintf(scope, '*RST');
fprintf(scope, ':TIMebase:OFFSet 0');
% fprintf(scope, ':TIMebase:SCALe 0.1');

fprintf(scope, ':CHANnel1:DISPlay 1');
fprintf(scope, ':CHANnel2:DISPlay 1');
% fprintf(scope, ':CHANnel3:DISPlay 1');

fprintf(scope, ':CHANnel1:COUPling AC');
fprintf(scope, ':CHANnel2:COUPling AC');
% fprintf(scope, ':CHANnel3:COUPling AC');

% fprintf(scope, ':TRIGger:EDGE:EXT');

fprintf(scope, ':RUN');
end