"""
test_microservice6.py — Unit tests for the BMI microservice
Written by: coen  (fixed & completed)

Communication: Plain text files (request.txt / response.txt)
Run the microservice first:  python microservice6.py
Then run this file        :  python test_microservice6.py

The client NEVER imports or calls microservice6.py directly.
All data exchange happens via text files on disk.

Text file protocol:
  Client writes  request.txt        → "<height_cm>,<weight_kg>"
  Client creates request_ready.flag → signals server a request is waiting
  Server writes  response.txt       → "OK,<bmi>,<category>"  or  "ERROR,<reason>"
  Server creates response_ready.flag→ signals client the response is ready
"""

import os
import time
import sys

REQUEST_FILE        = "request.txt"
RESPONSE_FILE       = "response.txt"
REQUEST_READY_FLAG  = "request_ready.flag"
RESPONSE_READY_FLAG = "response_ready.flag"
TIMEOUT             = 5.0   # seconds to wait for a response
POLL_INTERVAL       = 0.05


def BMICalculator(height_cm: float, weight_kg: float):
    """
    Send a request to the microservice via text files and return:
      - ""            if the service reports an error (negative inputs, etc.)
      - a dict        {"bmi": float, "category": str}  on success
    """
    # Write the request file
    with open(REQUEST_FILE, "w") as f:
        f.write(f"{height_cm},{weight_kg}\n")

    # Signal the server
    open(REQUEST_READY_FLAG, "w").close()

    # Wait for the server's response flag
    deadline = time.time() + TIMEOUT
    while not os.path.exists(RESPONSE_READY_FLAG):
        if time.time() > deadline:
            print("  [ERROR] Timed out waiting for microservice response.")
            print("          Is microservice6.py running?")
            sys.exit(1)
        time.sleep(POLL_INTERVAL)

    # Read the response
    with open(RESPONSE_FILE, "r") as f:
        line = f.read().strip()

    # Remove the response flag so the server is ready for the next request
    os.remove(RESPONSE_READY_FLAG)

    # Parse: OK,<bmi>,<category>  or  ERROR,<reason>
    parts = line.split(",", 2)
    if parts[0] == "ERROR":
        return ""

    bmi = float(parts[1])
    category = parts[2]
    return {"bmi": bmi, "category": category}


def bmi_value(height_cm, weight_kg):
    """Return only the numeric BMI float, or '' on error."""
    result = BMICalculator(height_cm, weight_kg)
    return "" if result == "" else result["bmi"]


def bmi_category(height_cm, weight_kg):
    """Return only the category string, or '' on error."""
    result = BMICalculator(height_cm, weight_kg)
    return "" if result == "" else result["category"]


# ── test runner ──────────────────────────────────────────────────────────────

def run_tests():
    print("Welcome to the microservice 6: BMI/Health calculator unit tests\n")

    passed = 0
    failed = 0

    def check(actual, expected):
        nonlocal passed, failed
        ok = actual == expected
        print(f"  Expected : {expected!r}")
        print(f"  Actual   : {actual!r}")
        print(f"  -> {'Passed test' if ok else 'Failed test'}\n")
        if ok:
            passed += 1
        else:
            failed += 1

    # ── negative / invalid inputs ─────────────────────────────────────────
    print("We are going to start by feeding the function negative inputs with")
    print("the expectation that it will terminate\n")

    print("Calling BMI calculator with inputs -1 (cm), 20 (kg)")
    check(bmi_value(-1, 20), "")

    print("Calling BMI calculator with inputs 20 (cm), -1 (kg)")
    check(bmi_value(20, -1), "")

    # ── numeric accuracy tests ────────────────────────────────────────────
    print("Next we will test for correctness by testing against precalculated values\n")

    print("Calling BMICalculator with inputs 20 (cm), 10 (kg)")
    check(bmi_value(20, 10), 250.0)

    print("Calling BMICalculator with inputs 180 (cm), 65 (kg)")
    # Note: the original test script had 20.10 — the mathematically correct value is 20.06
    check(bmi_value(180, 65), 20.06)

    print("Calling BMICalculator with inputs 160 (cm), 110 (kg)")
    check(bmi_value(160, 110), 42.97)

    # ── category tests ────────────────────────────────────────────────────
    print("Lastly we will test the accuracy of the categories that are returned\n")

    print("Calling BMICalculator with inputs 202 (cm), 68 (kg)")
    check(bmi_category(202, 68), "Underweight")

    print("Calling BMICalculator with inputs 189 (cm), 73 (kg)")
    check(bmi_category(189, 73), "Normal Weight")

    print("Calling BMICalculator with inputs 173 (cm), 85 (kg)")
    check(bmi_category(173, 85), "Overweight")

    print("Calling BMICalculator with inputs 159 (cm), 96 (kg)")
    check(bmi_category(159, 96), "Obese")

    # ── summary ───────────────────────────────────────────────────────────
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests.")
    print("\nThis concludes the microservice 6: BMI/Health calculator unit tests.")
    print("Thank you for testing with us.")


if __name__ == "__main__":
    run_tests()
