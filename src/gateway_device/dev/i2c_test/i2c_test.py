import smbus

SLAVE_ADDR = 0x10

i2c = smbus.SMBus(1)

r=int(input())
g=int(input())
b=int(input())

i2c.write_i2c_block_data(SLAVE_ADDR,0x00,[r,g,b])
