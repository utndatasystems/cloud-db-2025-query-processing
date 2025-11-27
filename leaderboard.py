import os
import sys
from subprocess import Popen, PIPE
from tabulate import tabulate

bench_type = sys.argv[1]
group_folders = sys.argv[2:]

results = []

for folder in group_folders:
    file = f"{bench_type}.py"
    file_path = os.path.join(folder, file)

    if not os.path.exists(file_path):
        continue

    print("Evaluating:", file_path)

    # Run using full path
    process = Popen([sys.executable, file_path], stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()

    text = output.decode("utf-8", errors="replace")

    lines = [line for line in text.splitlines() if line.startswith("Result:")]

    if len(lines) != 1:
        print("Invalid output format:", text)
        results.append((float("inf"), folder))
        continue

    result_line = lines[0]
    print(result_line)

    try:
        value = float(result_line.split()[1])
    except:
        value = float("inf")

    results.append((value, folder))

results.sort(key=lambda x: x[0])

formatted_results = [
    [idx + 1, folder, str(value)]
    for idx, (value, folder) in enumerate(results)
]

print(tabulate(formatted_results, headers=["Rank", "Group", "Time [ms]"]))