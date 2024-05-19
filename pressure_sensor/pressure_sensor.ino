
/*
 * Definitions:
*/
#define DS0 2 //Demux select 0 pin
#define DS1 3 //Demux select 1 pin
#define DS2 4 //Demux select 2 pin
#define DS3 5 //Demux select 3 pin

#define D1E 10 //Demux 1: enable pin
#define D2E 11 //Demux 2: enable pin

#define MS0 6 //Mux select 0 pin
#define MS1 7 //Mux select 1 pin
#define MS2 8 //Mux select 2 pin
#define MS3 9 //Mux select 3 pin

#define VOLTAGE_READ A0 //Voltage analog reading pin

#define COL 16 //Number of columns in the sensor matrix
#define ROW 16 //Number of rows in the sensor matrix

#define GET_DATA 0b1 //Byte defining the get data command

//#define DEBUG


/*
 * Global variables:
*/

//Mux and Demux route selectors
bool s0_states[16] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool s1_states[16] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool s2_states[16] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};
bool s3_states[16] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

float bias[ROW][COL]; //Bias values for each sensor in the matrix
bool D1On = false; //Demux 1 enable state
static uint16_t DATA[ROW][COL]; //Data array to store the sensor readings


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

void collectData();
void userOptions();


/*
 * Main Setup and Loop
*/

void setup() {
    Serial.begin(115200);
    demuxSetup();
    muxSetup();
    //mosfetSetup();
    calculateBias();

    Serial.write(0b1); // Send "ready" message to computer (a "1" byte)
}

void loop() {

  #ifdef DEBUG
    while (Serial.available() > 0) {
      userOptions();
    }
    int i = 0;
    int j = 1;
    demuxSelect(i);
    muxSelect(j);

    Serial.println(analogRead(VOLTAGE_READ) - bias[i][j]);
  #endif

  #ifndef DEBUG
    while(Serial.read() != GET_DATA); //Wait until data is requested (by receiving a '1' byte)

    // Send the size of the data, then the data itself
    sendTwoByteInt(ROW);
    sendTwoByteInt(COL);
    collectData();
    sendData();
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
      // delay(50);
    }
  }
  else {
    if (D1On == false) {
      digitalWrite(D1E, HIGH);
      digitalWrite(D2E, LOW);
      D1On = true;
      // delay(50);
    }
  }
  // delay(3);
  i = i % 8;
  digitalWrite(DS0, s0_states[i]);
  digitalWrite(DS1, s1_states[i]);
  digitalWrite(DS2, s2_states[i]);
}

void sendTwoByteInt(uint16_t value) {
  Serial.write((byte*)&value, sizeof(uint16_t));
}

void sendData() {
  Serial.write((byte*)DATA, ROW * COL * sizeof(uint16_t));
}

void collectData() {
  for(int row = 0; row < ROW; row++) {
    demuxSelect(row); // Select the row on the demultiplexer
    delayMicroseconds(10);
    for(int col = 0; col < COL; col++) {
      muxSelect(col); // Select the column on the multiplexer
      delayMicroseconds(10);

      int value = removeBias(row, col); // Read the voltage at the selected row and column
      value = value < 0 ? 0 : value; // If the value is negative, set it to 0
      DATA[row][col] = value; // Store the value in the data array

      delayMicroseconds(10);
    }
  }
}

void calculateBias() {
  for(int row = 0; row < ROW; row++) {
    demuxSelect(row);
    for(int col = 0; col < COL; col++) {
      muxSelect(col);
      delay(5);

      bias[row][col] = analogRead(VOLTAGE_READ);
      delay(1);
    }
  }
}

int removeBias(int row, int col) {
  return analogRead(VOLTAGE_READ) - bias[row][col];
}

void userOptions() {
  String inBytes = Serial.readStringUntil('\n');

  if (inBytes == "reset") {
    Serial.println("Recalculated bias");
    calculateBias();
  }
  else if (inBytes == "pause") {
    Serial.println("Paused");
    bool resumed = false;
    while(!resumed) {
      if (Serial.readStringUntil('\n') == "resume") {
        Serial.println("Resuming ...");
        delay(2000);
        resumed = true;
      }
    }
  }
}