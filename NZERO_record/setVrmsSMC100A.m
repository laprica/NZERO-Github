function setVrmsSMC100A(SMC100A,V)
fprintf(SMC100A, [':SOURce:POWer:LEVel:IMMediate ' num2str(V) 'V']);
end