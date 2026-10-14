"""
Tests for trip management endpoints.
"""
from datetime import date, timedelta

import pytest
from fastapi import status
from pydantic import ValidationError

from .. import schemas


def test_create_trip(client, auth_headers):
    """Test creating a new trip."""
    tomorrow = date.today() + timedelta(days=1)
    next_week = date.today() + timedelta(days=7)

    response = client.post(
        "/api/v1/trips/",
        headers=auth_headers,
        json={
            "name": "Tokyo Adventure",
            "start_date": tomorrow.isoformat(),
            "end_date": next_week.isoformat(),
            "final_destination": "Tokyo, Japan"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Tokyo Adventure"
    assert data["start_date"] == tomorrow.isoformat()
    assert data["end_date"] == next_week.isoformat()
    assert data["final_destination"] == "Tokyo, Japan"
    assert "id" in data

def test_create_trip_unauthorized(client):
    """Test creating trip without auth fails."""
    response = client.post(
        "/api/v1/trips/",
        json={"name": "Test Trip"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_trip_rejects_overlong_destination(client, auth_headers):
    response = client.post(
        "/api/v1/trips/",
        headers=auth_headers,
        json={"name": "Test Trip", "final_destination": "x" * 256},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["loc"] == ["body", "final_destination"]


@pytest.mark.parametrize("trip_schema", [schemas.TripCreate, schemas.TripUpdate])
def test_destination_schema_matches_database_limit(trip_schema):
    assert trip_schema(name="Test Trip", final_destination="x" * 255).final_destination == "x" * 255
    with pytest.raises(ValidationError, match="at most 255 characters"):
        trip_schema(name="Test Trip", final_destination="x" * 256)

def test_get_trip(client, auth_headers):
    """Test retrieving a trip."""
    tomorrow = date.today() + timedelta(days=1)
    next_week = date.today() + timedelta(days=7)

    create_response = client.post(
        "/api/v1/trips/",
        headers=auth_headers,
        json={
            "name": "Test Trip",
            "start_date": tomorrow.isoformat(),
            "end_date": next_week.isoformat()
        }
    )
    trip_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/trips/{trip_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Trip"
    assert "participants" in data
    assert "itinerary_days" in data
