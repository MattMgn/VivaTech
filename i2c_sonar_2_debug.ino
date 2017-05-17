#include <Wire.h>
#define SLAVE_ADDRESS 0x04
#define FLOATS_SENT 3
#include "Ultrasonic.h"

Ultrasonic ultrasonic1(3);
Ultrasonic ultrasonic3(5);
Ultrasonic ultrasonic5(7);

float data[FLOATS_SENT]; //faire des tests avec des int
int array_size = 4;
//int array_us_1[4];
float raw_float_us_1;
float raw_float_us_2;
float raw_float_us_3;
int cnt_false_1;
int cnt_false_2;
int cnt_false_3;
int raw_us_1;
int raw_us_2;
int raw_us_3;
int previous_raw_us_1;
int previous_raw_us_2;
int previous_raw_us_3;
int filt_us_1;
int filt_us_2;
int filt_us_3;

unsigned long previousMillis = 0; 
unsigned long currentMillis = 0;
unsigned long delta_time = 0;

int array_us_1[]  = {10, 20, 30, 40};
int array_us_2[]  = {10, 20, 30, 40};
int array_us_3[]  = {10, 20, 30, 40};

//byte data[] = {1,2,3,4};

void setup() {
    Serial.begin(9600);
    Wire.begin(SLAVE_ADDRESS);    
}

void loop() {
  // MAJ data 
  process_ultrasonic_data();
   // send data with i2c
  Wire.onRequest(sendData);
  delay(50);    
}

void sendData(){
  Wire.write((byte*) &data, FLOATS_SENT*sizeof(float));
}


void process_ultrasonic_data(){
  
//  // debug mode with timing
//  Serial.println("----- NEW SEQUENCE -----"); 
//  currentMillis = millis();
//  delta_time = currentMillis - previousMillis;
//  previousMillis = currentMillis;
//  Serial.print("delay between two scans : "); Serial.print(delta_time);Serial.println("ms");Serial.println("");
//  Serial.print("size of float : ,"); Serial.print(sizeof(float));
//  Serial.print("size of int : ,"); Serial.print(sizeof(int));
  
  // get raw data as float
  raw_float_us_1 = ultrasonic1.MeasureInCentimeters();
  raw_float_us_2 = ultrasonic3.MeasureInCentimeters();
  raw_float_us_3 = ultrasonic5.MeasureInCentimeters();
//  Serial.print("raw_float_us_1 : "); Serial.println(raw_float_us_1); Serial.println("");


  
  // transform raw data to integer (optimize speed computing and memory allocation)
  raw_us_1 = (int) raw_float_us_1;
  raw_us_2 = (int) raw_float_us_2;
  raw_us_3 = (int) raw_float_us_3;
//  Serial.print("raw_us_1 : "); Serial.println(raw_us_1); Serial.println("");

  // if (erroned value : >450) then keep last good value, else if (for 5 times, we have value>450) then keep this value, else (no erroned value) increment previous good value 'previous_raw_us_1'
  //if (raw_us_1>450) {raw_us_1 = previous_raw_us_1;} else{previous_raw_us_1 = raw_us_1;};
  //if (raw_us_2>450) {raw_us_2 = previous_raw_us_2;} else{previous_raw_us_2 = raw_us_2;};
  //if (raw_us_3>450) {raw_us_3 = previous_raw_us_3;} else{previous_raw_us_3 = raw_us_3;};
  
  if (raw_us_1>450 && cnt_false_1<5) {raw_us_1 = previous_raw_us_1; ++cnt_false_1;} else if (raw_us_1>450 && cnt_false_1<=5) {cnt_false_1=0; previous_raw_us_1 = raw_us_1;} else{previous_raw_us_1 = raw_us_1;};
  if (raw_us_2>450 && cnt_false_2<5) {raw_us_2 = previous_raw_us_2; ++cnt_false_2;} else if (raw_us_2>450 && cnt_false_2<=5) {cnt_false_2=0; previous_raw_us_2 = raw_us_2;} else{previous_raw_us_2 = raw_us_2;};
  if (raw_us_3>450 && cnt_false_3<5) {raw_us_3 = previous_raw_us_3; ++cnt_false_3;} else if (raw_us_3>450 && cnt_false_3<=5) {cnt_false_3=0; previous_raw_us_3 = raw_us_3;} else{previous_raw_us_3 = raw_us_3;};

  // rotate us array
//  Serial.print("array_us_1 before rotation : ");for(int i = 0; i < array_size; i++) {Serial.print(array_us_1[i]);Serial.print(",");}; Serial.println("");
  circular_array_rotation(array_us_1);
  circular_array_rotation(array_us_2);
  circular_array_rotation(array_us_3);
//  Serial.print("array_us_1 after rotation : ");for(int i = 0; i < array_size; i++) {Serial.print(array_us_1[i]);Serial.print(",");}; Serial.println("");
  
  // populate with new data
  array_us_1[0] = raw_us_1;
  array_us_2[0] = raw_us_2;
  array_us_3[0] = raw_us_3;
//  Serial.print("array_us_1 after populating : ");for(int i = 0; i < array_size; i++) {Serial.print(array_us_1[i]);Serial.print(",");}; Serial.println("");
  
  // compute filtered value
  filt_us_1 = filtering_array(array_us_1);
  filt_us_2 = filtering_array(array_us_2);
  filt_us_3 = filtering_array(array_us_3);
//  Serial.print("filt_us_1 : "); Serial.println(filt_us_1); Serial.println("");
  
  // populate data to be sent
  data[0] = filt_us_1;
  data[1] = filt_us_2;
  data[2] = filt_us_3;
  
//  data[0] = ultrasonic1.MeasureInCentimeters();
//  data[1] = ultrasonic3.MeasureInCentimeters();
//  data[2] = ultrasonic5.MeasureInCentimeters();

//  Serial.print("raw  : "); Serial.print(raw_float_us_1);Serial.print(" | if_filt : "); Serial.print(raw_us_1);Serial.print(" | filt : "); Serial.println(filt_us_1);

}

void circular_array_rotation(int *array){
  // right rotation of 'array' of size 'array_size'
  int temp = array[array_size-1];
  for( int i=array_size-1; i>=1; i--){
    array[i]=array[i-1];
  }
  array[0] = temp;
}

int filtering_array(int *array){
  //basic filtering
  int filtered_value = (4*array[0] + 1*array[1] + 0.5*array[2] + 0.5*array[3]) / (6);
  return filtered_value;
}
