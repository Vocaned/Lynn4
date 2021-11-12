class LynnError(Exception):
    """Custom error message, raise to send an error embed."""

    def __init__(self, title: str = None, text: str = None):
        self.title: str = title
        """The error title."""
        self.text: str = text
        """The error text."""

class ExtensionError(LynnError):
    ...

class ExtensionAlreadyLoadedError(ExtensionError):
    def __init__(self, extension: str):
        super().__init__(title='Extension already loaded!', text='Extension: ' + extension)

class ExtensionNotFound(ExtensionError):
    def __init__(self, extension: str):
        super().__init__(title='Extension not found!', text='Extension: ' + extension)

class ExtensionNotLoaded(ExtensionError):
    def __init__(self, extension: str):
        super().__init__(title='Extension not loaded!', text='Extension: ' + extension)

class ExtensionNoClass(ExtensionError):
    def __init__(self, extension: str):
        super().__init__(title='Extension does not have an Extension class.', text='Extension: ' + extension)