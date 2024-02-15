/* This file contains the Arduino sketch that runs the pressure mat. 
*/

#define DS0 2 //Demux select 0 pin
#define DS1 3
#define DS2 4
#define DS3 5
#define MS0 6 //Mux select pin 0
#define MS1 7
#define MS2 8
#define MS3 9
#define VOLTAGE_READ A0
#define COL 3 // The dimension (e.g. 3x3 or 8x8 of the prototype)
#define ROW COL
#define MAX_DIMENSION 8 // The maximum dimension, or number of output pins on the DEMUX

bool s0_states[16] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool s1_states[16] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool s2_states[16] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};
bool s3_states[16] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

//Function prototypes
void muxSetup();
void demuxSetup();
void muxSelect(int i);
void demuxSelect(int i);
String intArrayToString(int intArray[], size_t numElements);
int* collectData();

//Setup
void setup() {
    Serial.begin(9600);

    muxSetup();
    demuxSetup();
}

//Main loop
void loop() {

  int* data = collectData();

  Serial.println(intArrayToString(data, ROW*COL));

  delay(1000);
  /*
  while (!(UCSR0A & _BV(UDRE0)) || !(UCSR0A & _BV(TXC0))) {
    delay(1000);
  }
  */
}

/** User-defined Functions **/
void demuxSetup() {
  pinMode(DS0, OUTPUT);
  pinMode(DS1, OUTPUT);
  pinMode(DS2, OUTPUT);
  pinMode(DS3, OUTPUT);
  digitalWrite(DS0, LOW);
  digitalWrite(DS1, LOW);
  digitalWrite(DS2, LOW);
  digitalWrite(DS3, LOW);
}

void muxSetup() {
  pinMode(MS0, OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(MS3, OUTPUT);
  pinMode(VOLTAGE_READ, INPUT);
  digitalWrite(MS0, LOW);
  digitalWrite(MS1, LOW);
  digitalWrite(MS2, LOW);
  digitalWrite(MS3, LOW);
}

void muxSelect(int i) {
  digitalWrite(MS0, s0_states[i]);
  digitalWrite(MS1, s1_states[i]);
  digitalWrite(MS2, s2_states[i]);
  digitalWrite(MS3, s3_states[i]);
}

void demuxSelect(int i) {
  digitalWrite(DS0, s0_states[i]);
  digitalWrite(DS1, s1_states[i]);
  digitalWrite(DS2, s2_states[i]);
  digitalWrite(DS3, s3_states[i]);
}

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
            demuxSelect(i);
            // Set MUX
            muxSelect(j);
            // Read voltage at chosen point
            delay(5);
            data[COL*i+j] = analogRead(VOLTAGE_READ);
        }
    }
    return data;
}
