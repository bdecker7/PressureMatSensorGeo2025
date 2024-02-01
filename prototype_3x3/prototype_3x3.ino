/* This file contains the Arduino sketch that runs the pressure mat. 
*/

#define MUX_S0 22
#define MUX_S1 24
#define MUX_S2 26
#define DEMUX_A0 49
#define DEMUX_A1 51
#define DEMUX_A2 53
#define VOLTAGE_READ A0

bool address0[3] = {LOW, HIGH, LOW};
bool address1[3] = {LOW, LOW, HIGH};
bool address2[3] = {LOW, LOW, LOW};

void setup() {
    Serial.begin(9600);

    pinMode(MUX_S0, OUTPUT);
    pinMode(MUX_S1, OUTPUT);
    pinMode(MUX_S2, OUTPUT);
    pinMode(DEMUX_A0, OUTPUT);
    pinMode(DEMUX_A1, OUTPUT);
    pinMode(DEMUX_A2, OUTPUT);
    pinMode(VOLTAGE_READ, INPUT);

    digitalWrite(MUX_S0, LOW);
    digitalWrite(MUX_S1, LOW);
    digitalWrite(MUX_S2, LOW);
    digitalWrite(DEMUX_A0, LOW);
    digitalWrite(DEMUX_A1, LOW);
    digitalWrite(DEMUX_A2, LOW);
}

void loop() {

    long i = 0;

    digitalWrite(DEMUX_A0, address0[i]);
    digitalWrite(DEMUX_A1, address1[i]);
    digitalWrite(DEMUX_A2, address2[i]);
    digitalWrite(MUX_S0, address0[i]);
    digitalWrite(MUX_S1, address1[i]);
    digitalWrite(MUX_S2, address2[i]);
    Serial.println(analogRead(VOLTAGE_READ));

    delay(500);

}
