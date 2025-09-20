from pathlib import Path
import sys
import subprocess

current_directory = Path(__file__).parent
binary_path = current_directory.joinpath("bin", "koolbox")


def main():
    subprocess.run([binary_path] + sys.argv[1:])
