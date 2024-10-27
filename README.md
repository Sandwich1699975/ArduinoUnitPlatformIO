# AUnit PlatformIO Integration

**My template** for using [AUnit](https://github.com/bxparks/AUnit) in [PlatformIO](https://platformio.org/) with a [logic analyser](https://core-electronics.com.au/usb-logic-analyzer-24mhz-8-channel.html) and with a custom ESP-32S2 based board.

<p align="center">
    <img src="assets/setup.png" alt="Annotated hardware setup" width="300">
</p>

For those looking to implement their own version of AUnit with PlatformIO, I wish you the best of luck. This was incredibly complex to get working. My method also uses a [physical logic analyser](https://core-electronics.com.au/usb-logic-analyzer-24mhz-8-channel.html) and [Saleae's Logic2 application](https://www.saleae.com/pages/downloads?srsltid=AfmBOop1eoIiGSyJggODsT0lgRuMeX46d3sEPPDvJscgZumQkeUSdmga) to make this work well with: physical testing, software compatability and development. If you don't have a logic analyser, you will need some sort of way to read the serial data from the board and pipe it into the the [custom test runner](https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/custom/runner.html) which is located in `test/**/test_custom_runner.py`.

## Summary

To run a test, use the provided [PIO test hierarchy](https://docs.platformio.org/en/stable/advanced/unit-testing/structure/hierarchy.html#test-hierarchy) and try to minimise the amount of seperate test files. Each test file `*.cpp` will be compiled and flashed inividually which takes a while. So make sure you can fit in as much as you can in the one flash to avoid 10 minute test runs. 

In each test, you are using **just** [AUnit](https://github.com/bxparks/AUnit). This is the methodology and [heirarchy](https://docs.platformio.org/en/latest/advanced/unit-testing/structure/hierarchy.html) for creating tests:

0. Install python test dependencies
    - `source ~/.platformio/penv/bin/activate` then  `pip install logic2-automation`
1. Create a test in a folder prefixed with `test_`
    - This requires a `.cpp` file with the AUnit software that runs all tests in that file with the `aunit::TestRunner::run();` command.
2. Run the PIO test

### Python Runner

This implementation uses a [python handler/runner](https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/custom/runner.html) which must be called `test_custom_runner.py`. 

This file is a generic bridge to parse the results of each test. PIO will search each directory and parent directory until it has reached the root of `test_dir`. This means each test can have custom handlers with precedence. At the moment, only a generic one is needed in the `embedded/` folder to handle all those test cases.

This Python file will then connect to your logic analyser software ([Logic2](https://saleae.github.io/logic2-automation/index.html)) and create raw and high-level ASCII CSV analysis files. After those files are created by the logic analyser, the PIO `test_custom_runner.py` file will then scrape that output for the AUnit success and failure messages. That data is then formatted with the PIO test cases class and presented in the rich report. 

## Known Limitations 

- This method with the Logic2 API does not run concurrently. The Unity test system and the Logic API are totally disjointed. The recording starts then begins a race condition with the Unity scraper (which sucks). This seems to require a rebuild of the API or some sort of custom local hosted server to fix this. It's currently not a big issue and does not warrant a change this big. A simple delay on the Python or hardware side can account for timing issues if needed.
    - Due to the race condition, ESP boot messages over serial are not accounted for because they are consisitenly skipped by timeout anyway
- Some `TestCase` attributes are not printing. I can't see `message` or `TestCaseSource` for some reason

## Troubleshooting

**Getting import errors**

- Make sure you have installed the python dependancies as listed in the summary section above. 
- Make sure your python interpreter is selected as `~/.platformio/penv/bin/python`.

## Todo List

- Stop the recording once the tests have finished [link](https://saleae.github.io/logic2-automation/automation.html#saleae.automation.CaptureConfiguration) and [method to use](https://saleae.github.io/logic2-automation/automation.html#manualcapturemode). This will have to be done by stopping it manually while parsing when the summary line is detected
    - This may be impossible with current API
- Test if this works on another computer
- Note: Continuous capturing is only available with a [HLA](https://github.com/saleae/logic2-automation/issues/4) it seems. This would also require another system to export back and fourth from logic and unity. Probably not worth it. 
- Test with more complex AUnit test outputs

Example **ArduinoUnit** output for refference:

```
ESP-ROM:esp32s2-rc4-20191025
Build:Oct 25 2019
rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:DIO, clock div:1
load:0x3ffe6100,len:0x55c
load:0x4004c000,len:0xa70
load:0x40050000,len:0x29d8
entry 0x4004c18c
TestRunner started on 2 test(s).
Test exampleTest passed.
AUnitPlatformIO.ino:12: Assertion failed: (3) == (2).
Test exampleTest2 failed.
TestRunner duration: 0.011 seconds.
TestRunner summary: 1 passed, 1 failed, 0 skipped, 0 timed out, out of 2 test(s).
```
