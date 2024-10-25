import logging
import enum

from src.api.config import LOG_LEVEL


LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevels(str, enum.Enum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging():
    log_level = str(LOG_LEVEL).upper()  # cast to string
    log_levels = list(log_level.value for log_level in LogLevels)  # Enum 값을 리스트로

    if log_level not in log_levels:
        # we use error as the default log level
        logging.basicConfig(level=LogLevels.error.value)  # .value로 열거형 값 사용
        return

    if log_level == LogLevels.debug.value:  # Enum 값을 비교할 때도 .value 사용
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)

    # sometimes the slack client can be too verbose
    logging.getLogger("slack_sdk.web.base_client").setLevel(logging.CRITICAL)
