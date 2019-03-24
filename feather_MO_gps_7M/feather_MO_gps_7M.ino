#include <TinyGPS++.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>


#define VBATPIN A7

const int chipSelect = 4;
   
 //feather uses Serial1 instead
static const uint32_t GPSBaud = 9600;

// The TinyGPS++ object
TinyGPSPlus gps;
Adafruit_BMP280 bmp;

static const uint32_t SERIAL_DEBUG = 0;

void setup()
{

  if(SERIAL_DEBUG==1){
    Serial.begin(115200);
    while (!Serial) {
      ; // wait for serial port to connect. Needed for native USB port only
    }
  }
  Serial1.begin(GPSBaud);
  
  //ss.begin(GPSBaud);

  if(SERIAL_DEBUG==1){
    Serial.println(F("Starting..."));
  }
  
  if (!SD.begin(chipSelect)) {
    if(SERIAL_DEBUG==1){
      Serial.println("Card failed, or not present");
    }
    // don't do anything more:
    return;
  }
  if(SERIAL_DEBUG==1){
    Serial.println("card initialized.");
  }
  
  if (!bmp.begin()) {
    if(SERIAL_DEBUG==1){
      Serial.println("Could not find a valid BMP085 sensor, check wiring!");
    }
    return;
  }

  pinMode(VBATPIN, INPUT);

  
}

float batteryLevel(void)
{
    float measuredvbat = analogRead(VBATPIN);
    measuredvbat *= 2;    // we divided by 2, so multiply back
    measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
    measuredvbat /= 1024; // convert to voltage
    //Serial.print("VBat: " ); Serial.println(measuredvbat);
    return measuredvbat;

}
void loop()
{

  String dataString = "";

  if(gps.location.isValid()){

      char sz[32] = "******";

      TinyGPSDate d = gps.date;
      TinyGPSTime t = gps.time;
      
      if (!d.isValid())
      {
        //Serial.print(F("********** "));
        dataString += String(sz);
      }
      else
      {
        char sz[32];
        sprintf(sz, "%02d/%02d/%02d ", d.month(), d.day(), d.year());
        //Serial.print(sz);
        dataString += String(sz);
        dataString +=",";
      }
      
      if (!t.isValid())
      {
        //Serial.print(F("******** "));
        dataString += String(sz);
      }
      else
      {
        char sz[32];
        sprintf(sz, "%02d:%02d:%02d ", t.hour(), t.minute(), t.second());
        //Serial.print(sz);
        dataString += String(sz);
        dataString +=",";
      }
      dataString += String(gps.location.lat(),8);
      dataString +=",";
      dataString += String(gps.location.lng(),8);
      dataString +=",";
      dataString += String(gps.altitude.meters(),3);
      dataString +=",";
      dataString += String(bmp.readPressure(),3);
      dataString +=",";
      dataString += String(bmp.readAltitude(),3);
      dataString +=",";
      dataString += String(bmp.readTemperature(),3);
      dataString +=",";
      dataString += String(batteryLevel(),3);

     // if(SERIAL_DEBUG==1){
     //   Serial.println(dataString);
     // }
      writeToFile(dataString);
  }
  
  smartDelay(1000);

  if (millis() > 5000 && gps.charsProcessed() < 10)
    if(SERIAL_DEBUG==1){
      Serial.println(F("No GPS data received: check wiring"));
    }
}

// This custom version of delay() ensures that the gps object
// is being "fed".
static void smartDelay(unsigned long ms)
{
  unsigned long start = millis();
  do 
  {
    while (Serial1.available())
      gps.encode(Serial1.read());
  } while (millis() - start < ms);
}

void writeToFile(String ds)
{

  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  File dataFile = SD.open("datalog.txt", FILE_WRITE);

  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println(ds);
    dataFile.close();
    // print to the serial port too:
    if(SERIAL_DEBUG==1){
      Serial.println(ds);
    }
  }
  // if the file isn't open, pop up an error:
  else {
    if(SERIAL_DEBUG==1){
      Serial.println("error opening datalog.txt");
    }
  }
}
