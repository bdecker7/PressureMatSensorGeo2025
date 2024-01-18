#define ADDRESS1 22
#define ADDRESS2 24
#define ADDRESS3 26

int state = 0;
unsigned long startMillis;
unsigned long currentMillis;
unsigned long period = 1000;

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
      switch (state) {
          case 0:
              digitalWrite(ADDRESS1, LOW);
              digitalWrite(ADDRESS2, LOW);
              digitalWrite(ADDRESS3, LOW);
              state += 1;
              break;
          case 1:
              digitalWrite(ADDRESS1, HIGH);
              digitalWrite(ADDRESS2, LOW);
              digitalWrite(ADDRESS3, LOW);
              state += 1;
              break;
          case 2:
              digitalWrite(ADDRESS1, LOW);
              digitalWrite(ADDRESS2, HIGH);
              digitalWrite(ADDRESS3, LOW);
              state += 1;
              break;
          case 3:
              digitalWrite(ADDRESS1, HIGH);
              digitalWrite(ADDRESS2, HIGH);
              digitalWrite(ADDRESS3, LOW);
              state += 1;
              break;
          case 4:
              digitalWrite(ADDRESS1, LOW);
              digitalWrite(ADDRESS2, LOW);
              digitalWrite(ADDRESS3, HIGH);
              state += 1;
              break;
          case 5:
              digitalWrite(ADDRESS1, HIGH);
              digitalWrite(ADDRESS2, LOW);
              digitalWrite(ADDRESS3, HIGH);
              state += 1;
              break;
          case 6:
              digitalWrite(ADDRESS1, LOW);
              digitalWrite(ADDRESS2, HIGH);
              digitalWrite(ADDRESS3, HIGH);
              state += 1;
              break;
          case 7:
              digitalWrite(ADDRESS1, HIGH);
              digitalWrite(ADDRESS2, HIGH);
              digitalWrite(ADDRESS3, HIGH);
              state = 0;
              break;
        }
        Serial.println(state);
    }
}