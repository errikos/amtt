"""Logging-related definitions."""

import logging


class MsgCountHandler(logging.Handler):
    """Custom logging handler class to count warnings and errors."""

    no_warnings = 0
    no_errors = 0

    def __init__(self, *args, **kwargs):
        """Initialize MsgCountHandler."""
        super(MsgCountHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        """Handle log record override."""
        if record.levelname.lower() == 'warning':
            MsgCountHandler.no_warnings += 1
        elif record.levelname.lower() == 'error':
            MsgCountHandler.no_errors += 1
