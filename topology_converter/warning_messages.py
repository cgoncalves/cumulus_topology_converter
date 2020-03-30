"""
Serves as a global logger that can be used to print messages at the end of a Topology Converter run.
"""

class WarningMessages:
    """
    An instance of this class can be used to create and print warning messages
    """
    # A static list of warnings that will be shared amongst WarningMessages instances
    warnings = []

    def append(self, msg):
        """ Wrapper for appending a message to the list """
        WarningMessages.warnings.append(msg)

    def print_warnings(self):
        """ Prints all warnings that have been generated so far """
        for warning in WarningMessages.warnings:
            print(warning)
