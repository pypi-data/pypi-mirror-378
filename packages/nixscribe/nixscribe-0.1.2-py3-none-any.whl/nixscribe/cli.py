from .main import main
import sys

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting…")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
