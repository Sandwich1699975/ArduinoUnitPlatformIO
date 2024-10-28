# ArduinoUnit PlatformIO Integration

**My template** for using [`arduinounit`](https://github.com/mmurdoch/arduinounit) in [PlatformIO](https://platformio.org/) with a [logic analyser](https://core-electronics.com.au/usb-logic-analyzer-24mhz-8-channel.html) and with a custom ESP-32S2 based board.

> [!NOTE]  
> This repo was originally for [`AUnit`](https://github.com/bxparks/AUnit) but I needed the `MockStream` object so I converted to ArdunioUnit.
> **If you want to use `AUnit`, you see see their tutorial on migrating from ArduinoUnit [here](https://github.com/bxparks/AUnit?tab=readme-ov-file#ArduinoUnitCompatible)**

<p align="center">
    <img src="assets/setup.png" alt="Annotated hardware setup" width="300">
</p>

For those looking to implement their own version of ArduinoUnit with PlatformIO, I wish you the best of luck. This was incredibly complex to get working. My method also uses a [physical logic analyser](https://core-electronics.com.au/usb-logic-analyzer-24mhz-8-channel.html) and [Saleae's Logic2 application](https://www.saleae.com/pages/downloads?srsltid=AfmBOop1eoIiGSyJggODsT0lgRuMeX46d3sEPPDvJscgZumQkeUSdmga) to make this work well with: physical testing, software compatibility and development. If you don't have a logic analyser, you will need some sort of way to read the serial data from the board and pipe it into the the [custom test runner](https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/custom/runner.html) which is located in `test/**/test_custom_runner.py`.

## Summary

To run a test, use the provided [PIO test hierarchy](https://docs.platformio.org/en/stable/advanced/unit-testing/structure/hierarchy.html#test-hierarchy) and try to minimise the amount of separate test files. Each test file `*.cpp` will be compiled and flashed inividually which takes a while. So make sure you can fit in as much as you can in the one flash to avoid 10 minute test runs. 

In each test, you are using **just** [ArduinoUnit](https://github.com/mmurdoch/arduinounit). This is the methodology and [hierarchy](https://docs.platformio.org/en/latest/advanced/unit-testing/structure/hierarchy.html) for creating tests:

0. Install python test dependencies
    - `source ~/.platformio/penv/bin/activate` then  `pip install logic2-automation`
1. Create a test in a folder prefixed with `test_`
    - This requires a `.cpp` file with the ArduinoUnit software that runs all tests in that file with the `Test::run` command.
2. Run the PIO test

### Python Runner

This implementation uses a [python handler/runner](https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/custom/runner.html) which must be called `test_custom_runner.py`. 

This file is a generic bridge to parse the results of each test. PIO will search each directory and parent directory until it has reached the root of `test_dir`. This means each test can have custom handlers with precedence. At the moment, only a generic one is needed in the `embedded/` folder to handle all those test cases.

This Python file will then connect to your logic analyser software ([Logic2](https://saleae.github.io/logic2-automation/index.html)) and create raw and high-level ASCII CSV analysis files. After those files are created by the logic analyser, the PIO `test_custom_runner.py` file will then scrape that output for the ArduinoUnit success and failure messages. That data is then formatted with the PIO test cases class and presented in the rich report. 

## Known Limitations 

- This method with the Logic2 API does not run concurrently. The Unity test system and the Logic API are totally disjointed. The recording starts then begins a race condition with the Unity scraper (which sucks). This seems to require a rebuild of the API or some sort of custom local hosted server to fix this (the logic recording is not written to a file until it's finished). It's currently not a big issue and does not warrant a change this big. A simple delay on the Python or hardware side can account for timing issues if needed.
    - Due to the race condition, ESP boot messages over serial are not accounted for because they are consistently skipped by timeout anyway
- Some `TestCase` attributes are not printing. I can't see `message` or `TestCaseSource` for some reason

## Troubleshooting

**Getting import errors**

- Make sure you have installed the python dependencies as listed in the summary section above. 
- Make sure your python interpreter is selected as `~/.platformio/penv/bin/python`.

**No test cases or no summary file**

- Make sure baud rate is correct

## Todo List

- Stop the recording once the tests have finished [link](https://saleae.github.io/logic2-automation/automation.html#saleae.automation.CaptureConfiguration) and [method to use](https://saleae.github.io/logic2-automation/automation.html#manualcapturemode). This will have to be done by stopping it manually while parsing when the summary line is detected
    - This may be impossible with current API
- Test if this works on another computer
- Note: Continuous capturing is only available with a [HLA](https://github.com/saleae/logic2-automation/issues/4) it seems. This would also require another system to export back and fourth from logic and unity. Probably not worth it. 
- Test with more complex ArduinoUnit test outputs

Example **ArduinoUnit** output for reference:

```
Dummy test 1
Test exampleTest1 passed.
MOCK_OUTPUT: value? 10*10=100
Test exampleTest2 passed.
Serial output prefixed with no newlineTest exampleTest3 passed.
Test summary: 3 passed, 0 failed, and 0 skipped, out of 3 test(s).
```
