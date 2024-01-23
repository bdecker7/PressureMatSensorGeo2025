/*
#define ADDRESS1 22
#define ADDRESS2 24
#define ADDRESS3 26

#define MUX_S0 32
#define MUX_S1 34
#define MUX_S2 36
*/

#define ADDRESS1 22
#define ADDRESS2 24
#define ADDRESS3 26

int outputState = 0;
int inputState = 0;
unsigned long startMillisDeMux;
unsigned long currentMillisDeMux;
unsigned long currentMillisMux;
unsigned long startMillisMux;
unsigned long period = 1000;

bool address1[8] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool address2[8] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool address3[8] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};

void multiplexerFunction();

void setup() {
    Serial.begin(9600);
    pinMode(ADDRESS1, OUTPUT);
    pinMode(ADDRESS2, OUTPUT);
    pinMode(ADDRESS3, OUTPUT);
    //pinMode(MUX_S0, OUTPUT);
    //pinMode(MUX_S1, OUTPUT);
    //pinMode(MUX_S2, OUTPUT);
    digitalWrite(ADDRESS1, LOW);
    digitalWrite(ADDRESS2, LOW);
    digitalWrite(ADDRESS3, LOW);
    //digitalWrite(MUX_S0, HIGH);
    //digitalWrite(MUX_S1, LOW);
    //digitalWrite(MUX_S2, LOW);

    pinMode(40, OUTPUT);
    digitalWrite(40, LOW);

    startMillisDeMux = millis();
    startMillisMux = millis();
}

//FIXME I think we need to use smaller resistors since we have two LEDs in series. Either that, or pump up the power. A 200 ohm resistor should be fine, instead of the 260 resistors we have

void loop() {
  currentMillisDeMux = millis();
  if ((currentMillisDeMux - startMillisDeMux) >= period) {
    startMillisDeMux = currentMillisDeMux;
    digitalWrite(ADDRESS1, address1[outputState]);
    digitalWrite(ADDRESS2, address2[outputState]);
    digitalWrite(ADDRESS3, address3[outputState]);
    //multiplexerFunction();
    outputState += 1;
    if (outputState == 8) {
      outputState = 0;
    }
  }
}

void multiplexerFunction() {
  currentMillisMux = millis();
  if ((currentMillisMux - startMillisMux) >= period) {
    
  }
}