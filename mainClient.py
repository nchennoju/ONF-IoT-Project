from __future__ import division

import serial
from pycreate2 import Create2
import time
import socket

import Adafruit_PCA9685

SERVER_IP = "10.0.0.6"
SERVER_PORT = 65432

SERVO_MIN = 150
SERVO_MAX = 600

def getElement(data, str):
    tmp = data.split('\\t')
    for i in range(len(tmp)):
        if (str.lower() in tmp[i].lower()):
            ind = tmp[i].lower().find(' = ') + 3
            return float(tmp[i].lower()[ind:])
    return None

def isInt(s):
    try:
        int(s)
        return True
    except:
        return False

def isFloat(s):
    try:
        float(s)
        return True
    except:
        return False

def handleData(bot, data):
    if (len(data) == 7):
        if (data[1] == '0' and data[2] == '0'):
            bot.drive_stop()
        elif (isInt(data[1]) and isInt(data[2])):
            #DRIVE COMMAND
            print ('DRIVE')
        if (isInt(data[0]) and int(data[0]) == 0):
            #OFF mode
            bot.stop()
        elif (isInt(data[0]) and int(data[0]) == 1):
            #SAFE mode
            bot.safe()
        elif (isInt(data[0]) and int(data[0]) == 2):
            #PASSIVE mode
            bot.start()
        elif (isInt(data[0]) and int(data[0]) == 3):
            #FULL mode
            bot.full()
        elif (isInt(data[0]) and int(data[0]) == 4):
            #AUTO mode
            bot.drive_stop()
            bot.start()
            bot.clean()
        if(isInt(data[4]) and int(data[4]) == 1):
            #SEEK DOCK
            bot.safe()
            bot.drive_stop()
            bot.seek_dock()
            time.sleep(60)
        if(isInt(data[5])):
            if(int(data[5]) == 1):
                #TURN PAN/TILT LEFT
                print ('left')
            if(int(data[5]) == -1):
                #TURN PAN/TILT RIGHT
                print ('right')
        if(isInt(data[6])):
            if(int(data[6]) == 1):
                #TURN PAN/TILT UP
                print ('up')
            if(int(data[6]) == -1):
                #TURN PAN/TILT DOWN
                print ('down')


if __name__ == "__main__":

    '''pwm = Adafruit_PCA9685.PCA9685()
    print ('Servo TEST...', end = '\n\n')
    pwm.set_pwm(0, 0, SERVO_MIN)
    time.sleep(1)
    pwm.set_pwm(0, 0, SERVO_MAX)
    time.sleep(1)
    pwm.set_pwm(1, 1, SERVO_MIN)
    time.sleep(1)
    pwm.set_pwm(1, 1, SERVO_MAX)
    time.sleep(1)
    pwm.set_pwm(0, 0, int((SERVO_MIN + SERVO_MAX)/2))
    time.sleep(0.4)
    pwm.set_pwm(1, 1, int((SERVO_MIN + SERVO_MAX)/2))'''


    #Serial initialization
    ser = serial.Serial("/dev/ttyACM0", 9600)


    port = "/dev/ttyUSB0"
    #port = '/dev/tty.usbserial-DA01NX3Z'
    baud = {
        'default': 115200,
        #'alt': 19200  # shouldn't need this unless you accidentally set it to this
    }

    bot = Create2(port=port, baud=baud['default'])

    bot.start()

    bot.safe()

    print ('Starting ...')

    #[ [0,3]  represents robot state]	[ left motor power +/- 500max]	[ right motor power +/- 500max]	[ time to drive ]	[ seek dock ]
    # robot state: 0-OFF, 1-SAFE, 2-PASSIVE, 3-FULL, ' '-KEEP CURRENT STATE, 4-AUTO
    # seek dock: 0-FALSE, 1-TRUE
    dataSent = "-\t-\t-\t-\t-\t-\t-"

    initTime = time.time()

    bot.safe()
    #sensors = bot.get_sensors()
    while True:
        #try:
        #    sensors = bot.get_sensors()
        #except:
        #    print ('ERROR: corrupt sensors data')
        
        try:
            s = str(ser.readline())
            externalSensors = s[2:len(s) - 5].replace('\\t', '\t')
            #print (externalSensors)
        except:
            print ('ERROR: bad serial data')



        #FORMAT SENSOR VAL (tabs between values)
        dataStr = ''
        #for data in sensors:
        #     dataStr += str(data) + '\t'
        dataStr += externalSensors
        #print (dataStr)


        try:
            #Create a client socket
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            clientSocket.connect((SERVER_IP, SERVER_PORT)) #connect to server
            clientSocket.send(str(dataStr).encode()) #send message to client
            dataServer = clientSocket.recv(1024) #recieve data from server

            if(dataServer.decode()[0:7] == "MSG RCV"):
                print ("SUCCESS", end='\t')
            else:
                print ("ERROR: server side", end='/t')

            dataSent = dataServer.decode()[7:].split('\t')
            print (dataSent, end='\t')
            handleData(bot, dataSent) #method handles instructions from server

            clientSocket.close() #disconnect from server
        except:
            print ("Error connecting to server at ", SERVER_IP, end='\t')


        curTime = time.time()
        if (curTime - initTime >= 50):
            bot.reset()
            time.sleep(3)
            bot.wake()
            print ("---- WAKE ----")
            initTime = curTime
            time.sleep(2)
            #bot.start()
        print (curTime - initTime)
        #time.sleep(0.1)
