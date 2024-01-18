#define RED_LIGHT 2
String InBytes;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(RED_LIGHT, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String inBytes = Serial.readStringUntil('\n');
    if (inBytes == "on") {
      digitalWrite(RED_LIGHT, HIGH);
      Serial.write("LED on");
    }
    else if (inBytes == "off") {
      digitalWrite(RED_LIGHT, LOW);
      Serial.write("LED off");
    }
    else {
      Serial.write("Invalid Input. Try again");
    }
  }
}
