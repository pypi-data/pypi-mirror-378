from pathlib import Path
import sys
import subprocess

current_directory = Path(__file__).parent
jar_path = current_directory.joinpath("bin", "void.jar")


def main():
    raise NotImplemented
    # subprocess.run([jar_path] + sys.argv[1:])
