import string
from hashids import Hashids
from database.catch import redis_handler
# ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
# BASE = len(ALPHABET)


# class UuidGenerator:

#     def encode(self, num: int) -> str:
#         """把正整數 num 轉成 bijective base-62 字串（短碼）"""
#         if num < 1:
#             raise ValueError("Num must be >= 1")
#         s = []
#         while num:
#             num, rem = divmod(num-1, self.base)
#             s.append(self.alphabet[rem])

#         return "".join(reversed(s))

#     def decode(self, code: str) -> int:
#         """把 bijective base-62 短碼還原回對應的整數 ID。"""

#         for char in code:
#             num = num * self.base + self.alphabet.index(char) + 1
#         return num


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
