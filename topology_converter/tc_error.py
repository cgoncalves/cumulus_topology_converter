"""
Topology Converter-specific exceptions
"""
class TcError(BaseException):
    """ Provides a base exception that more specific errors can inherit from """

class RenderError(TcError):
    """ An error encountered when rendering Jinja templates """
    def __init__(self, message):
        self.message = message
        super().__init__()
