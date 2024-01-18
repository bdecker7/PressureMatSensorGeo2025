#define ADDRESS1 22
#define ADDRESS2 24
#define ADDRESS3 26

int outputState = 0;
int inputState = 0;
unsigned long startMillis;
unsigned long currentMillis;
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
    digitalWrite(ADDRESS1, LOW);
    digitalWrite(ADDRESS2, LOW);
    digitalWrite(ADDRESS3, LOW);
    startMillis = millis();
}

void loop() {
    currentMillis = millis();
    if ((currentMillis - startMillis) >= period) {
      startMillis = currentMillis;
      digitalWrite(ADDRESS1, address1[outputState]);
      digitalWrite(ADDRESS2, address2[outputState]);
      digitalWrite(ADDRESS3, address3[outputState]);
      outputState += 1;
      if (outputState == 8) {
        outputState = 0;
      }
    }
}

void multiplexerFunction() {
  
}