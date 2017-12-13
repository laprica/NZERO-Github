function setFreqSMC100A(SMC100A,freq)
fprintf(SMC100A, [':SOURce:FREQuency:CW ' num2str(freq)]);
end