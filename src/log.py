import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("/var/log/killer.log")
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
