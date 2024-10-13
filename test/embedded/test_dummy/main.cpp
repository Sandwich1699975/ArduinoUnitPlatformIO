#line 2 "AUnitPlatformIO.ino"

#include <AUnit.h>

test(exampleTest1)
{
  assertEqual(3, 3);
}

test(exampleTest2)
{
  assertNotEqual(3, 3);
}

test(exampleTest3)
{
  assertLess(5, 5);
}

//----------------------------------------------------------------------------
// setup() and loop()
//----------------------------------------------------------------------------

void setup()
{
#if !defined(EPOXY_DUINO)
  delay(1000); // wait for stability on some boards to prevent garbage Serial
#endif
  Serial.begin(115200); // ESP8266 default of 74880 not supported on Linux
  while (!Serial)
    ; // for the Arduino Leonardo/Micro only
#if defined(EPOXY_DUINO)
  Serial.setLineModeUnix();
#endif
  pinMode(1, OUTPUT);
  digitalWrite(1, HIGH);
}

void loop()
{
  aunit::TestRunner::run();
}