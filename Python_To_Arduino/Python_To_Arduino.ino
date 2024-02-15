#define RED_LIGHT 2

//String InBytes;
//int test[] = {1, 2, 3, 4, 5};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.write("In loop");
  if (Serial.available() > 0) {
    String inBytes = Serial.readStringUntil('\n');
    //Serial.write("Reached if statement");
    if (inBytes == "on") {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.write("LED on");
    }
    else if (inBytes == "off") {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.write("LED off");
    }
    else {
      Serial.write("Invalid Input. Try again");
    }
  }
}
