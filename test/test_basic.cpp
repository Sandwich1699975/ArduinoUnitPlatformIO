#line 2 "AUnitPlatformIO.ino"

#include <AUnit.h>
#include <unity.h>

test(exampleTest)
{
  assertEqual(3, 3);
}

//----------------------------------------------------------------------------
// setup() and loop()
//----------------------------------------------------------------------------

// void setup()
// {
// #if !defined(EPOXY_DUINO)
//   delay(1000); // wait for stability on some boards to prevent garbage Serial
// #endif
//   Serial.begin(115200); // ESP8266 default of 74880 not supported on Linux
//   while (!Serial)
//     ; // for the Arduino Leonardo/Micro only
// #if defined(EPOXY_DUINO)
//   Serial.setLineModeUnix();
// #endif
// }

void runAUnit()
{
  aunit::TestRunner::run();
}

int runUnityTests(void)
{
  UNITY_BEGIN();
  RUN_TEST(runAUnit);
  return UNITY_END();
}

/**
 * For Arduino framework
 */
void setup()
{
  // Wait ~2 seconds before the Unity test runner
  // establishes connection with a board Serial interface
  delay(2000);

  runUnityTests();
}
void loop() {}

// /**
//  * For ESP-IDF framework
//  */
// void app_main()
// {
//   runUnityTests();
// }