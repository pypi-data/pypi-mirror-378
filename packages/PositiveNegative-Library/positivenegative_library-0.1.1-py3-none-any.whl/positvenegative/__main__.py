
from .core import check_number
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: PosNegLib <number>")
        return
    try:
        n = float(sys.argv[1])
    except ValueError:
        print("Please provide a valid number.")
        return
    print(f"{n} is {check_number(n)}")

if __name__ == "__main__":
    main()