from services.investor_ui_service import (
    DEFAULT_INVESTOR_WINDOW,
    INVESTOR_WINDOW_OPTIONS,
    normalize_investor_window,
)


def test_investor_window_options_are_product_windows():
    assert INVESTOR_WINDOW_OPTIONS == (
        90,
        180,
        365,
    )


def test_valid_investor_window_is_preserved():
    assert (
        normalize_investor_window("180")
        == 180
    )


def test_invalid_investor_window_falls_back_to_default():
    assert (
        normalize_investor_window("30")
        == DEFAULT_INVESTOR_WINDOW
    )

    assert (
        normalize_investor_window("not-a-number")
        == DEFAULT_INVESTOR_WINDOW
    )