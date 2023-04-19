from flask import current_app

def register_new_users_allowed():
    """Check if registering new users is allowed."""

    # Check settings
    key = "ALLOW_REGISTER_NEW_USERS"
    if key in current_app.config:
        return current_app.config[key]

    # Default.
    return True

# Hack for Python older than 3.9.
def removeSuffix(string, suffix):
    """Remove suffix."""

    try:
        # Try Python 3.9 method.
        return string.removesuffix(suffix)
    except AttributeError:
        # Use hack.
        if string.endswith(suffix):
            return string[:len(string) - len(suffix)]

    # Default case.
    return string
