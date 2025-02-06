def file_exists(filename):
    """
    Checks if a file exists by trying to open it.
    """
    try:
        with open(filename, "r"):
            return True
    except OSError:
        return False
