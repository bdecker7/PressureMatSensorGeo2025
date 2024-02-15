#define DS0 2 //Demux select 0 pin
#define DS1 3
#define DS2 4
#define DS3 5
#define MS0 6
#define MS1 7
#define MS2 8
#define MS3 9
#define VOLTAGE_READ A0
#define COL 3
#define ROW 3

//#define DEBUG

//Mux and Demux route selectors
bool s0_states[16] = {LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH, LOW, HIGH};
bool s1_states[16] = {LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH};
bool s2_states[16] = {LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH};
bool s3_states[16] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

float bias[ROW][COL];

//Function prototypes
void muxSetup();
void demuxSetup();
void muxSelect(int i);
void demuxSelect(int i);
void calculateBias();
int removeBias(int row, int col);
String getPadStates();
void userOptions();


//Setup
void setup() {
    Serial.begin(9600);
    demuxSetup();
    muxSetup();
    calculateBias();
}

//Loop
void loop() {

  while (Serial.available() > 0) {
    userOptions();
  }

  #ifdef DEBUG
    int i = 0;
    int j = 0;
    demuxSelect(i);
    muxSelect(j);

    Serial.println(analogRead(VOLTAGE_READ));
  #endif

  #ifndef DEBUG
    Serial.println(getPadStates());
    Serial.println();
    while(!Serial.available() || Serial.read() == 0b1);
  #endif
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

String getPadStates() {
  String output = "";

  for(int row = 0; row < ROW; row++) {
    demuxSelect(row);
    delay(.1);
    for(int col = 0; col < COL; col++) {
      muxSelect(col);
      delay(5);

      output += String(removeBias(row, col));

      if (col != 2) {
        output += ",";
      }
    }
    output += "\n";
  }

  return output;
}

void calculateBias() {
  for(int row = 0; row < ROW; row++) {
    demuxSelect(row);
    for(int col = 0; col < COL; col++) {
      muxSelect(col);
      delay(5);

      bias[row][col] = analogRead(VOLTAGE_READ);
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