//IR sensor pins

const int IR_2 = 9; 

//------------------------------------------------

void setup() // setup code to run once
{
  Serial.begin(9600); // sets up Serial library at 9600 bps
}

//------------------------------------------------


//Calibration loop, delete later
void loop()
{
  Serial.println("Calibrating IR Sensors...");
  delay(1000);  // Allow time to position the robot


  Serial.print("IR_2 Value: ");
  Serial.println(digitalRead(IR_2));
  delay(100);
}
