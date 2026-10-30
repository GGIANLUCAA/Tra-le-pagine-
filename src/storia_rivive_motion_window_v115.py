"""Offline, fail-closed pre-freeze source-window guard for La Storia Rivive.

Checks timing metadata only. A pass is NOT proof of actual visual motion,
source authenticity, rights, I2I quality, or artistic approval.
"""
from fractions import Fraction


def check_source_window(start_pts, freeze_pts, time_base, *, min_seconds=0.9, max_seconds=2.5):
    """Return (ok, reason) using exact rational source clock arithmetic."""
    if type(start_pts) is not int or type(freeze_pts) is not int:
        return False, "INVALID_PTS_TYPE"
    if start_pts < 0 or freeze_pts <= start_pts:
        return False, "NO_PRE_FREEZE_SOURCE_WINDOW"
    if not isinstance(time_base, str) or '/' not in time_base:
        return False, "INVALID_TIME_BASE"
    try:
        numerator, denominator = time_base.split('/')
        if not numerator.isdigit() or not denominator.isdigit():
            return False, "INVALID_TIME_BASE"
        num, den = int(numerator), int(denominator)
        if num <= 0 or den <= 0:
            return False, "INVALID_TIME_BASE"
        duration = (freeze_pts - start_pts) * Fraction(num, den)
    except (ValueError, ZeroDivisionError):
        return False, "INVALID_TIME_BASE"
    if duration < Fraction(str(min_seconds)):
        return False, "PRE_FREEZE_WINDOW_TOO_SHORT"
    if duration > Fraction(str(max_seconds)):
        return False, "PRE_FREEZE_WINDOW_TOO_LONG"
    return True, "TEMPORAL_WINDOW_METADATA_PASS_MOTION_UNVERIFIED"
