import json
from app import create_app, db


def test_root_endpoint():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

        resp = client.get('/')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert 'message' in data
        assert 'available_endpoints' in data
        assert '/api/register' in data['available_endpoints']

        with app.app_context():
            db.drop_all()
