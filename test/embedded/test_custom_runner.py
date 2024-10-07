from saleae import automation # This will need to be installed in the pio venv
# from grpc import _channel
from platformio.public import TestCase, TestCaseSource, TestStatus, UnityTestRunner
import os
import os.path
from datetime import datetime
# This is gonna be one of thoses projects where you almost need unit tests for the unit tester

# This will run over all embedded/ test cases.
# TODO Make this loop over the logic output to parse AUnit test results


def _connect_logic() -> bool:
    # Connect to the running Logic 2 Application on port `10430`.
    # Alternatively you can use automation.Manager.launch() to launch a new Logic 2 process - see
    # the API documentation for more details.
    # Using the `with` statement will automatically call manager.close() when exiting the scope. If you
    # want to use `automation.Manager` outside of a `with` block, you will need to call `manager.close()` manually.
    with automation.Manager.connect(port=10430) as manager:
        # Configuration based on options in the Logic2 UI
        device_configuration = automation.LogicDeviceConfiguration(
            enabled_digital_channels=[0, 1, 2, 3, 4, 5, 6, 7],
            digital_sample_rate=2_000_000,
        )

        # Record 5 seconds of data before stopping the capture
        capture_configuration = automation.CaptureConfiguration(
            capture_mode=automation.TimedCaptureMode(duration_seconds=5)
        )

        # Start a capture - the capture will be automatically closed when leaving the `with` block
        try:
            _start_logic_capture(manager, device_configuration,
                                 capture_configuration)
        except automation.errors.MissingDeviceError:
            automation.logger.error("Logic is open, but device is missing")
            return False
        return True


def _start_logic_capture(manager, device_configuration, capture_configuration) -> None:
    with manager.start_capture(
            device_id="A448875BC25A7C58",
            device_configuration=device_configuration,
            capture_configuration=capture_configuration) as capture:
        # Wait until the capture has finished
        # This will take about 5 seconds because we are using a timed capture mode
        capture.wait()

        # Add an analyzer to the capture. This is verbatem from the UI
        uart_analyzer = capture.add_analyzer('Async Serial', label=f'Test Analyzer', settings={
            'Input Channel': 0,
            'Bit Rate (Bits/s)': 115200,
            'Bits per Frame': '8 Bits per Transfer (Standard)',
            'Stop Bits': '1 Stop Bit (Standard)',
            'Parity Bit': 'No Parity Bit (Standard)',
            'Significant Bit': 'Least Significant Bit Sent First (Standard)',
            'Signal inversion': 'Non Inverted (Standard)',
            'Mode': 'Normal'
        })

        # Store output in a timestamped directory
        output_dir = os.path.join(
            os.getcwd(), "serial_data", f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
        os.makedirs(output_dir)

        # Export analyzer data to a CSV file
        analyzer_export_filepath = os.path.join(
            output_dir, 'uart_export.csv')
        capture.export_data_table(
            filepath=analyzer_export_filepath,
            analyzers=[uart_analyzer]
        )

        # Export raw digital data to a CSV file
        capture.export_raw_data_csv(
            directory=output_dir, digital_channels=[0, 1, 2, 3, 4, 5, 6, 7])

        # Finally, save the capture to a file
        capture_filepath = os.path.join(output_dir, 'example_capture.sal')
        capture.save_capture(filepath=capture_filepath)

def run_serial_analysis() -> bool:
    """_summary_
    Run the logic2 API (this is mostly copied from their documentation)
    - Save the UART data to a csv
    """
    try:
        return _connect_logic()
    except Exception:
        # This is a _channel._InactiveRpcError error from the grpc library
        # But I can't get it to work in the venv so this will do for now
        
        # Logic is not open. 
        automation.logger.error("Logic is not open. Timeout reached")
        return False



class CustomTestRunner(UnityTestRunner):
    def setup(self):
        # Setup serial analysis 
        self.LOGIC_BOOT_OK = run_serial_analysis()
        if not self.LOGIC_BOOT_OK:
            raise RuntimeError("Error starting Logic2")    
        return super().setup()
    
    def stage_testing(self):
        # 1. Gather test results from Serial, HTTP, Socket, or other sources
        # 2. Report test results (add cases)

        # Exmaple: Report succeed result with duration (optional)
        self.test_suite.add_case(
            TestCase(name="test_connectivity",
                     status=TestStatus.PASSED, duration=1.34)
        )

        # # Example: Report failed result with source file
        # self.test_suite.add_case(
        #     TestCase(
        #         name="test_calculator_division",
        #         status=TestStatus.FAILED,
        #         message="Expected 32 Was 33",
        #         stdout="test/test_desktop/test_calculator.cpp:43:test_calculator_division:FAIL: Expected 32 Was 33",
        #         duration=0.44,
        #         # source=TestCaseSource(
        #         #     file="test/test_desktop/test_calculator.cpp", line=43
        #         # ),
        #     )
        # )
