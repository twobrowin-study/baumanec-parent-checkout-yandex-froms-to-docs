from pathlib import Path

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

import index  # noqa: E402

if __name__ == "__main__":
    index.handler(
        {"body": Path("test-body.json").read_text(), "isBase64Encoded": False},
        {"test": True},
    )
