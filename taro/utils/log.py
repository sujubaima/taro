import os
import logging
import logging.handlers

from taro import options


FILE_FORMATS = logging.Formatter("[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d] %(message)s")


def file_handler(log_dir, level):
    handler = logging.handlers.RotatingFileHandler(os.path.join(log_dir, 'debug.log'), 'a', 20971520, 3)
    handler.setFormatter(FILE_FORMATS)
    handler.setLevel(level)
    return handler

def init_logger(log_dir=None):
    if log_dir is None:
        log_dir = options.LOG_DIR
    #os.environ["LOG_ROOT"] = log_dir
    log_level = logging.INFO

    log_dir = os.path.expanduser(log_dir)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler(log_dir, log_level))
    return logger


class _LOG(object):

    _instance = None

    @staticmethod
    def init():
        init_logger()
        LOG._instance = logging.getLogger("taro")

    @staticmethod
    def debug(*args, **kwargs):
        LOG._instance.debug(*args, **kwargs)

    @staticmethod
    def info(*args, **kwargs):
        LOG._instance.info(*args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        LOG._instance.error(*args, **kwargs)

    @staticmethod
    def exception(*args, **kwargs):
        LOG._instance.exception(*args, **kwargs)

#LOG = init_logger(options.LOG_DIR)
