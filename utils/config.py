import logging
import configparser


class Config(configparser.ConfigParser):
    def __init__(self, logger: logging.Logger, file='config.ini'):
        super().__init__()
        self._logger = logger
        self._file = file
        self.read(self._file)

    def save(self):
        try:
            with open(self._file, 'w') as stream:
                self.write(stream)
        except OSError as e:
            self._logger.error(e)
