/* This file contains the Arduino sketch that runs the pressure mat. 
*/

#define MUX_S0 22
#define MUX_S1 24
#define MUX_S2 26
#define DEMUX_A0 49
#define DEMUX_A1 51
#define DEMUX_A2 53
#define VOLTAGE_READ A0
#define COL 3 // The dimension (e.g. 3x3 or 8x8 of the prototype)
#define ROW COL
#define MAX_DIMENSION 8 // The maximum dimension, or number of output pins on the DEMUX

bool address0[8] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool address1[8] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool address2[8] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};

String intArrayToString(int intArray[], size_t numElements) {
  /* Create a string representation of an int array. For serial transmission.
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

int* collectData() {
    /* Loops through all possible MUX/DEMUX combinations, gathers data at each one
     * Returns pointer to int array containing values read
    */
    int data[ROW * COL];
    
    // i = DEMUX, j = MUX
    for (size_t i = 0; i < ROW; i++) {
        for (size_t j = 0; j < COL; j++) {
            // Set DEMUX
            digitalWrite(DEMUX_A0, address0[i]);
            digitalWrite(DEMUX_A1, address1[i]);
            digitalWrite(DEMUX_A2, address2[i]);
            // Set MUX
            digitalWrite(MUX_S0, address0[j]);
            digitalWrite(MUX_S1, address1[j]);
            digitalWrite(MUX_S2, address2[j]);
            // Read voltage at chosen point
            delay(5);
            data[8*i+j] = analogRead(VOLTAGE_READ);
        }
    }
    return data;
}

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

    int* data = collectData();

    Serial.print(intArrayToString(data, ROW*COL));
    while (SERIAL_TX_BUFFER_SIZE - Serial.availableForWrite() - 1 != 0) {
      // Wait for data to be read from output buffer before repeating
      delay(1);
    }
    // Serial.flush(); // Wait for data to be read from buffer before repeating
    
    // ^^ neither of the above "wait" methods seemed to work

    // Serial.print(data[0]);
    // Serial.println("test");
    // delay(1000);
}
