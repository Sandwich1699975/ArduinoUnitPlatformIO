#line 2 "main.cpp"
#include <ArduinoUnit.h>

test(exampleTest1)
{
  Serial.println("Dummy test 1");
  assertEqual(3, 3);
}

void square(Stream &io)
{
  io.print("value? ");
  int x = io.parseInt();
  io.print(x);
  io.print("*");
  io.print(x);
  io.print("=");
  io.println(x * x);
}

test(exampleTest2)
{
  MockStream ms;
  ms.input.print(10);
  square(ms);
  Serial.print("MOCK_OUTPUT: ");
  Serial.println(ms.output);
  assertEqual(ms.output, "value? 10*10=100\r\n");
}

test(exampleTest3)
{
  Serial.print("Serial output prefixed with no newline");
  // Serial.println("Serial output on own line");
  assertEqual(5, 5);
}

//----------------------------------------------------------------------------
// setup() and loop()
//----------------------------------------------------------------------------

void setup()
{
  Serial.begin(115200);
  while (!Serial)
  {
  } // Portability for Leonardo/Micro
  delay(2000); // Delay to wait for logic to startup
}

void loop()
{
  Test::run();
}