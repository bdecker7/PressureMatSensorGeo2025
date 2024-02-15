// #include <cstdint>
#include <Stream.h>

#define RED_LIGHT 2

const size_t NUM_MEASUREMENT_POINTS = 5;
int myArray[NUM_MEASUREMENT_POINTS] = {1, 2, 3, 4, 5};
// boolean first_loop = true;

void printToSerialIfEmpty(String str) {
  Serial.print(str);
  Serial.flush();
}

String intArrayToString(int intArray[], size_t numElements) {
  /* Create a string representation of an int array.
   * Output string has the form "[1,2,3,4,...]"
  */
  String arrayString = "[";
  for (size_t i = 0; i < numElements; i++) {
    arrayString += (String)intArray[i];
    if (i < numElements - 1) arrayString += ",";
  }
  arrayString += "]";
  return arrayString;
}

byte b1 = 8;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  // if (first_loop) {
  //   Serial.write("First Loop");
  //   first_loop = false;
  // }

  if (Serial.available() > 0) {
    String inBytes = Serial.readStringUntil('\n');

    if (inBytes == "on") {
      digitalWrite(LED_BUILTIN, HIGH);
      // Serial.write("LED on\n");
      // Serial.println("LED on");
      printToSerialIfEmpty("LED on");
    }
    else if (inBytes == "off") {
      digitalWrite(LED_BUILTIN, LOW);
      // Serial.write("LED off\n");
      printToSerialIfEmpty("LED off");
    }
    else if (inBytes == "write") {
      // Serial.println(myArray[3]);
      printToSerialIfEmpty(intArrayToString(myArray, NUM_MEASUREMENT_POINTS));
    }
    else {
      Serial.write("Invalid Input. Try again");
    }
  }
}
