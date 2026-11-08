import base64
import json

import pytest

from trackcoder.errors import CollectionError
from trackcoder.software import calculate_software_metrics, minutes_from_aria
from trackcoder.trackme import decode_trackme, lines_for_day


def encoded(payload):
    return base64.b64encode(json.dumps(payload).encode()).decode()


def test_trackme_decoder_combines_javascript_and_jsx():
    payload = decode_trackme(encoded({
        "01/02/2026": {
            "lines_of_code": {"html": 10, "css": 5, "javascript": 20, "javascriptreact": 7}
        }
    }))
    assert lines_for_day(payload, "2026-01-02") == (10, 5, 27, 42)


def test_trackme_missing_day_is_zero_not_an_error():
    assert lines_for_day({}, "2026-01-02") == (0, 0, 0, 0)


def test_trackme_invalid_payload_is_rejected():
    with pytest.raises(CollectionError):
        decode_trackme("not base64!")
    with pytest.raises(CollectionError):
        lines_for_day({"01/02/2026": {"lines_of_code": {"html": -1}}}, "2026-01-02")


def test_software_aria_parser_supports_decimal_minutes():
    assert minutes_from_aria("Mon, 90. Active Code Time") == 90
    assert minutes_from_aria("Tue, 12.5. Code Time") == 12
    with pytest.raises(CollectionError):
        minutes_from_aria("Monday without a duration")


def test_software_calculation_preserves_legacy_definitions_and_override():
    metrics = calculate_software_metrics(30, 60)
    assert metrics.code_time_minutes == 90
    assert metrics.focus_minutes == 150
    assert calculate_software_metrics(0, 0).focus_minutes == 0
    assert calculate_software_metrics(30, 60, focus_override=75).focus_minutes == 75
