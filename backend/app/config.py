import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# Inject local ruby bin to system PATH for tool discovery
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RUBY_PATH = os.path.join(_BASE_DIR, "ruby", "bin")
if os.path.exists(_RUBY_PATH):
    os.environ["PATH"] = _RUBY_PATH + os.pathsep + os.environ.get("PATH", "")

class Settings(BaseSettings):
    ENVIRONMENT: str = "development" # development, production
    
    # AUTH
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_EMAIL: str = "gourabghosh828@gmail.com"
    
    @property
    def SECURE_COOKIES(self) -> bool:
        # Automatically returns True if in production, False otherwise
        return self.ENVIRONMENT.lower() == "production"

    # DATABASE
    DATABASE_URL: str

    # RECON KEYS
    SHODAN_API_KEY: str = ""
    SECURITYTRAILS_API_KEY: str = ""
    APININJAS_API_KEY: str = ""
    IPINFO_API_KEY: str = ""
    IPHUB_API_KEY: str = ""

    # THREAT INTEL KEYS
    VIRUSTOTAL_API_KEY: str = ""
    ABUSEIPDB_API_KEY: str = ""
    IPQUALITYSCORE_API_KEY: str = ""
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"

    # MAIL SETTINGS
    MAIL_USERNAME: str = "your-email@gmail.com"
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@reconxplorer.io"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    @property
    def API_NINJAS_WHOIS_KEY(self):
        return self.APININJAS_API_KEY

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
