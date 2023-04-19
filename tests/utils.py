# Hack for Python older than 3.9.
def removePrefix(string, prefix):
    """Remove prefix."""

    try:
        # Try Python 3.9 method.
        return string.removeprefix(prefix)
    except AttributeError:
        # Use hack.
        if string.startswith(prefix):
            return string[len(prefix):]

    # Default case.
    return string

# Hack to avoid URL prefix error.
def removeUrlPrefix(url):
    """Remove the prefix from the url."""

    prefix = "http://localhost"
    return removePrefix(url, prefix)
