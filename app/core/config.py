from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "12345"
    MYSQL_HOST: str = "localhost"
    MYSQL_DB: str = "events_db"
    
    SECRET_KEY: str = "secret-key-demo-123"  # 🔸 cámbialo por algo más fuerte en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}/{self.MYSQL_DB}"

settings = Settings()
