import logging

logging.basicConfig(
	level=logging.DEBUG,
	format="%(levelname)s - %(message)s"
)

def get_logger(name):
	return logging.getLogger(name)

def log_message(logger, level, component, message):
	PAD = 15
	format_string = f"{component.ljust(PAD)} | {message}"

	level = level.upper()
	if level == "INFO":
		logger.info(format_string)
	elif level == "ERROR":
		logger.error(format_string)
	elif level == "DEBUG":
		logger.debug(format_string)
	elif level == "WARNING":
		logger.warning(format_string)
	elif level == "CRITICAL":
		logger.critical(format_string)