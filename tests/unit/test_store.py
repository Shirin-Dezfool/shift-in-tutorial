import pytest

from snip.store import LinkRecord, Store


# SLI 3 (resolve correctness): the store hands back exactly what was put in.
def test_get_returns_the_record_that_was_put():
    store = Store()
    record = LinkRecord(code="abc123", url="https://example.com/x?y=1#z")
    store.put(record)

    got = store.get("abc123")

    assert got.code == "abc123"
    assert got.url == "https://example.com/x?y=1#z"


# SLI 2 (redirect availability): a miss is a KeyError, not a wrong or empty record.
def test_get_unknown_code_raises_key_error():
    with pytest.raises(KeyError):
        Store().get("missing")


def test_exists_reports_presence():
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com"))

    assert store.exists("abc123") is True
    assert store.exists("zzz999") is False


# SLI 5 (stats accuracy): a stored record is the live object, so a click recorded on it is
# visible on the next lookup; a new record starts at zero.
def test_new_record_starts_with_zero_clicks():
    assert LinkRecord(code="abc123", url="https://example.com").clicks == 0


def test_click_recorded_on_record_is_seen_on_next_get():
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com"))

    store.get("abc123").clicks += 1

    assert store.get("abc123").clicks == 1


def test_all_returns_every_record_and_is_empty_initially():
    store = Store()
    assert store.all() == []

    store.put(LinkRecord(code="a", url="https://a.example"))
    store.put(LinkRecord(code="b", url="https://b.example"))

    assert sorted(r.code for r in store.all()) == ["a", "b"]
