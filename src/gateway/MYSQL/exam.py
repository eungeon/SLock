import pymysql

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


"""
try:
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        selectSql = "SELECT * FROM Main_door"
        cur.execute(selectSql)
        rows = cur.fetchall()
        print(rows)

finally:
    conn.close()
"""

conn = pymysql.connect(
    host='slock.ctavaa2ygslv.us-east-2.rds.amazonaws.com',
    user='woskaangel',
    password='k06120393',
    db='slock',
    charset='utf8')

deviceStatus = []

def DetectChange():
    try:
        with conn.cursor() as curs:
            selectSql = "SELECT * FROM Device"
            curs.execute(selectSql)
            rows = curs.fetchall()
        #print(rows)
        global deviceStatus
        if rows != deviceStatus:
            value = True
            print("Device status is Changed")
            deviceStatus = rows
        else:
            value = False
            print("Device status is Not Changed")
    finally:
        return value


def GetStatus():
    try:
        with conn.cursor() as curs:
            selectSql = "SELECT * FROM door"
            curs.execute(selectSql)
            rows = curs.fetchall()
        print(rows)
    finally: 
        return rows

DetectChange()
status = GetStatus()
conn.close()

for door in status:
    for device in deviceStatus:
        if door[0] in device:
            cmd = [4]
            cmd[0] = device[0]
            cmd[1] = SET
            for i in range(3,5):
                cmd[2] = 
            print(device)
"""
if 101 in status[0]:
    print("Asdf")
else:
    print("qwerqwer")

for i in status:
    for j in deviceStatus:
        print(j.index(i))
"""      