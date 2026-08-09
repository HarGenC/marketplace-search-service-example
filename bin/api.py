import uvicorn

from src.fastapi import create_app
from src.logging_setup import setup_logging
from src.settings import Settings

settings = Settings()
setup_logging(settings.log_level)

app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_config=None,
    )
