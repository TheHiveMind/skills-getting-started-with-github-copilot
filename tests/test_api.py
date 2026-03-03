import urllib.parse

import src.app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange
    path = "/"

    # Act
    response = client.get(path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    encoded_activity = urllib.parse.quote(activity_name, safe="")
    path = f"/activities/{encoded_activity}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]
    encoded_activity = urllib.parse.quote(activity_name, safe="")
    path = f"/activities/{encoded_activity}/signup"

    # Act
    response = client.post(path, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    path = "/activities/Unknown%20Club/signup"

    # Act
    response = client.post(path, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email_query_param(client):
    # Arrange
    path = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = app_module.activities[activity_name]["participants"][0]
    encoded_activity = urllib.parse.quote(activity_name, safe="")
    path = f"/activities/{encoded_activity}/unregister"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    path = "/activities/Unknown%20Club/unregister"

    # Act
    response = client.delete(path, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_non_member(client):
    # Arrange
    path = "/activities/Chess%20Club/unregister"

    # Act
    response = client.delete(path, params={"email": "not.registered@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_requires_email_query_param(client):
    # Arrange
    path = "/activities/Chess%20Club/unregister"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 422
