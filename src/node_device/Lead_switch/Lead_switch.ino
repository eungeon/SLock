#include <SoftwareSerial.h>
#include <string.h>

#define ADDR 0x10

#define GET 0x00
#define SET 0x01
#define RES 0x10

#define DOOR_SEN 0x10
#define DOOR_LOCK 0x20
#define EM_LOCK 0x30

#define OPEN 0x01
#define CLOSE 0x00

SoftwareSerial BT(2, 3); // TX, RX
SoftwareSerial RF(4, 5); // TX, RX

void RF_Response(unsigned char* tx, unsigned char act,unsigned char ctrl,unsigned char val);

int leadSW = 6;
unsigned char RF_rx[4];
bool RF_en = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  BT.begin(9600);
  RF.begin(9600);

  pinMode(leadSW,INPUT_PULLUP);
}

int action=0, control=0, value=0;

void loop() {
  if(RF.available()){
    Serial.print("MJ447RTX : ");
    RF.readBytes(RF_rx,4);
    RF_en = true;
  }
   
  if(Serial.available()){
    BT.write(Serial.read());
  }
  if(BT.available()){
    Serial.write(BT.read());
  }

  if(RF_en){
    for(int i=0; i<4; i++){
      Serial.print("0x");
      Serial.print(RF_rx[i],16);  
      Serial.print(' ');
    }
    Serial.println(" ");
    
    //Serial.println(RF_rx[0]);
    if(RF_rx[0] == ADDR){
      Serial.println("Receive");
      action = RF_rx[1];
      control = RF_rx[2];
      value = RF_rx[3];
      
      unsigned char buf[4];
      RF_Response(buf, RF_rx[1],RF_rx[2],RF_rx[3]);
      //delay(5000);
      RF.write(buf,4);
      Serial.write(buf,4);
      Serial.println("");
      for(int i=0; i<4; i++){
        Serial.print("0x");
        Serial.print(buf[i],16); 
        Serial.print(' '); 
      }
    Serial.println("");
    }
    memset(RF_rx, 0, 4);
    RF_en = false;
  }
}

void RF_Response(unsigned char* tx, unsigned char act,unsigned char ctrl,unsigned char val){
  tx[0] = ADDR;
  tx[1] = RES;
  tx[2] = ctrl;
  
  if(act == GET){
    switch(ctrl & 0xF0){
        case DOOR_SEN:
          tx[3] = digitalRead(leadSW) ? OPEN : CLOSE;
          break;
        case DOOR_LOCK:
        
        case EM_LOCK:
        
        default:
          tx[3] = 0xFF;
          break;
    }
  }
  else if(act == SET){
    switch(ctrl & 0xF0){
      case DOOR_LOCK:

      case EM_LOCK:
      
      case DOOR_SEN:
        
      default:
        tx[3] = 0xFF;
        break;
    }
  }
  else{
    tx[3] = 0xFF;
  }
}
