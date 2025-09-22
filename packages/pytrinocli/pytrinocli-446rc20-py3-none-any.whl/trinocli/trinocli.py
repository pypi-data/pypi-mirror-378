from pathlib import Path
import sys
import subprocess

current_directory = Path(__file__).parent
jar_path = current_directory.joinpath("bin", "trino-cli.jar")


def main():
    subprocess.run([jar_path] + sys.argv[1:])
