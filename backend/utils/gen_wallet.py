import random

def generate_wallet_id(owner_type: str):
    prefix = "USR" if owner_type == "user" else "VND"
    rand = random.randint(1000, 9999)
    return f"WAL-{prefix}-{rand}"
