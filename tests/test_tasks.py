import pytest
import json
from app import create_app, db
from app.models import User, Task

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

@pytest.fixture
def auth_token(client):
    # Register and login user
    client.post('/api/register', 
               json={
                   'username': 'testuser',
                   'email': 'test@example.com',
                   'password': 'testpass123'
               })
    
    response = client.post('/api/login', 
                         json={
                             'username': 'testuser',
                             'password': 'testpass123'
                         })
    data = json.loads(response.data)
    return data['access_token']

def test_create_task(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/tasks', 
                         json={
                             'title': 'Test Task',
                             'description': 'Test Description'
                         },
                         headers=headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Task created successfully'
    assert data['task']['title'] == 'Test Task'

def test_get_tasks(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Create a task first
    client.post('/api/tasks', 
               json={'title': 'Test Task'},
               headers=headers)
    
    response = client.get('/api/tasks', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['tasks']) == 1
    assert data['tasks'][0]['title'] == 'Test Task'

def test_update_task(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Create a task
    response = client.post('/api/tasks', 
                         json={'title': 'Test Task'},
                         headers=headers)
    task_id = json.loads(response.data)['task']['id']
    
    # Update the task
    response = client.put(f'/api/tasks/{task_id}', 
                        json={'title': 'Updated Task', 'completed': True},
                        headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['task']['title'] == 'Updated Task'
    assert data['task']['completed'] == True

def test_delete_task(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    
    # Create a task
    response = client.post('/api/tasks', 
                         json={'title': 'Test Task'},
                         headers=headers)
    task_id = json.loads(response.data)['task']['id']
    
    # Delete the task
    response = client.delete(f'/api/tasks/{task_id}', headers=headers)
    assert response.status_code == 200
    
    # Verify task is deleted
    response = client.get(f'/api/tasks/{task_id}', headers=headers)
    assert response.status_code == 404