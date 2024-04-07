from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch('main.get_db')
def test_create_workflow(mock_get_db):
    # Mock the database connection
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Send a POST request to the /workflows endpoint with a new workflow
    response = client.post("/workflows", json={"id": 4, "name": "test_workflow"})

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the name of the workflow in the response is the same as the one we sent
    assert response.json()["name"] == "test_workflow"

@patch('main.get_db')
def test_get_workflow(mock_get_db):
    # Mock the database connection
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Mock the return value of the fetchone method to return a specific workflow
    mock_db.execute.return_value.fetchone.return_value = {"id": 4, "name": "test_workflow"}

    # Send a GET request to the /workflows/4 endpoint to get the details of the workflow
    response = client.get("/workflows/4")

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response contains the word "Workflow"
    assert "Workflow" in response.json()

@patch('main.get_db')
def test_update_workflow(mock_get_db):
    # Mock the database connection
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Send a PUT request to the /workflows/1 endpoint to update the workflow
    response = client.put("/workflows/1", json={"name": "WorkFlow1"})

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the name of the workflow in the response is the same as the one we sent
    assert response.json()["name"] == "WorkFlow1"

@patch('main.get_db')
def test_start_workflow(mock_get_db):
    # Mock the database connection
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Send a POST request to the /workflows/1/start endpoint to start the workflow
    response = client.post("/workflows/1/start")

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response is a list (as workflows can have multiple steps)
    assert isinstance(response.json(), list)

@patch('main.get_db')
def test_delete_workflow(mock_get_db):
    # Mock the database connection
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    # Send a DELETE request to the /workflows/4 endpoint to delete the workflow
    response = client.delete("/workflows/4")

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert that the response contains a success message
    assert response.json() == {"message": "Workflow deleted successfully"}





