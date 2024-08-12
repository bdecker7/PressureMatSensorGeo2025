// Uncomment the line below before uploading sketch to enable debugging mode
// Data will be sent to the serial monitor instead of the python script

// #define DEBUG

/*
 * Definitions:
*/

// Pin definitions (must match the hardware connections)

#define DS0 2 //Demux select 0 pin
#define DS1 3 //Demux select 1 pin
#define DS2 4 //Demux select 2 pin

#define D1E 5 //Demux 1: enable pin
#define D2E 6 //Demux 2: enable pin

#define MS0 7 //Mux select 0 pin
#define MS1 8 //Mux select 1 pin
#define MS2 9 //Mux select 2 pin
#define MS3 10 //Mux select 3 pin

#define VOLTAGE_READ A0 //Voltage analog reading pin

// Data definitions

#define COL 16 //Number of columns in the sensor matrix
#define ROW 16 //Number of rows in the sensor matrix

#define GET_DATA 0b1 //Byte defining the get data command received from the computer


/*
 * Global variables:
*/

//Mux and Demux route selectors
bool s0_states[16] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool s1_states[16] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool s2_states[16] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};
bool s3_states[16] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

bool D1On = false; //Demux 1 enable state


/*
 * Function declarations
*/
void muxSetup();
void demuxSetup();

void sendTwoByteInt(uint16_t value);
void sendData();

void muxSelect(int i);
void demuxSelect(int i);
void calculateBias();
int removeBias(int row, int col);

void collectAndSendData(bool debug = false);


/*
 * Main Setup and Loop
*/

void setup() {
    Serial.begin(115200);
    
    demuxSetup();
    muxSetup();

    #ifndef DEBUG
      Serial.write(0b1); // Send "ready" message to computer (a "1" byte)
    #endif
}

void loop() {

    #ifndef DEBUG
      //Wait until data is requested by the computer
      while(Serial.read() != GET_DATA);
      
      // Send the size of the data array
      sendTwoByteInt(ROW);
      sendTwoByteInt(COL);
      collectAndSendData();
    #endif


    #ifdef DEBUG
      collectAndSendData(true);
      delay(500); // Wait for a bit before sending the next data
    #endif
}


/*
 * Function definitions
*/

void demuxSetup() {
  pinMode(DS0, OUTPUT);
  pinMode(DS1, OUTPUT);
  pinMode(DS2, OUTPUT);
  pinMode(D1E, OUTPUT);
  pinMode(D2E, OUTPUT);
  digitalWrite(DS0, LOW);
  digitalWrite(DS1, LOW);
  digitalWrite(DS2, LOW);
  digitalWrite(D1E, HIGH);
  digitalWrite(D2E, LOW);
  D1On = true;
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
  if (i >= 8) {
    if (D1On == true) {
      digitalWrite(D1E, LOW);
      digitalWrite(D2E, HIGH);
      D1On = false;
    }
  }
  else {
    if (D1On == false) {
      digitalWrite(D1E, HIGH);
      digitalWrite(D2E, LOW);
      D1On = true;
    }
  }
  i = i % 8;
  digitalWrite(DS0, s0_states[i]);
  digitalWrite(DS1, s1_states[i]);
  digitalWrite(DS2, s2_states[i]);
}

void sendTwoByteInt(uint16_t value) {
  Serial.write((byte*)&value, sizeof(uint16_t));
}

void collectAndSendData(bool debug = false) {
  for(int row = 0; row < ROW; row++) {
    
    demuxSelect(row); // Select the row on the demultiplexer
    delayMicroseconds(100);
    
    for(int col = 0; col < COL; col++) {

      muxSelect(col); // Select the column on the multiplexer
      delayMicroseconds(100);

      int value = analogRead(VOLTAGE_READ); // Read the voltage at the selected row and column

      if (debug) {
        Serial.print(value);
        Serial.print("  ");
      } else {
        sendTwoByteInt(static_cast<uint16_t>(value)); // Send the value to the computer
      }
    }
    if (debug) Serial.println();
  }
  if (debug) Serial.println();
}