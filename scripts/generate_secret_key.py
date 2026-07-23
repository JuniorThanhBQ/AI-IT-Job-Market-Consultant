#!/usr/bin/env python3
import secrets
import sys


def generate_secret_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    length = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    token = generate_secret_token(length)
    print(token)
