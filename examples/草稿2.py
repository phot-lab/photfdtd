import subprocess

# 执行 a.py
result_a = subprocess.run(["python", "ring_ex_no_y_pml.py"], capture_output=True, text=True)
print("Output of a.py:\n", result_a.stdout)

# 执行 b.py
result_b = subprocess.run(["python", "ring_ex.py"], capture_output=True, text=True)
print("Output of b.py:\n", result_b.stdout)
