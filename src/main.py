from config import validate_config
from extract import run_extraction


def main():
    validate_config()
    run_extraction()


if __name__ == "__main__":
    main()
