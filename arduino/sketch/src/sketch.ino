#include "LED_Bar.h"
#include <math.h>

// analog sensor mapping
#define PLANT_SENSOR_1 A0
#define PLANT_SENSOR_2 A1
#define PLANT_SENSOR_3 A2
#define VOLTAGE_SENSOR A3
#define LIGHT_SENSOR A4
#define TEMPERATURE_SENSOR A5

#define THERMISTOR_VALUE 3975 //B value of the thermistor

LED_Bar led_bar;

int led_pin = 3;
int relay_pin = 4;

int plant1_value = 0;
int plant2_value = 0;
int plant3_value = 0;
float voltage_value = 0.0f;
float temperature_value = 0;
int light_value = 0;

int led_bar_value = 0;

int incomingByte = 0; // for incoming serial data
int relay_delay = 0;
bool relay_delay_counting = false;

void setup() {
    // set up pins and serial baud rate
    pinMode(led_pin, OUTPUT);
    pinMode(relay_pin, OUTPUT);
    Serial.begin(9600);
    led_bar.set_LED_Index(0b000001101010101,0b0000000010101010);
}

void loop() {
    // read sensor data
    plant1_value = analogRead(PLANT_SENSOR_1);
    plant2_value = analogRead(PLANT_SENSOR_2);
    plant3_value = analogRead(PLANT_SENSOR_3);
    voltage_value = get_voltage_value();
    light_value = analogRead(LIGHT_SENSOR);
    temperature_value = get_temperature_value();

    set_led_bar();
    
    if (Serial.available() > 0) { // check if serial input is available
        // turn status led on
        digitalWrite(led_pin,HIGH); 
        
        // read data
        incomingByte = Serial.read();

        if (incomingByte == 49){ // turn relay on if input was ASCII "1"
            digitalWrite(relay_pin,HIGH);
            Serial.println("{ \"relay_state\": 1 }");
        } else if (incomingByte == 50) { // turn relay on if input was ASCII "2"
            digitalWrite(relay_pin,LOW);
            Serial.println("{ \"relay_state\": 0 }");
        } else if (incomingByte == 51) { // turn relay on if input was ASCII "3"
            digitalWrite(relay_pin,HIGH);
            Serial.println("{ \"relay_state\": 1 }");
            relay_delay = 30 /2; //30s
            relay_delay_counting = true;
        } else { // otherwise, reply with sensor data
            
            // print data in json format
            Serial.print("{ \"plant1_value\": ");
            Serial.print(plant1_value);
            Serial.print(", \"plant2_value\": ");
            Serial.print(plant2_value);
            Serial.print(", \"plant3_value\": ");
            Serial.print(plant3_value);
            Serial.print(", \"battery_value\": ");
            Serial.print(voltage_value, 2);
            Serial.print(", \"light_value\": ");
            Serial.print(light_value);
            Serial.print(", \"temperature_value\": ");
            Serial.print(temperature_value, 2);
            Serial.println(" }");
        }

        // delay loop and turn status led off
        delay(100);
        digitalWrite(led_pin,LOW);
    } else {
        if(relay_delay_counting){
            if(relay_delay > 0){
                relay_delay--;
            }else{
                relay_delay = 0;
                relay_delay_counting = false;
                digitalWrite(relay_pin,LOW);
            }
        }
    }
}

float get_temperature_value()
{
    int sensor_value;
    float resistance = 0.0f;
    sensor_value = analogRead(TEMPERATURE_SENSOR);
    // temperature mapping to celsius
    resistance=(float)(1023-sensor_value)*10000/sensor_value;
    return 1/(log(resistance/10000)/THERMISTOR_VALUE+1/298.15)-273.15;
}

float get_voltage_value()
{
    // voltage probing (takes 2s)
    long sum=0;
    for(int i=0;i<1000;i++)
    {  
        sum=voltage_value+sum;
        voltage_value=analogRead(VOLTAGE_SENSOR);
        delay(2);
    }   
    // voltage mapping
    return 10*(sum/1000)*4980/(1023.00*1000) * (12.96/14.07); // voltmeter used to determine last factor
}

void set_led_bar()
{
    // set led bar accordingly to solar value
    led_bar_value = round((voltage_value-10.0)/4.0*10); // min: 10V max: 14V
    led_bar_value = max(min(led_bar_value,10),0); // make sure led_bar_value is in range 0-10
    led_bar.set_LED_Range(1,led_bar_value);
}