"""Run a review check, retain its complete output, and print only a concise tail."""
from pathlib import Path
import subprocess
import sys

name, directory, *command = sys.argv[1:]
log = Path(__file__).parent / f"{name}.log"
with log.open("w") as output:
    result = subprocess.run(command, cwd=directory, stdout=output, stderr=subprocess.STDOUT)
print(f"{name}: exit {result.returncode}; complete output in {log.name}")
print("\n".join(log.read_text().splitlines()[-30:]))
sys.exit(result.returncode)
