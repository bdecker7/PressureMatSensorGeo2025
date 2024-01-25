#define MUX_S0 2
#define MUX_S1 3
#define MUX_S2 4

int inputState = 0;
unsigned long currentMillisMux;
unsigned long startMillisMux;
unsigned long period = 1000;

bool address1[8] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool address2[8] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool address3[8] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};

void multiplexerFunction();

void setup() {
    Serial.begin(9600);
    pinMode(MUX_S0, OUTPUT);
    pinMode(MUX_S1, OUTPUT);
    pinMode(MUX_S2, OUTPUT);
    pinMode(5, OUTPUT);
    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);
    digitalWrite(MUX_S0, LOW);
    digitalWrite(MUX_S1, LOW);
    digitalWrite(MUX_S2, LOW);

    startMillisMux = millis();
}

void loop() {
  digitalWrite(MUX_S0, LOW);
  digitalWrite(MUX_S1, LOW);
  digitalWrite(MUX_S2, LOW);
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  digitalWrite(7, HIGH);
  /*
  currentMillisMux = millis();
  if ((currentMillisMux - startMillisMux) >= period) {
    startMillisMux = currentMillisMux;
    digitalWrite(MUX_S0, address1[inputState]);
    digitalWrite(MUX_S1, address2[inputState]);
    digitalWrite(MUX_S2, address3[inputState]);
    inputState += 1;
    if (inputState == 8) {
      inputState = 0;
    }
  }
  */
}
