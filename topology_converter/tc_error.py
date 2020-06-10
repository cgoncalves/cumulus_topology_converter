"""
Topology Converter-specific exceptions
"""

from .styles import styles

class TcError(Exception):
    """ Provides a base exception that more specific errors can inherit from """
    def __init__(self, message='', print_on_create=True):
        self.message = message
        super().__init__()
        if print_on_create:
            self.print_error()

    def __str__(self):
        return self.message

    def print_error(self):
        print(styles.FAIL + styles.BOLD + ' ### ERROR:', self.message + styles.ENDC)

class RenderError(TcError):
    """ An error encountered when rendering Jinja templates """

class LintError(TcError):
    """ An error encountered when linting a DOT file """
    def __init__(self, message, print_on_create=True):
        self.message = message
        super().__init__(message, print_on_create)
