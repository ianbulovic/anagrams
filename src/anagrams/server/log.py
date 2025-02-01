import logging
import logging.handlers

from uvicorn.logging import ColourizedFormatter

handler = logging.StreamHandler()
handler.setFormatter(
    ColourizedFormatter(
        "{levelprefix:<8} {name} - {message}", style="{", use_colors=True
    )
)
logging.basicConfig(level=logging.INFO, handlers=[handler])


def get_logger(name: str):
    return logging.getLogger(name)
