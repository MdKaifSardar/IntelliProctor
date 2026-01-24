import sys
# Hack: Disable tensorflow import to prevent protobuf conflict with MediaPipe
# The user's environment has an incompatible tensorflow/protobuf combo.
sys.modules["tensorflow"] = None

from app.main import main

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"Error importing app modules: {e}")
        print("Make sure you are running from the root directory and 'app' is accessible.")
        sys.exit(1)
