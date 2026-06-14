from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

initial_activities = deepcopy(activities)
client = TestClient(app)


def reset_activities() -> None:
    activities.clear()
    activities.update(deepcopy(initial_activities))


@pytest.fixture(autouse=True)
def restore_activities() -> None:
    reset_activities()
    yield
    reset_activities()


def test_root_redirect() -> None:
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities() -> None:
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_success() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_already_signed_up() -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "alex@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    first_response = client.post(url, params={"email": email})
    second_response = client.post(url, params={"email": email})

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_not_found() -> None:
    # Arrange
    url = "/activities/Nonexistent/signup"
    email = "user@mergington.edu"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success() -> None:
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found() -> None:
    # Arrange
    activity_name = "Programming Class"
    email = "missing@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
