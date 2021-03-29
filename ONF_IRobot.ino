#include <Arduino_APDS9960.h>
#include <Arduino_HTS221.h>
#include <Arduino_LPS22HB.h>
#include <Arduino_LSM9DS1.h>

const int SERIAL_INTERVAL = 1000;
unsigned long last = 0;

int INTERVAL1 = 1000;
unsigned long lastUpdate = 0;
float temperature = 0;
float humidity = 0;
float pressure = 0;

int INTERVAL2 = 100;
unsigned long lastUpdate2 = 0;
int proximity = 0;
int r = 0, g = 0, b = 0;

int INTERVAL3 = 100000;
unsigned long lastUpdate3 = 0;
float x, y, z;
float Gyz = 0;
float GyroZError = 0;
unsigned long prvTime, currentTime, elapsedTime;

int INTERVAL4 = 100;
unsigned long lastUpdate4 = 0;
float voltage = 0;
int i = 0;
float v[] = {16, 16, 16, 16, 16, 16, 16, 16, 16, 16};  //length of 10

void setup() {
  Serial.begin(9600);
  pinMode(A0, INPUT);
  
  while (!Serial);
  if (!HTS.begin()) {
    Serial.println("Failed to initialize humidity temperature sensor!");
    while (1);
  }
  if (!BARO.begin()) {
    Serial.println("Failed to initialize pressure sensor!");
    while (1);
  }
  if (!APDS.begin()) {
    Serial.println("Error initializing APDS9960 sensor.");
    while (true); // Stop forever
  }
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  for(int i = 0; i < 1000; i++) {
    if (IMU.gyroscopeAvailable()) {
      IMU.readGyroscope(x, y, z);
      GyroZError += z;
      delay(5);
    }else{
      i--;
    }
  }
  GyroZError /= 1000.0;
}

void loop() {
  if(millis() - lastUpdate4 > INTERVAL4) {
    lastUpdate4 = millis();
    v[i] = analogRead(A0)*(15.3/948.0);
    if(i > 9) {
      i = 0;
    }
    i += 1;

    voltage = 0;
    for(int j = 0; j < 10; j++){
      voltage += v[j];
    }
    voltage /= 10;
  }

  if(millis() - lastUpdate > INTERVAL1){
    lastUpdate = millis();
    
    temperature = HTS.readTemperature(FAHRENHEIT) - 10;
    humidity = HTS.readHumidity();

    pressure = BARO.readPressure(PSI);
  }

  if(millis() - lastUpdate2 > INTERVAL2){
    lastUpdate2 = millis();
    
    // Check if a proximity reading is available.
    if (APDS.proximityAvailable()) {
      proximity = APDS.readProximity();
    }
  
    // check if a color reading is available
    if (APDS.colorAvailable()) {
      APDS.readColor(r, g, b);
    }
  }

  if(millis() - lastUpdate3 > INTERVAL3){
    lastUpdate3 = millis();
    Gyz = 0;
  }

  if (IMU.gyroscopeAvailable()) {
    currentTime = millis();
    elapsedTime = currentTime - prvTime;
    IMU.readGyroscope(x, y, z);
    Gyz += (z+GyroZError)*(elapsedTime/1000.0);
    prvTime = currentTime;
  }


  if (millis() - last > SERIAL_INTERVAL){
    last = millis();
  
    // print each of the sensor values
    Serial.print("Tmp = ");
    Serial.print(temperature);
    Serial.print("\t");
    Serial.print("Hum = ");
    Serial.print(humidity);
    Serial.print("\t");
    Serial.print("Psi = ");
    Serial.print(pressure);
    Serial.print("\t");
    
    Serial.print("Prx = ");
    Serial.print(proximity);
    Serial.print("\t");
    Serial.print("R = ");
    Serial.print(r);
    Serial.print("\t");
    Serial.print("G = ");
    Serial.print(g);
    Serial.print("\t");
    Serial.print("B = ");
    Serial.print(b);
    Serial.print("\t");
  
    Serial.print("Hd = ");
    Serial.print(Gyz);
    Serial.print("\t");

    Serial.print("Volt = ");
    Serial.print(voltage);
  
    Serial.println();
  }
}
