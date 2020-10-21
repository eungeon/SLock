from time import sleep
import serial
import pymysql.cursors
import smbus
import signal
import sys

# define
SLAVE_ADDR = 0x10

SEN_ADDR = 0x10
LOCK_ADDR = 0x20

GET = 0x00
SET = 0x01
RES = 0x10

DOOR_SEN = 0x10
DOOR_LOCK = 0x20
EM_LOCK = 0x30

OPEN = 0x01
CLOSE = 0x00

# neopixel set with i2c
neoPixel = smbus.SMBus(1)

# MJ447RTX module set with UART
RF = serial.Serial("/dev/ttyAMA0", 9600, timeout = 1)

vals = [SEN_ADDR, 0x00, 0x10, 0x00]
oldRfData = bytes(1)
rfRx = []
mainDoor = 101

def SetColor(mode,r,g,b):
    neoPixel.write_i2c_block_data(SLAVE_ADDR,int(mode),[int(r),int(g),int(b)])

# ctrl+C signal Handler
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    print("Closing")
    SetDeviceConnection(0x00, False)
    conn.close()
    SetColor(0x00, 0, 0, 0)
    sys.exit(0)

def GetDB(table):
    rows = []
    try:
        with conn.cursor() as curs:
            conn.commit()
            selectSql = "SELECT * FROM " + table
            curs.execute(selectSql,)
            rows = curs.fetchall()
        #print(rows)
    finally:
        return rows

def GetDeviceStatus():
    rows = []
    try:
        with conn.cursor() as curs:
            selectSql = "SELECT * FROM Device"
            curs.execute(selectSql)
            rows = curs.fetchall()
        conn.commit() 
        #print(rows)
    finally:
        return rows

def GetStatus():
    try:
        with conn.cursor() as curs:
            conn.commit()
            selectSql = "SELECT * FROM door"
            curs.execute(selectSql)
            rows = curs.fetchall()
        print(rows)
    finally:
        return rows

def SetDeviceConnection(addr, status):
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as curs:
            updateSql = "UPDATE Device SET connect=%s WHERE addr=%s"
            curs.execute(updateSql, (status,addr))
        conn.commit()
    finally:
        pass

def SetDoorSensor(d_num, d_flg):
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as curs:
            updateSql = "UPDATE door SET d_flg=" + str(d_flg) + " WHERE d_num=" + str(d_num)
            updateSql = "UPDATE door SET d_flg=%s WHERE d_num=%s"
            print(curs.execute(updateSql, (d_flg, d_num)))
        conn.commit()
    finally:
        pass

try:
    
    signal.signal(signal.SIGINT, signal_handler)

    if __name__ == '__main__':
        # initializing Neopixel
        SetColor(0x01, 10, 0, 0)
        sleep(2)

        #connect to MySQL server
        conn = pymysql.connect(
            host='192.168.1.12',
            user='root',
            password='k06120393@',
            db='slock',
            charset='utf8')

        SetColor(0x00, 0, 0, 0)
        sleep(2)

        oldDoorStatus = []
        oldDeviceStatus = []

        SetDeviceConnection(0x00, True)     

        while True:
            # Door lock Setting
            doorStatus = GetDB('door')
            deviceStatus = GetDB('device')
            #print(doorStatus)
            for door in doorStatus:
                for device in deviceStatus:
                    if door[0] in device:
                        for i in range(3,5):
                            if device[i] == True:
                                if i == 3:
                                    controlDevice = DOOR_LOCK
                                elif i == 4:
                                    controlDevice = EM_LOCK
                                else:
                                    continue

                                RF.write(bytearray([device[0], SET, controlDevice, door[2]]))
                                print("command : " + '0x'+'{0:02X}'.format(device[0]),'0x'+'{0:02X}'.format(SET),'0x'+'{0:02X}'.format(controlDevice),'0x'+'{0:02X}'.format(door[2]))

                                while RF.readable():
                                    del rfRx[0:]
                                    for i in range(0,4):
                                        rfRx.append(RF.read())
                                    #print(rfRx)

                                    if rfRx[0] != '':
                                        rfData = bytearray(rfRx)
                                        print("receive : " + '0x'+'{0:02X}'.format(rfData[0]),'0x'+'{0:02X}'.format(rfData[1]),'0x'+'{0:02X}'.format(rfData[2]),'0x'+'{0:02X}'.format(rfData[3]))
                                        if rfData == bytearray([device[0], RES, controlDevice, door[2]]):
                                            SetDeviceConnection(device[0], True)
                                        else:
                                            print("communication Error")
                                            SetDeviceConnection(device[0], False)
                                    else:
                                        print("not communicate")
                                        SetDeviceConnection(device[0], False)
                                    break
            
            for device in deviceStatus:
                if device[2] == True:
                    RF.write(bytearray([device[0], GET, DOOR_SEN, 0x00]))
                    print("command : " + '0x'+'{0:02X}'.format(device[0]),'0x'+'{0:02X}'.format(GET),'0x'+'{0:02X}'.format(DOOR_SEN),'0x'+'{0:02X}'.format(0))

                    while RF.readable():
                        del rfRx[0:]
                        for i in range(0,4):
                            rfRx.append(RF.read())
                        #print(rfRx)

                        if rfRx[0] != '':
                            rfData = bytearray(rfRx)
                            print("receive : " + '0x'+'{0:02X}'.format(rfData[0]),'0x'+'{0:02X}'.format(rfData[1]),'0x'+'{0:02X}'.format(rfData[2]),'0x'+'{0:02X}'.format(rfData[3]))
                            if rfData[:3] == bytearray([device[0], RES, DOOR_SEN]):
                                SetDeviceConnection(device[0], True)
                                print(rfData[3] == CLOSE and "Close" or "Open")
                                if rfData[3] == CLOSE:
                                    SetDoorSensor(device[1], CLOSE)
                                    if device[1] == mainDoor and oldRfData != rfData[3]:
                                        SetColor(0x00, 0, 200, 0)
                                        oldRfData = rfData[3]        
                                elif rfData[3] == OPEN:
                                    SetDoorSensor(device[1], OPEN)
                                    if device[1] == mainDoor and oldRfData != rfData[3]:
                                        SetColor(0x00, 200, 0, 0)
                                        oldRfData = rfData[3]
                                else:
                                    pass
                            else:
                                print("communication Error")
                                SetDeviceConnection(device[0], False)
                                if device[1] == mainDoor:
                                    SetColor(0x00, 200, 100, 0)
                                    oldRfData = 0xFF
                                    
                        else:
                            print("not communicate")
                            SetDeviceConnection(device[0], False)
                            if device[1] == mainDoor:
                                SetColor(0x00, 200, 100, 0)
                                oldRfData = 0xFF
                        break

except Exception as e : 
    print(str(e)) 
    pass
