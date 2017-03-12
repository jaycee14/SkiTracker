/*
  SD card basic file example

 This example shows how to create and destroy an SD card file
 The circuit:
 * SD card attached to SPI bus as follows:
 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 4 (for MKRZero SD: SDCARD_SS_PIN)

 created   Nov 2010
 by David A. Mellis
 modified 9 Apr 2012
 by Tom Igoe

 This example code is in the public domain.

 */
#include <SPI.h>
#include <SD.h>

File myFile;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }


  Serial.print("Initializing SD card...");

  if (!SD.begin(4)) {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialization done.");

  if (SD.exists("datalog.txt")) {
    Serial.println("datalog.txt exists.");

    // delete the file:
    Serial.println("Removing datalog.txt...");
    SD.remove("datalog.txt");

    if (SD.exists("datalog.txt")) {
      Serial.println("something went wrong with the delete");
    } else {
      Serial.println("delete complete");
    }

    
  } else {
    Serial.println("datalog.txt doesn't exist.");
  }

  
}

void loop() {
  // nothing happens after setup finishes.
}



