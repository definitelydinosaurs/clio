import sys
from urllib.parse import urlparse

def main():
    print("Hello, World!")
    print("Command-line arguments:")
    for arg in sys.argv[1:]:
        print(f" - {arg}")
    parsed = urlparse(sys.argv[1] if len(sys.argv) > 1 else "")
    print(f"Parsed URL: {parsed}")

if __name__ == "__main__":
    main()
