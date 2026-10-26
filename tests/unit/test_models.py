import pytest
from pydantic import ValidationError

from snip.models import CreateLinkRequest, LinkResponse
from snip.store import LinkRecord


# SLIs 3 and 5: the response reports the stored URL and click count unchanged.
def test_link_response_copies_code_url_and_clicks_from_record():
    record = LinkRecord(code="abc123", url="https://example.com/a b?x=é", clicks=4)

    response = LinkResponse.from_record(record)

    assert (response.code, response.url, response.clicks) == (
        "abc123",
        "https://example.com/a b?x=é",
        4,
    )


# SLI 4 (create validation): the only rejection the model itself performs is a missing or
# non-string url.
def test_create_request_requires_a_url():
    with pytest.raises(ValidationError):
        CreateLinkRequest()


def test_create_request_rejects_non_string_url():
    with pytest.raises(ValidationError):
        CreateLinkRequest(url=123)
