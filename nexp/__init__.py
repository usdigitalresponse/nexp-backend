# nexp.__init__

import logging

root = logging.getLogger()

# Deals with some lambda weirdness
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] [%(funcName)s] [line: %(lineno)s] - %(message)s",
)
