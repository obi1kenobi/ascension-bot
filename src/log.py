import logging

# http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground
# with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def create_logger(logger_name, color):
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging.INFO)

  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.DEBUG)

  color_seq = COLOR_SEQ % (30 + color)
  format_str = (color_seq + BOLD_SEQ + 
    "%(asctime)s - %(name)s - %(levelname)s -" + RESET_SEQ + " %(message)s")
  formatter = logging.Formatter(format_str, "%H:%M:%S")
  console_handler.setFormatter(formatter)

  logger.addHandler(console_handler)
  return logger

