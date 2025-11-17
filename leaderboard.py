import os
import sys
from subprocess import Popen, PIPE
from tabulate import tabulate

bench_type = sys.argv[1]
group_folders = sys.argv[2:]

results = []

# Save original working directory
cwd = os.getcwd()

for folder in group_folders:
    file = f"{bench_type}.py"
    folder_path = os.path.join(cwd, folder)

    # Ensure folder exists
    if not os.path.exists(os.path.join(folder_path, file)):
        continue

    print("Evaluating:", f"{folder}/{file}")

    # Change into the folder
    os.chdir(folder_path)

    # Run script inside the folder
    process = Popen(["python", file], stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()

    # Go back immediately
    os.chdir(cwd)

    text = output.decode("utf-8", errors="replace")

    # Extract "Result:" line
    lines = [line for line in text.splitlines() if line.startswith("Result:")]

    if len(lines) != 1:
        print("Invalid output format:", text)
        results.append((float("inf"), folder))
        continue

    result_line = lines[0]
    print(result_line)

    try:
        # format: "Result: 123.45 ms"
        value = float(result_line.split()[1])
    except:
        value = float("inf")

    results.append((value, folder))

# Sort and print results
results.sort(key=lambda x: x[0])

formatted_results = [
    [idx + 1, folder, str(value)]
    for idx, (value, folder) in enumerate(results)
]

print(tabulate(formatted_results, headers=["Rank", "Group", "Time [ms]"]))