import logging

from .components import TextKPIInferenceCurator
from .config import config, logging_config

# Logger for this package
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging_config.get_console_handler())
logger.propagate = False
