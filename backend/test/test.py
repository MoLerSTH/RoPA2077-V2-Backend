import test.schemas as schemas
from pwdlib import PasswordHash

class LoginRequest:
    username: str
    password: str

# password_hash = PasswordHash.recommended()

# password = input("Enter your password: ")
# hash = password_hash.hash(password)

# change_password = input("Enter your password again to verify: ")
# valid = password_hash.verify(change_password, hash)

# if valid:
#     print("Password is valid!")
# else:
#     print("Password is invalid!")
password = input("Enter your password: ")
def hash_password(password: LoginRequest) -> str:
    password_hash = PasswordHash.recommended()
    return password_hash.hash(password)