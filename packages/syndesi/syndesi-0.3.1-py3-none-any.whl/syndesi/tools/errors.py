# File : errors.py
# Author : Sébastien Deriaz
# License : GPL

class SyndesiError(Exception):
    """Base class for all Syndesi errors"""

class BackendCommunicationError(SyndesiError):
    """Error with backend communication"""

class BackendError(SyndesiError):
    """Error inside the backend"""

class AdapterBackendError(BackendError):
    """Error inside an adapter backend"""

class AdapterError(SyndesiError):
    """Error inside an adapter frontend"""