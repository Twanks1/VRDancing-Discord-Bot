import logging


class Logger:
    def __init__(self, name, logLevel):
        logger = logging.getLogger("discord")
        logger.setLevel(logLevel)
        handler = logging.FileHandler(
            filename=name + ".log", encoding="utf-8", mode="w"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logging.basicConfig()  # Print logging to console
        self.logger = logger

    def Log(self, msg):
        self.logger.log(logging.INFO, msg)

    def Warn(self, msg):
        self.logger.warning(msg)
