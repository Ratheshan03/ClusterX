"""
Simple API Tests for UniGuide AI
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


def test_get_universities():
    """Test getting all universities"""
    response = client.get("/universities")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data


def test_get_courses():
    """Test getting all courses"""
    response = client.get("/courses")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data
    assert "limit" in data
    assert "offset" in data


def test_filter_courses_by_university():
    """Test filtering courses by university"""
    response = client.get("/courses?university=oxford")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_filter_courses_by_subject():
    """Test filtering courses by subject"""
    response = client.get("/courses?subject=computer")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_pagination():
    """Test pagination parameters"""
    response = client.get("/courses?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_invalid_limit():
    """Test invalid limit parameter"""
    response = client.get("/courses?limit=200")
    assert response.status_code == 422  # Validation error
