import logging
import colorlog
from ctypes import windll

#Special HACK for correct DPI
user32 = windll.user32
user32.SetProcessDPIAware()

logging.basicConfig(filename='output.log', level=logging.DEBUG)
logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    colorlog.ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s', 
        log_colors={
            'DEBUG':    'fg_bold_cyan',
            'INFO':     'fg_bold_green',
            'WARNING':  'bg_bold_yellow,fg_bold_blue',
            'ERROR':    'bg_bold_red,fg_bold_white',
            'CRITICAL': 'bg_bold_red,fg_bold_yellow',
    },secondary_log_colors={}

    ))
logger.addHandler(handler)

logger.debug('This is a DEBUG message. These information is usually used for troubleshooting')
logger.info('This is an INFO message. These information is usually used for conveying information')
logger.warning('some warning message. These information is usually used for warning')
logger.error('some error message. These information is usually used for errors and should not happen')
logger.critical('some critical message. These information is usually used for critical error, and will usually result in an exception.')