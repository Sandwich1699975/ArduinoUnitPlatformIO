import sys
import os

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_dir, "include"))

from platformio.public import UnityTestRunner
from logic_analyzer import LogicAnalyser  # type: ignore
from test_parser import TestParser  # type: ignore


class CustomTestRunner(UnityTestRunner):

    def setup(self):
        return super().setup()

    def stage_testing(self):
        # 1. Gather test results from Serial, HTTP, Socket, or other sources
        print("Starting logic")
        logic = LogicAnalyser();
        # Setup serial analysis
        self.LOGIC_BOOT_OK = logic.start_serial_analysis()
        if not self.LOGIC_BOOT_OK:
            raise RuntimeError("Error starting Logic2")

        # 2. Report test results (add cases)
        parser = TestParser()
        for case in parser.create_all_test_cases():
            self.test_suite.add_case(case)
