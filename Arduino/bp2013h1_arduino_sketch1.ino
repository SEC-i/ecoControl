#include "LED_Bar.h"
#include <math.h>

int led_pin = 3;
int relay_pin = 4;

int plant1_value = 0;
int plant2_value = 0;
int temperature_value = 0;
int light_value = 0;

int led_bar_value = 0;
int B=3975; //B value of the thermistor

int incomingByte = 0; // for incoming serial data

float temperature = 0.0f;
float resistance = 0.0f;

LED_Bar led_bar;

void setup() {
    // set up pins and serial baud rate
    pinMode(led_pin, OUTPUT);
    pinMode(relay_pin, OUTPUT);
    Serial.begin(9600);
    led_bar.set_LED_Index(0b000001101010101,0b0000000010101010);
}

void loop() {
    // read sensor data
    plant1_value = analogRead(A0);
    plant2_value = analogRead(A1);
    light_value = analogRead(A2);
    temperature_value = analogRead(A3);

    // set led bar accordingly to plant1_value
    led_bar_value = round(plant1_value/80); // min: 0, max: 800
    led_bar.set_LED_Range(1,led_bar_value);

    
    if (Serial.available() > 0) { // check if serial input is available
        // turn status led on
        digitalWrite(led_pin,HIGH); 
        
        // read data
        incomingByte = Serial.read();

        if (incomingByte == 49){ // turn relay on if input was ASCII "1"
            digitalWrite(relay_pin,HIGH);
            Serial.println("{ \"relay_state\": 1 }");
        } else if (incomingByte == 50) { // turn relay on if input was ASCII "1"
            digitalWrite(relay_pin,LOW);
            Serial.println("{ \"relay_state\": 0 }");
        } else { // otherwise, reply with sensor data

            // temperature mapping to celsius
            resistance=(float)(1023-temperature_value)*10000/temperature_value;
            temperature=1/(log(resistance/10000)/B+1/298.15)-273.15;
            
            // print data in json format
            Serial.print("{ \"plant1_value\": ");
            Serial.print(plant1_value);
            Serial.print(", \"plant2_value\": ");
            Serial.print(plant2_value);
            Serial.print(", \"light_value\": ");
            Serial.print(light_value);
            Serial.print(", \"temperature_value\": ");
            Serial.print(temperature);
            Serial.println(" }");
        }

        // delay loop and turn status led off
        delay(100);
        digitalWrite(led_pin,LOW);
    } else {
        // delay the loop if there was no input
        delay(250); 
    }
}