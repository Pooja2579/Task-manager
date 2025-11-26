import pytest
import json
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_user(client):
    response = client.post('/api/register', 
                         json={
                             'username': 'testuser',
                             'email': 'test@example.com',
                             'password': 'testpass123'
                         })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User created successfully'
    assert data['user']['username'] == 'testuser'

def test_register_duplicate_username(client):
    # Create first user
    client.post('/api/register', 
               json={
                   'username': 'testuser',
                   'email': 'test1@example.com',
                   'password': 'testpass123'
               })
    
    # Try to create user with same username
    response = client.post('/api/register', 
                         json={
                             'username': 'testuser',
                             'email': 'test2@example.com',
                             'password': 'testpass123'
                         })
    assert response.status_code == 400

def test_login_success(client):
    # Register user
    client.post('/api/register', 
               json={
                   'username': 'testuser',
                   'email': 'test@example.com',
                   'password': 'testpass123'
               })
    
    # Login
    response = client.post('/api/login', 
                         json={
                             'username': 'testuser',
                             'password': 'testpass123'
                         })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_login_invalid_credentials(client):
    response = client.post('/api/login', 
                         json={
                             'username': 'nonexistent',
                             'password': 'wrongpass'
                         })
    assert response.status_code == 401