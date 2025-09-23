import argparse
from mycalculator import operations

def main():
    parser = argparse.ArgumentParser(description="Simple Calculator CLI")
    parser.add_argument("operation", choices=["add", "subtract", "multiply", "divide"], help="Operation to perform")
    parser.add_argument("a", type=float, help="First number")
    parser.add_argument("b", type=float, help="Second number")
    args = parser.parse_args()

    if args.operation == "add":
        result = operations.add(args.a, args.b)
    elif args.operation == "subtract":
        result = operations.subtract(args.a, args.b)
    elif args.operation == "multiply":
        result = operations.multiply(args.a, args.b)
    elif args.operation == "divide":
        result = operations.divide(args.a, args.b)

    print("Result:", result)

if __name__ == "__main__":
    main()