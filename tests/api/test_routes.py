import pytest
from fastapi.testclient import TestClient

from snip import shortener
from snip.main import app
from snip.store import Store

LINK_KEYS = {"code", "url", "clicks"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(shortener, "store", Store())
    return TestClient(app)


def create(client, url="https://example.com"):
    return client.post("/api/links", json={"url": url})


def test_create_link_returns_201_with_link_shape(client):
    response = create(client)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == LINK_KEYS
    assert isinstance(body["code"], str)
    assert isinstance(body["url"], str)
    assert isinstance(body["clicks"], int)


def test_list_links_returns_200_with_a_list_of_link_shapes(client):
    create(client)

    response = client.get("/api/links")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list) and len(body) == 1
    assert set(body[0]) == LINK_KEYS


def test_list_links_returns_200_and_empty_list_when_no_links(client):
    response = client.get("/api/links")

    assert response.status_code == 200
    assert response.json() == []


def test_stats_returns_200_with_link_shape(client):
    code = create(client).json()["code"]

    response = client.get(f"/api/links/{code}/stats")

    assert response.status_code == 200
    assert set(response.json()) == LINK_KEYS


def test_stats_unknown_code_returns_404_with_detail(client):
    response = client.get("/api/links/nope00/stats")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_follow_returns_307_with_a_location_header(client):
    code = create(client).json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert "location" in response.headers


def test_follow_unknown_code_returns_404_with_detail(client):
    response = client.get("/nope00", follow_redirects=False)

    assert response.status_code == 404
    assert "detail" in response.json()
