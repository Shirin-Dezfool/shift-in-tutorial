import pytest

from snip import shortener
from snip.store import Store


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    monkeypatch.setattr(shortener, "store", Store())


def test_code_collision_does_not_overwrite_existing_link(monkeypatch):
    codes = iter(["ABCDEF", "ABCDEF", "GHIJKL"])
    monkeypatch.setattr(shortener, "generate_code", lambda: next(codes))

    first = shortener.create_link("https://first.example")
    second = shortener.create_link("https://second.example")

    assert shortener.resolve(first.code).url == "https://first.example"
    assert second.code == "GHIJKL"  # the retry must produce the next generated code
    assert shortener.resolve(second.code).url == "https://second.example"


# SLI 2 (redirect availability): a miss must surface as a clean, catchable KeyError (which the
# API layer turns into a 404), and must not have side effects.
def test_resolve_unknown_code_raises_key_error_and_creates_nothing():
    with pytest.raises(KeyError):
        shortener.resolve("nope00")

    assert shortener.list_links() == []


def test_stats_unknown_code_raises_key_error():
    with pytest.raises(KeyError):
        shortener.stats("nope00")


# SLI 3 (resolve correctness): resolve returns exactly what create stored, and the right link
# when several exist.
@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://example.com/a/b?x=1&y=2#frag",
        "https://example.com/café?q=a b",
        "http://example.com/" + "a" * 5000,
        "HTTPS://Example.COM/Path/CaseSensitive?Q=MixedCase ",
    ],
)
def test_resolve_returns_exact_url_that_was_created(url):
    record = shortener.create_link(url)

    assert shortener.resolve(record.code).url == url


def test_resolve_picks_the_right_link_among_many():
    a = shortener.create_link("https://a.example")
    b = shortener.create_link("https://b.example")

    assert shortener.resolve(a.code).url == "https://a.example"
    assert shortener.resolve(b.code).url == "https://b.example"


def test_generate_code_has_six_alphanumeric_characters():
    for _ in range(200):
        code = shortener.generate_code()
        assert len(code) == 6
        assert code.isascii() and code.isalnum()


# SLI 5 (stats accuracy): clicks equal follows.
def test_new_link_has_zero_clicks():
    assert shortener.create_link("https://example.com").clicks == 0


def test_n_follows_record_exactly_n_clicks():
    record = shortener.create_link("https://example.com")

    for _ in range(7):
        shortener.resolve(record.code)

    assert shortener.stats(record.code).clicks == 7


def test_reading_stats_or_listing_does_not_count_as_a_click():
    record = shortener.create_link("https://example.com")

    shortener.stats(record.code)
    shortener.list_links()

    assert shortener.stats(record.code).clicks == 0


def test_following_one_link_does_not_change_another_links_clicks():
    a = shortener.create_link("https://a.example")
    b = shortener.create_link("https://b.example")

    shortener.resolve(a.code)

    assert shortener.stats(b.code).clicks == 0


def test_failed_follow_does_not_count_for_any_link():
    record = shortener.create_link("https://example.com")

    with pytest.raises(KeyError):
        shortener.resolve("nope00")

    assert shortener.stats(record.code).clicks == 0


def test_list_links_returns_every_created_link():
    a = shortener.create_link("https://a.example")
    b = shortener.create_link("https://b.example")

    assert {r.code for r in shortener.list_links()} == {a.code, b.code}
