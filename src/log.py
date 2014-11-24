import logging

# Modified a bit from
# http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

# The background is set with 40 plus the number of the color, and the foreground
# with 30
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = [
  COLOR_SEQ % (30 + i) for i in xrange(8)
]

# TODO(ddoucet): how can we take advantage of the hierarchy?
# e.g., let's say we wanted to turn off all logs from P1...

def initialize_logging(log_level):
  # create a console handler with our formatting
  console_handler = logging.StreamHandler()
  console_handler.setLevel(log_level)

  format_str = ("%(color_seq)s" + BOLD_SEQ +
    "%(asctime)s - %(name)s - %(levelname)s -" + RESET_SEQ + " %(message)s")
  formatter = logging.Formatter(format_str, "%H:%M:%S")
  console_handler.setFormatter(formatter)

  # grab the root logger and attach the console handler
  root = logging.getLogger()
  root.setLevel(log_level)
  root.addHandler(console_handler)

def create_logger(logger_name):
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging.DEBUG)
  return logger

