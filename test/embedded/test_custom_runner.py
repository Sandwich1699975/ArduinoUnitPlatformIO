from platformio.public import TestCase, TestCaseSource, TestStatus, UnityTestRunner

# This is gonna be one of thoses projects where you almost need unit tests for the unit tester

# This will run over all embedded/ test cases.
# TODO Make this loop over the logic output to parse AUnit test results


class CustomTestRunner(UnityTestRunner):
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
