#define MUX_S0 6
#define MUX_S1 5
#define MUX_S2 4
#define voltageRead 8
#define voltageOut 10

int output[] = {0, 102, 255};
int i = 0;

void setup() {
    Serial.begin(9600);
    pinMode(MUX_S0, OUTPUT);
    pinMode(MUX_S1, OUTPUT);
    pinMode(MUX_S2, OUTPUT);
    pinMode(voltageOut, OUTPUT);
    pinMode(voltageRead, INPUT);
    digitalWrite(MUX_S0, LOW);
    digitalWrite(MUX_S1, LOW);
    digitalWrite(MUX_S2, LOW);
    digitalWrite(voltageOut, LOW);
}

void loop() {
  digitalWrite(MUX_S0, HIGH);
  digitalWrite(MUX_S1, HIGH);
  digitalWrite(MUX_S2, LOW);

  if (digitalRead(voltageRead) == HIGH) {
    analogWrite(voltageOut, output[i % 3]);
    i++;
  }

  delay(1000);

}
