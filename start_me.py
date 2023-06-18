import subprocess
import time

def run_script():
    subprocess.run(['python', 'final_code.py'])
    print("Script executed")

while True:
    run_script()
    time.sleep(20)
