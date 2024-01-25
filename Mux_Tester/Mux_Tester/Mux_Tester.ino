#define MUX_S0 4
#define MUX_S1 5
#define MUX_S2 6
#define voltageRead 10


void setup() {
    Serial.begin(9600);
    pinMode(MUX_S0, OUTPUT);
    pinMode(MUX_S1, OUTPUT);
    pinMode(MUX_S2, OUTPUT);
    pinMode(voltageRead, INPUT);
    digitalWrite(MUX_S0, HIGH);
    digitalWrite(MUX_S1, LOW);
    digitalWrite(MUX_S2, LOW);
}

void loop() {
  digitalWrite(MUX_S0, LOW);
  digitalWrite(MUX_S1, LOW);
  digitalWrite(MUX_S2, LOW);

  Serial.println(digitalRead(voltageRead));

}
