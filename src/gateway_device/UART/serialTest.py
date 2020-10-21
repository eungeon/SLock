from time import sleep
import serial
import smbus


SLAVE_ADDR = 0x10
OPEN = 0x01
CLOSE = 0x00

neoPixel = smbus.SMBus(1)

RF = serial.Serial("/dev/ttyAMA0",9600,timeout=1)

# ser.writelines("OK")
# print("sent")

#vals = [0x20, 0x01, 0x30, OPEN] 
vals = [0x20, 0x01, 0x30, CLOSE] 
#vals = [0x10, 0x00, 0x10, 0x00] 
RF.write(bytearray(vals))
#rfRes = bytearray(4)
oldRfRes = bytearray(1)
temp = []

if __name__ == '__main__':
    while True:
        RF.write(bytearray(vals))
        print("sent")
        
        while RF.readable():
            #print("sent2")
            del temp[0:]
            for i in range(0,4):
                temp.append(RF.read())
            #print(temp)
            if temp[0] != '':
                rfRes = bytearray(temp)
                print('0x'+'{0:02X}'.format(rfRes[0]),'0x'+'{0:02X}'.format(rfRes[1]),'0x'+'{0:02X}'.format(rfRes[2]),'0x'+'{0:02X}'.format(rfRes[3]))
                #print(rfRes)
                if oldRfRes != rfRes[3]:
                    print(rfRes[3] == CLOSE and "Close" or "Open")
                    if rfRes[3] == CLOSE:
                        neoPixel.write_i2c_block_data(SLAVE_ADDR,int(0x00),[int(0),int(200),int(0)])
                    elif rfRes[3] == OPEN:
                        neoPixel.write_i2c_block_data(SLAVE_ADDR,int(0x00),[int(200),int(0),int(0)])
                    oldRfRes = rfRes[3]
            #print("sent3")
            else:
                print("not communicate")
                if(oldRfRes != 0xFF):
                    neoPixel.write_i2c_block_data(SLAVE_ADDR,int(0x00),[int(200),int(100),int(0)])
                    oldRfRes = 0xFF
            break
        
        sleep(3)
        #print("sent4")
        #command = input('Enter the Command.\n> ')
        #ser.writelines([1,2,3,4])
