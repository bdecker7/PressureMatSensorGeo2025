#define RED_LIGHT 2
#define GREEN_LIGHT 3
#define BLUE_LIGHT 4
#define INPUT_PIN A0
#define LEVEL1 200
#define LEVEL2 400
#define LEVEL3 600

void setup() {
  // Set the serial monitor baudrate to 9600
  Serial.begin(9600);
    
  // Output LED Level 3
  pinMode(RED_LIGHT, OUTPUT);
  // Output LED Level 2
  pinMode(GREEN_LIGHT, OUTPUT);
  // Output LED Level 1
  pinMode(BLUE_LIGHT, OUTPUT);
  // Input Pin for sensor
  pinMode(INPUT_PIN, INPUT);
}
  
void loop() {
  //delay(2000);
  // Variable to store ADC value ( 0 to 1023 )
  delay(200);
  int level;
  // analogRead function returns the integer 10 bit integer (0 to 1023)
  level = analogRead(0);

  // Print output voltage in serial monitor
  Serial.println(level);
    
  // Turn off all the led initially
  digitalWrite(RED_LIGHT,LOW);
  digitalWrite(GREEN_LIGHT,LOW);
  digitalWrite(BLUE_LIGHT,LOW);
  
    
    // Splitting 1023 into 3 level => 300, 650, 1023
    // Based on the ADC output, LED indicates the level (1 to 3)
    
  if (level<=LEVEL1)
  {
    // LEVEL 1 LED
    digitalWrite(BLUE_LIGHT,LOW);
    digitalWrite(GREEN_LIGHT,LOW);
    digitalWrite(RED_LIGHT,LOW);
  }
  else if(level<=LEVEL2 && level>LEVEL1)
  {
    // LEVEL 2 LED
    digitalWrite(BLUE_LIGHT,HIGH);
    digitalWrite(GREEN_LIGHT,LOW);
    digitalWrite(RED_LIGHT,LOW);
  }
  else if(level>LEVEL2 && level<= LEVEL3)
  {
    // LEVEL 3 LED
    digitalWrite(BLUE_LIGHT,LOW);
    digitalWrite(GREEN_LIGHT, HIGH);
    digitalWrite(RED_LIGHT,LOW);
  }

  else if (level > LEVEL3)
  {
    // LEVEL 3 LED
    digitalWrite(BLUE_LIGHT,LOW);
    digitalWrite(GREEN_LIGHT,LOW);
    digitalWrite(RED_LIGHT,HIGH);
  }
    
}