import string
from hashids import Hashids
from database.catch import redis_handler


class UuidGenerator:
    def __init__(self, salt: str = "pass", min_length: int = 6):
        self.alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
        self.hashids = Hashids(
            salt=salt, min_length=min_length, alphabet=self.alphabet)

    def encode(self, num: int) -> str:
        if num < 0:
            raise ValueError("Num must be non-negative")
        return self.hashids.encode(num)

    def decode(self, code: str) -> int | None:
        decoded = self.hashids.decode(code)
        print(decoded)
        return decoded[0] if decoded else None

    async def generate_uuid(self):
        next_num = await redis_handler.get_next_num()
        uuid = self.encode(next_num)
        print(f"最新counter:{next_num}")
        print(uuid)
        return uuid


uuid_generator = UuidGenerator()
