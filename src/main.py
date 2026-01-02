from config import Config, validate_config


def main():
    validate_config()
    print("Config OK")
    print(Config.LUCCA_API_URL)


if __name__ == "__main__":
    main()
