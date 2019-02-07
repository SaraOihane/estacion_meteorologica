# encoding=utf8
"""
@author: Sara García y Oihane Busselo
@desc: Este programa lee la humedad y temperatura y los sube a ThingSpeak utilizando el protocolo HTTP
"""

import httplib
import urllib
import json
import time
import Adafruit_DHT
CLEAR_API_KEY = 'X1FW95JO20879TPI'
CREATE_API_KEY = 'X1FW95JO20879TPI'
INPUT_PIN_SENSOR = 22


def Crear_canal(index):
    print("Creando canal " +str(index) +  "...")
    method = "POST"
    relative_uri = "/channels.json"
    headers = {'Host': server,
               'Content-Type': 'application/x-www-form-urlencoded'}  # diccionario
    payload = {'api_key': CREATE_API_KEY,
               'name': 'Info meteorológica ' + str(index),
               'field1': 'HUMEDAD',
               'field2': 'TEMPERATURA'}

    # Codificamos los datos a enviar en formato form.
    payload_encoded = urllib.urlencode(payload)
    headers['Content-Length'] = len(payload_encoded)

    print("\tEnviando petición de creación del canal..."),
    connTCP.request(method, relative_uri, body=payload_encoded, headers=headers)
    print("\tPetición enviada!")

    print("\tEsperando respuesta...")
    respuesta = connTCP.getresponse()
    status = respuesta.status
    print("\tStatus: " + str(status))
    contenido = respuesta.read()
    # Pasamos contenido en formato json a un dict.
    contenido_json = json.loads(contenido)
    CHANNEL_IDi = contenido_json['id']
    WRITE_API_KEYi = contenido_json['api_keys'][0]['api_key']
    print("Canal " + str(index) + " creado.")

    return CHANNEL_IDi, WRITE_API_KEYi


def Medir_Temperatura_Humedad(pin):
    sensor = Adafruit_DHT.DHT22
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)
    return humedad, temperatura


if __name__ == '__main__':
    # Servidor donde queremos subir los datos
    server = 'api.thingspeak.com'
    # connTCP es la variable o el objeto que referencia la conexión TCP
    connTCP = httplib.HTTPSConnection(server)
    print("Establenciendo conexión TCP..."),
    connTCP.connect()  # establecer conexión
    print("Conexión TCP establecida!")

    # Creamos 2 canales para subir los datos
    CHANNEL_ID1, WRITE_API_KEY1 = Crear_canal(1)
    CHANNEL_ID2, WRITE_API_KEY2 = Crear_canal(2)

    # Utilizamos un flag para saber en qué canal escribir los datos
    flag = 0

    try:
        while 1:
            #Medimos instante inicial
            init = time.time()
            if flag == 0:
                WRITE_API_KEY = WRITE_API_KEY1
                flag = 1
            else:
                WRITE_API_KEY = WRITE_API_KEY2
                flag = 0

            # Leyendo el API de la librería de psutil vemos cuales son los métodos para obtener el %CPU y %RAM

            sensorHum, sensorTemp = Medir_Temperatura_Humedad(INPUT_PIN_SENSOR)

            print("\nTemperatura: " + str(sensorTemp) + "\tHumedad: " + str(sensorHum))

            # Creamos la petición http que sube datos a mi canal de thinspeak
            # https://www.mathworks.com/help/thingspeak/writedata.html
            method = "POST"
            relative_uri = "/update.json"
            headers = {'Host': server,
                       'Content-Type': 'application/x-www-form-urlencoded'}  # diccionario
            payload = {'api_key': WRITE_API_KEY,
                       'field1': sensorHum,
                       'field2': sensorTemp}
            # Codificamos los datos a enviar en formato form.
            payload_encoded = urllib.urlencode(payload)
            headers['Content-Length'] = len(payload_encoded)

            print("Enviando petición HTTP..."),
            connTCP.request(method, relative_uri, body=payload_encoded, headers=headers)
            print("Petición enviada!")

            print("Esperando respuesta HTTP...")
            respuesta = connTCP.getresponse()
            status = respuesta.status
            print(str(status))
            print(respuesta.read())

            fin = time.time()
            # Calculamos el tiempo que ha tardado
            delta_tiempo = init - fin
            # Esperamos la diferencia de tiempo hasta 10 segundos antes de subir otro dato
            time.sleep(10-delta_tiempo)

    except KeyboardInterrupt:
        connTCP.close()
        print("Se ha pulsado Ctrl+C. Saliendo del programa...")
