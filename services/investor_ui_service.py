INVESTOR_WINDOW_OPTIONS = (
    90,
    180,
    365,
)

DEFAULT_INVESTOR_WINDOW = 365


def normalize_investor_window(value):
    """
    Return a supported investor-intelligence window.

    Invalid or unsupported query-string values fall back to
    the product default rather than raising a user-facing error.
    """

    try:
        window = int(value)

    except (
        TypeError,
        ValueError,
    ):
        return DEFAULT_INVESTOR_WINDOW

    if window not in INVESTOR_WINDOW_OPTIONS:
        return DEFAULT_INVESTOR_WINDOW

    return window