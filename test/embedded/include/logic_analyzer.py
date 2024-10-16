import os
from datetime import datetime
from saleae import automation


class LogicAnalyser:
    """Generates a Logic2 instance and collects test data
    """
    LOGIC_ANALYSER_WAIT_TIME = 5

    def _connect_logic(self) -> bool:
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
                capture_mode=automation.TimedCaptureMode(
                    duration_seconds=LogicAnalyser.LOGIC_ANALYSER_WAIT_TIME
                )
                # ManualCaptureMode()
            )

            # Start a capture - the capture will be automatically closed when leaving the `with` block
            try:
                self._start_logic_capture(manager, device_configuration,
                                          capture_configuration)
            except automation.errors.MissingDeviceError:
                automation.logger.error("Logic is open, but device is missing")
                return False
            return True

    def _start_logic_capture(self, manager, device_configuration, capture_configuration) -> None:
        with manager.start_capture(
                device_id="A448875BC25A7C58",
                device_configuration=device_configuration,
                capture_configuration=capture_configuration) as capture:
            # Wait until the capture has finished
            # This will take about 5 seconds because we are using a timed capture mode
            automation.logger.info(
                f"Starting recording for {LogicAnalyser.LOGIC_ANALYSER_WAIT_TIME} seconds")
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
                os.getcwd(), "test", "logs", f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
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
            capture_filepath = os.path.join(output_dir, 'test_capture.sal')
            capture.save_capture(filepath=capture_filepath)

    def start_serial_analysis(self) -> bool:
        """_summary_
        Run the logic2 API (this is mostly copied from their documentation)
        - Save the UART data to a csv
        """
        try:
            return self._connect_logic()
        except Exception as e:
            # This is a _channel._InactiveRpcError error from the grpc library
            # But I can't get it to work in the venv so this will do for now

            # Logic is not open.
            automation.logger.error("Logic is not open. Timeout reached")
            automation.logger.error(e)
            return False
