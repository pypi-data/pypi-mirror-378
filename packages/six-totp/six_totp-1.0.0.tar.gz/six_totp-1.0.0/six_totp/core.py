import random

def generate_totp() -> str:
    totp = random.randint(0, 999_999)
    return f"{totp:06}"