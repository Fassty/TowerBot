import logging
import logging.config

def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the entire project.
    """
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': level,
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'formatter': 'detailed',
                'level': 'INFO',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': level,
        },
        'loggers': {
            'my_module': {
                'handlers': ['console'],
                'level': level,
                'propagate': False,
            },
        },
    }
    logging.config.dictConfig(logging_config)