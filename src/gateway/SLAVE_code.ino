#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define LED_PIN    10
#define LED_COUNT 8

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

#define SLAVE_ADDR 0x10

unsigned char cnt='A';
unsigned char tx[4];
unsigned char rainbowFlg = 0, rainbowAvailable = 0;
unsigned int rainbowSpeed = 0;

void setup(){
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif

  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(100); // Set BRIGHTNESS to about 1/5 (max = 255)
  
  Serial.begin(9600);
  Wire.begin(SLAVE_ADDR);
//  Wire.onRequest(sendToMaster);
  Wire.onReceive(receiceEvent);
  
    colorWipe(strip.Color(200,   200,   200), 50);
     colorWipe(strip.Color(0    , 0    , 0    ), 50); 
}

void loop(){
  if(rainbowAvailable){
    rainbow(rainbowSpeed);
  }
}

void receiceEvent(int rxSize){
  int idx=0;
  while(Wire.available()){
    tx[idx++] = Wire.read();
    Serial.println(tx[idx-1]);
  }
  
  colorWipe(strip.Color(0    , 0    , 0    ), 50);
  if(tx[0] == 0x00){
    colorWipe(strip.Color(tx[1], tx[2], tx[3]), 50);
    rainbowFlg = 0;
  }
  else{
    rainbowFlg = 1; 
    rainbowAvailable = 1;
    rainbowSpeed = tx[1];
  }
}
/*
void sendToMaster(){
  
  Wire.write(++cnt);
    
  if(cnt >= 'z'){
    cnt = 'A';
  }
}
*/
void colorWipe(uint32_t color, int wait) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
}

void rainbow(int wait) {
  for(long firstPixelHue = 0; firstPixelHue < 5*65536; firstPixelHue += 256) {
    for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
      int pixelHue = firstPixelHue + (i * 65536L / strip.numPixels());
      strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue)));
      if(!rainbowFlg){
        rainbowAvailable = 0;
        break;
      }
    }
    if(!rainbowFlg){
        rainbowAvailable = 0;
        break;
    }
    strip.show(); // Update strip with new contents
    delay(wait);  // Pause for a moment
  }
}

// bacguneun babo meongcheongeeeeeeeeee~~~

