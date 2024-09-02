import logging
import logging.handlers

PAPERTRAIL_HOST = 'logs2.papertrailapp.com'
PAPERTRAIL_PORT = 28987


handler = logging.handlers.SysLogHandler(address=(PAPERTRAIL_HOST,PAPERTRAIL_PORT))
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
# HANDLER.setformatter(formatter)

logging.basicConfig(level=logging.INFO,
# format="%(asctime)s %(levelname)s %(name)s %(message)s")
handlers =[handler])
def get_logger(name):
 logger = logging.getLogger(name)
 return logger

# logging.debug("this message will be reorded")
# logging.info("this message will be reordered")
# logging.warning("this message will be reordered")
# logging.critical("this message will be reordered")