#!/usr/bin/env python3

from azure.iot.device import IoTHubDeviceClient, Message
import random
import socket
import time
import threading


import cv2
from pyzbar.pyzbar import decode
from PIL import Image

BATTERY_LOW = 14.2
BATTERY_HIGH = 15.3

PORT = 65432 #TCP Port
receiveMsg = "MSG RCV"

CONNECTION_STRING = 'HostName=...
TEMPERATURE = 20.0 
HUMIDITY = 60
CONSTANT = 60

MSG_TXT = '{{"temperature": {temperature},"humidity": {humidity} }}'
MSG = '{{"temperature": {temperature}, "humidity": {humidity}, "heading": {heading}, "proximity": {proximity}, "pressure": {pressure}, "voltage": {voltage}, "currentRoom": {currentRoom}  }}'

msg = receiveMsg + "-\t-\t-\t-\t-\t-\t-"
room = ''

def getElement(data, str):
    tmp = data.split('\t')
    for i in range(len(tmp)):
        if (str.lower() in tmp[i].lower()):
            ind = tmp[i].lower().find(' = ') + 3
            return float(tmp[i].lower()[ind:])
    return None

def iothub_client_init():  
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)  
    return client 



# gets local IP of current device
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main():
    IP = get_ip()
    print ("Program Begin\t", "IP: ", IP)

    chargeFlag = False
    driveFlag = False

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with serverSocket as s:
        s.bind((IP, PORT))
        s.listen()

        try:
            client = iothub_client_init()
            print ('IOT Hub Device sending periodic messages, press Ctrl-C to exit')
        except:
            print ('IOTHubClient sample stopped')

        while(True):
            global msg, room
            
            (clientConnected, clientAddress) = serverSocket.accept()
            #print ("Accepted connection request from %s, %s" % (clientAddress[0], clientAddress[1]))

            data = clientConnected.recv(1024)
            decData = data.decode()

            data = decData.split('\t')
            print (decData)




            msg_txt_formatted = MSG.format(temperature=getElement(decData, "tmp"), humidity=getElement(decData, "hum"), heading=getElement(decData, "hd"), proximity=getElement(decData, "prx"), pressure=getElement(decData, "psi"), voltage=getElement(decData, "volt"), currentRoom=room )  #MSG_TXT.format(temperature=temperature, humidity=humidity)
            message = Message(msg_txt_formatted)
            #if temperature > 30:
            #  message.custom_properties["temperatureAlert"] = "true"
            #else:
            #  message.custom_properties["temperatureAlert"] = "false"


            print(msg)
            clientConnected.send(msg.encode())

            if (not (msg == receiveMsg + "-\t-\t-\t-\t-\t-\t-")):
                msg = "-\t-\t-\t-\t-\t-\t-"


            #BATTERY LOGIC
            v = getElement(decData, "volt")
            print ("Voltage", v, chargeFlag)
            if(v < BATTERY_LOW and not chargeFlag):
                chargeFlag = True
                driveFlag = False
                msg = receiveMsg + "1\t-\t-\t-\t1\t-\t-"
                print ('AUTO DOCK')
            if(v > BATTERY_HIGH and not driveFlag):
                driveFlag = True
                chargeFlag = False
                msg = receiveMsg + "4\t-\t-\t-\t-\t-\t-"
                print ('AUTO CLEAN')


            #msg = receiveMsg + "4\t-\t-\t-\t-\t-\t-"
            # if(len(inp) > 0):
            #    msg = receiveMsg + "4\t-\t-\t-\t-\t-\t-"

            #if not (charger_state == 2) and battery_capacity < CONSTANT:
            #    msg = receiveMsg + "4\t-\t-\t-\t1\t-\t-"

            #print(msg)
            #clientConnected.send(msg.encode())

            print( "Sending message: {}".format(message) )
            client.send_message(message)
            print ( "Message successfully sent" )
            #time.sleep(1)

def main2():
    global msg
    while True:
        inp = input()
        if (inp == 'c'):
            msg = receiveMsg + "4\t-\t-\t-\t-\t-\t-"
            print('CLEAN')
        if (inp == 'd'):
            msg = receiveMsg + "1\t-\t-\t-\t1\t-\t-"
            print('DOCK')

def main3():
    global room
    try:
        cap = cv2.VideoCapture("http://10.0.0.4:8000/stream.mjpg")
        cap.set(3, 960)
        cap.set(4, 720)

        while True:
            success, img = cap.read()

            for barcode in decode(img):
                room_raw = barcode.data.decode()
                room = int(room_raw.replace("room", ""))
                #print(room_raw,  room)
                color = (0, 255, 0)
                stroke = 2
                cv2.rectangle(img, (barcode.rect.left, barcode.rect.top),
                              (barcode.rect.left + barcode.rect.width, barcode.rect.top + barcode.rect.height), color,
                              stroke)
                cv2.putText(img, barcode.data.decode(), (barcode.rect.left, barcode.rect.top), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, color, stroke)

            # cv2.imshow('Result',img)
            cv2.waitKey(1)

        cap.release()
        cv2.destroyAllWindows()
    except:
        print('Stream Error')


thread1 = threading.Thread(target=main)
thread1.start()

thread2 = threading.Thread(target=main2)
thread2.start()

thread3 = threading.Thread(target=main3)
thread3.start()

