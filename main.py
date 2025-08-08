import sys

def main():
    print("Hello, World!")
    print("Command-line arguments:")
    for arg in sys.argv[1:]:
        print(f" - {arg}")

if __name__ == "__main__":
    main()
