%% 
%https://www.mathworks.com/help/thingspeak/read-data-from-channel.html
%% Descargamos los datos de thingSpeak
channelID_1 = 698783;
channelID_2 = 698784;
[data_1,timestamps_1] = thingSpeakRead(channelID_1,'NumPoints',60);
[data_2,timestamps_2] = thingSpeakRead(channelID_2,'NumPoints',60);
% Primera columna Humedad (Field1), segunda columna Temperatura (Field2)
%% Juntamos los datos de los dos canales
nData = 60;
tempData=[];
humData=[];
for i=1:nData
    tempData = [tempData; data_1(i,1); data_2(i,1)];
    humData = [humData; data_1(i,2); data_2(i,2)];
end

corrplot([tempData,humData],'varNames',{'Temperatura(ºC)', 'Humedad (%)'});
