from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashea la contraseña, truncándola a 72 bytes para cumplir con las limitaciones de bcrypt."""
    if not password:
        raise ValueError("Password no puede ser vacío o None")

    # Convertir a string si viene como SecretStr o similar
    if not isinstance(password, str):
        password = str(password)

    # Truncar si excede 72 bytes
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        encoded = encoded[:72]
        password = encoded.decode("utf-8", errors="ignore")

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña sin lanzar error si es demasiado larga."""
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)

    encoded = plain_password.encode("utf-8")
    if len(encoded) > 72:
        encoded = encoded[:72]
        plain_password = encoded.decode("utf-8", errors="ignore")

    return pwd_context.verify(plain_password, hashed_password)
