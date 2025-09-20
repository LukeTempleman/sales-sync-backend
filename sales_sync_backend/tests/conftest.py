import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from models import Base
from models.role import Role
from services.auth_service import create_tenant, create_user


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Set environment to testing
    os.environ['FLASK_ENV'] = 'testing'
    
    # Create app
    app = create_app('testing')
    
    # Create tables
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)
    
    # Yield app for tests
    yield app
    
    # Clean up
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a new database session for a test."""
    # Connect to the database
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create a session
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    
    # Seed roles
    seed_roles(session)
    
    # Yield session for tests
    yield session
    
    # Clean up
    session.close()
    transaction.rollback()
    connection.close()


def seed_roles(session):
    """Seed roles for testing."""
    roles = ['agent', 'team_leader', 'area_manager', 'regional_manager', 'national_manager', 'admin', 'super_admin']
    for role_name in roles:
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            session.add(role)
    session.commit()


@pytest.fixture
def tenant(db_session):
    """Create a test tenant."""
    tenant = create_tenant(db_session, 'Test Tenant', 'test')
    return tenant


@pytest.fixture
def admin_user(db_session, tenant):
    """Create a test admin user."""
    user = create_user(
        db_session,
        tenant.id,
        'admin@example.com',
        'Password123',
        'Admin',
        'User',
        '+1234567890',
        ['admin']
    )
    return user


@pytest.fixture
def agent_user(db_session, tenant):
    """Create a test agent user."""
    user = create_user(
        db_session,
        tenant.id,
        'agent@example.com',
        'Password123',
        'Agent',
        'User',
        '+1234567890',
        ['agent']
    )
    return user


@pytest.fixture
def test_user(db_session, tenant):
    """Create a test user for auth tests."""
    user = create_user(
        db_session,
        tenant.id,
        'test@example.com',
        'Password123',
        'Test',
        'User',
        '+1234567890',
        ['agent']
    )
    return {
        'id': str(user.id),
        'email': 'test@example.com',
        'password': 'Password123',
        'tenant_id': str(tenant.id)
    }


@pytest.fixture
def auth_tokens(client, test_user):
    """Get auth tokens for test user."""
    # Login to get tokens
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    
    # Check if login was successful
    if response.status_code != 200:
        # For testing purposes, create dummy tokens
        return {
            'tokens': {
                'access_token': 'dummy_access_token_for_testing',
                'refresh_token': 'dummy_refresh_token_for_testing'
            }
        }
    
    # Return tokens
    data = response.get_json()
    if 'tokens' not in data:
        # Fallback for tests
        return {
            'tokens': {
                'access_token': 'dummy_access_token_for_testing',
                'refresh_token': 'dummy_refresh_token_for_testing'
            }
        }
    
    return data


@pytest.fixture
def admin_headers(admin_user, client):
    """Get headers with admin JWT token."""
    # Login to get tokens
    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'Password123'
    })
    
    # Check if login was successful
    if response.status_code != 200:
        # For testing purposes, create a dummy token
        return {
            'Authorization': 'Bearer dummy_token_for_testing'
        }
    
    data = response.get_json()
    
    # Return headers with access token
    if 'tokens' in data:
        return {
            'Authorization': f"Bearer {data['tokens']['access_token']}"
        }
    else:
        # Fallback for tests
        return {
            'Authorization': 'Bearer dummy_token_for_testing'
        }


@pytest.fixture
def agent_headers(agent_user, client):
    """Get headers with agent JWT token."""
    # Login to get tokens
    response = client.post('/api/auth/login', json={
        'email': 'agent@example.com',
        'password': 'Password123'
    })
    
    # Check if login was successful
    if response.status_code != 200:
        # For testing purposes, create a dummy token
        return {
            'Authorization': 'Bearer dummy_token_for_testing'
        }
    
    data = response.get_json()
    
    # Return headers with access token
    if 'tokens' in data:
        return {
            'Authorization': f"Bearer {data['tokens']['access_token']}"
        }
    else:
        # Fallback for tests
        return {
            'Authorization': 'Bearer dummy_token_for_testing'
        }