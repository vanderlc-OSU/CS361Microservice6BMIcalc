"""
microservice6.py — BMI / Health Calculator Microservice
Communication: Plain text files

REQUEST FILE  (written by client): request.txt
    Format:  <height_cm>,<weight_kg>
    Example: 180,65

RESPONSE FILE (written by server): response.txt
    Format on success: OK,<bmi>,<category>
    Format on error:   ERROR,<reason>
    Example: OK,20.06,Normal Weight

Workflow:
    1. Client writes request.txt
    2. Client writes request_ready.flag  (signals server)
    3. Server detects flag, reads request.txt, deletes flag
    4. Server writes response.txt
    5. Server writes response_ready.flag (signals client)
    6. Client detects flag, reads response.txt, deletes flag

BMI formula : weight_kg / (height_m ** 2)
Categories  :
    bmi < 18.5          → Underweight
    18.5 <= bmi < 25.0  → Normal Weight
    25.0 <= bmi < 30.0  → Overweight
    bmi >= 30.0         → Obese
"""

import os
import time

REQUEST_FILE        = "request.txt"
RESPONSE_FILE       = "response.txt"
REQUEST_READY_FLAG  = "request_ready.flag"
RESPONSE_READY_FLAG = "response_ready.flag"
POLL_INTERVAL       = 0.05   # seconds between flag checks


def calculate_bmi(height_cm: float, weight_kg: float) -> str:
    """Return a response line: OK,<bmi>,<category>  or  ERROR,<reason>"""
    if height_cm <= 0 or weight_kg <= 0:
        return "ERROR,Height and weight must be positive numbers"

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal Weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return f"OK,{bmi},{category}"


def run_server():
    # Clean up any leftover files from a previous run
    for f in (REQUEST_FILE, RESPONSE_FILE, REQUEST_READY_FLAG, RESPONSE_READY_FLAG):
        if os.path.exists(f):
            os.remove(f)

    print("[microservice6] BMI service is running — waiting for requests ...")
    print(f"  Request file : {REQUEST_FILE}")
    print(f"  Response file: {RESPONSE_FILE}\n")

    while True:
        # Wait for the client to signal a request is ready
        if not os.path.exists(REQUEST_READY_FLAG):
            time.sleep(POLL_INTERVAL)
            continue

        # Read the request
        try:
            with open(REQUEST_FILE, "r") as f:
                line = f.read().strip()
            height_cm, weight_kg = (float(x) for x in line.split(","))
            response = calculate_bmi(height_cm, weight_kg)
        except Exception as exc:
            response = f"ERROR,Bad request: {exc}"

        # Remove the request flag
        os.remove(REQUEST_READY_FLAG)

        # Write the response then signal the client
        with open(RESPONSE_FILE, "w") as f:
            f.write(response + "\n")
        open(RESPONSE_READY_FLAG, "w").close()

        print(f"[microservice6] Served: {line!r}  ->  {response!r}")


if __name__ == "__main__":
    run_server()