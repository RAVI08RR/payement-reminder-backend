from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    print("DEBUG hash_password called")
    print("TYPE:", type(password))
    print("VALUE:", password)
    print("LENGTH:", len(str(password)))
    
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    # bcrypt-safe truncation
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = plain_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.verify(plain_password, hashed_password)
