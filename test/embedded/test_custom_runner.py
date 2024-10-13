from saleae import automation # This will need to be installed in the pio venv
from platformio.public import TestCase, TestCaseSource, TestStatus, UnityTestRunner
import os
import re
import csv
from typing import Optional, List, Dict
import os.path
from datetime import datetime
# This is gonna be one of thoses projects where you almost need unit tests for the unit tester

# This will run over all embedded/ test cases.
# TODO Make this loop over the logic output to parse AUnit test results


class CustomTestRunner(UnityTestRunner):
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
                    duration_seconds=CustomTestRunner.LOGIC_ANALYSER_WAIT_TIME
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
            automation.logger.info(f"Starting recording for {CustomTestRunner.LOGIC_ANALYSER_WAIT_TIME} seconds")
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
                os.getcwd(), "test","logs", f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
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

    def setup(self):
        return super().setup()
    
    def stage_testing(self):
        # 1. Gather test results from Serial, HTTP, Socket, or other sources
        # Setup serial analysis 
        self.LOGIC_BOOT_OK = self.start_serial_analysis()
        if not self.LOGIC_BOOT_OK:
            raise RuntimeError("Error starting Logic2")    
        # 2. Report test results (add cases)

        for case in self.create_all_test_cases():
            self.test_suite.add_case(case)
            
    def teardown(self):
        try:
            TIMESTAMPED_LINES = self.get_timestamped_lines()
            CURRENT_LOG_PATH = self.find_last_modified_test_dir()
        except Exception as e:
            print(e)
            
        with open(os.path.join(CURRENT_LOG_PATH,'summary.txt'),'w') as w:
            for line in TIMESTAMPED_LINES:
                w.write(line["line"] + '\n')
    


    def find_last_modified_test_dir(self) -> Optional[str]:
        """Finds the last modified directory in the 'test/logs' folder.

        Returns:
            Optional[str]: The path of the last modified directory, 
            or None if no directories are found.
        """
        dirs = []
        test_data_directory = os.path.join("test","logs")
        
        # Iterate through all items in the base_directory
        for d in os.listdir(test_data_directory):
            dir_path = os.path.join(test_data_directory, d)
            # Check if the item is a directory and add to the list
            if os.path.isdir(dir_path):
                dirs.append(dir_path)
        
        if not dirs:
            return None 

        # Find the directory with the latest modification time
        last_modified_dir = max(dirs, key=os.path.getmtime)
        
        return last_modified_dir

    def get_timestamped_lines(self) -> Optional[List[Dict[str, float]]]:
        """Get all lines from csv and timestamp the time the last byte was recieved

        Returns:
            list[dict]: A list of dictionaries with line contents and duration
        """
        
        LATEST_LOG_PATH = self.find_last_modified_test_dir()
        if not LATEST_LOG_PATH:
            print("No test log directories found.")
            return None

        LATEST_DATA_CSV_PATH = os.path.join(LATEST_LOG_PATH, "uart_export.csv")
        
        if not os.path.exists(LATEST_DATA_CSV_PATH):
            print(f"File '{LATEST_DATA_CSV_PATH}' not found.")
            return None

        timestamped_lines = []
        
        with open(LATEST_DATA_CSV_PATH, "r") as r:
            reader = csv.reader(r)
            header = next(reader, None)
            if not header:
                    print("Empty CSV file or no header row.")
                    return None
            try:
                # Get the column indices
                DATA_COL = header.index("data")
                START_TIME_COL = header.index("start_time")
            except ValueError:
                print("Required columns 'data' or 'start_time' not found.")
                return None
            
            # Flag to avoid storing consecutive newlines
            last_newline = False
            # Current text line (seperated by newline)
            current_line = ""
            # The timestamp of when the last line finished
            last_line_timestamp = 0.0
            
            # Header row is skipped because the iterator has passed it previously
            for row in reader:
                # Add data collumn which is probably last row
                data = row[DATA_COL]
                if data not in "\n\r":
                    current_line += data
                    last_newline = False
                elif not last_newline:
                    current_line_timestamp = float(row[START_TIME_COL])
                    timestamped_lines.append({
                        "line":current_line,
                        "fall_timestamp":current_line_timestamp
                        })
                    last_line_timestamp = current_line_timestamp
                    current_line = ""
                    last_newline = True
        return timestamped_lines

    def _get_index_of_last_result_line(
        self,
        timestamped_lines:Optional[List[Dict[str, float]]],
        line_index:int
        ):
        """Gets the index of the last result line.
        A result line is in the form `Test\s(\w+)\s(passed|failed)`

        Args:
            timestamped_lines (Optional[List[Dict[str, float]]]): Lines from `get_timestamped_lines()`
            line_index (int): Index of current line to search backwards from.
        """
        REGEX = r"Test\s(\w+)\s(passed|failed)"
        
        while not re.match(REGEX, timestamped_lines[line_index]):
            line_index -= 1
        return  line_index

    def _parse_failure_line(self,line_text: str) -> Optional[dict[str,str]]:
        # Regex to read the line of a failed test
        # Using "AUnitPlatformIO.ino:12: Assertion failed: (3) != (3)."
        # Group 1: File | Example: "AUnitPlatformIO.ino"
        # Group 2: Line | Example: "12"
        # Group 3: Message | Example: "Assertion failed: (3) != (3)."
        FAILURE_REGEX = r"(\w+.(?:cpp|ino)):(\d+):\s(.+)"
        match = re.match(FAILURE_REGEX, line_text)
        if match == None:
            return None
        return {
            "file": match.group(1),
            "line": match.group(2),
            "message": match.group(3),
        }

    def _generate_test_case(
        self,
        timestamped_lines:Optional[List[Dict[str, float]]],
        re_match:re.Match,
        line_index:int
        ):
        # Example: timestamped_lines
        
        # {'duration': 0.858, 'line': 'TestRunner started on 2 test(s).'},
        # {'duration': 0.002, 'line': 'Test exampleTest1 passed.'},
        # {'duration': 0.004, 'line': 'AUnitPlatformIO.ino:12: Assertion failed: (3) != (3).'},
        # {'duration': 0.002, 'line': 'Test exampleTest2 failed.'},
        # {'duration': 0.003, 'line': 'TestRunner duration: 0.010 seconds.'},
        # {'duration': 0.007,
        # 'line': 'TestRunner summary: 1 passed, 1 failed, 0 skipped, 0 timed out, out '
        #         'of 2 test(s).'}
        
        # Example: timestamped_lines in text form only
        
        # TestRunner started on 2 test(s).
        # Test exampleTest1 passed.
        # AUnitPlatformIO.ino:12: Assertion failed: (3) != (3).
        # Test exampleTest2 failed.
        # TestRunner duration: 0.010 seconds.
        # TestRunner summary: 1 passed, 1 failed, 0 skipped, 0 timed out, out 

        text_status = re_match.group(2)
        case_test_name = re_match.group(1)
        match text_status:
            case "passed":
                # Duration of a test that passed is the difference of duration of 
                # the sucess messsage the end of the last message
                case_duration = \
                    timestamped_lines[line_index]["fall_timestamp"] \
                    - timestamped_lines[line_index-1]["fall_timestamp"]
                case_status = TestStatus.PASSED
                test_case = TestCase(
                    name=case_test_name,
                    status=case_status,
                    duration=0.69 #TODO implement duration 
                )
            case "failed":
                case_status = TestStatus.FAILED
                # TODO Implement a scanner and compiler using _get_index_of_last_result_line
                # To find multiple assertions if you use them. For now, assume line_index-1
                parsed_line = self._parse_failure_line(
                    timestamped_lines[line_index-1]["line"]
                )
                if parsed_line == None:
                    raise Exception("Line incorrectly parsed")
                test_case = TestCase(
                    name=case_test_name,
                    status=case_status,
                    message=parsed_line["message"],
                    stdout=timestamped_lines[line_index-1]["line"],
                    duration=0.69,
                    source=TestCaseSource(
                        filename=parsed_line["file"], line=parsed_line["line"]
                    ),
                )
            case _: 
                print("Unexpected case_status")

        return test_case
            
            

    def create_all_test_cases(self) -> List[TestCase]:
        test_cases = []
        timestamped_lines = self.get_timestamped_lines()
        
        for index, line in enumerate(timestamped_lines):
            if re_match := re.match(r"Test\s(\w+)\s(passed|failed)",line["line"]):
                test_cases.append(self._generate_test_case(timestamped_lines, re_match, index))
            
        return test_cases
