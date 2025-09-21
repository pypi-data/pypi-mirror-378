from .core import find_max
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: MaxNumberLib <num1> <num2> ...")
        return
    try:
        numbers = [float(x) for x in sys.argv[1:]]
    except ValueError:
        print("Please provide valid numbers.")
        return
    print("Max:", find_max(numbers))

if __name__ == "__main__":
    main()