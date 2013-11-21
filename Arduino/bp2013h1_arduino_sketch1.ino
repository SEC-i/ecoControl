#include "LED_Bar.h"
#include <math.h>

int led_pin = 3;
int relay_pin = 4;

int plant1_value = 0;
int plant2_value = 0;
int temperature_value = 0;

int led_bar_value = 0;
int B=3975; //B value of the thermistor

float temperature = 0.0f;
float resistance = 0.0f;
float light_value = 0.0f;

LED_Bar led_bar;

void setup() {
  pinMode(led_pin, OUTPUT);
  pinMode(relay_pin, OUTPUT);
  Serial.begin(9600);
  led_bar.set_LED_Index(0b000001101010101,0b0000000010101010);
}

void loop() {
    plant1_value = analogRead(A0);
    plant2_value = analogRead(A1);
    light_value = analogRead(A2); // mapped to range 0-100
    temperature_value = analogRead(A3);

    //temperature mapping to celsius
    resistance=(float)(1023-temperature_value)*10000/temperature_value;
    temperature=1/(log(resistance/10000)/B+1/298.15)-273.15;
    
    led_bar_value = round(plant1_value/80); // min: 0, max: 800
    led_bar.set_LED_Range(1,led_bar_value);

    if(plant1_value > 300 and plant2_value > 300){
        digitalWrite(led_pin,HIGH); 
    }else{
        digitalWrite(led_pin,LOW);
    }
    
    Serial.print("{ \"plant1_value\": ");
    Serial.print(plant1_value);
    Serial.print(", \"plant2_value\": ");
    Serial.print(plant2_value);
    Serial.print(", \"light_value\": ");
    Serial.print(light_value);
    Serial.print(", \"temperature_value\": ");
    Serial.print(temperature);
    Serial.println(" }");
    
    delay(1000);        
}