% closeObj(obj1)
% Disconnect from instrument object and delete variable
% Visarute Pinrod, June 10, 2015

function closeObj(obj1)
% Disconnect from instrument object
fclose(obj1);
delete(obj1);
end