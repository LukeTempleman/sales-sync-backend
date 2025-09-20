from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Import all models here to ensure they're registered with SQLAlchemy
from .tenant import Tenant
from .user import User
from .role import Role, UserRole
from .brand import Brand, BrandInfographic
from .survey import Survey, SurveyQuestion
from .visit import Visit, VisitAnswer
from .photo import Photo, ShelfQuadrant
from .goal import Goal, GoalAssignment
from .call_cycle import CallCycle, CallCycleLocation
from .team import Team, UserTeam
from .audit import AuditLog


def init_db(app):
    """Initialize the database."""
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)


def seed_roles(session):
    """Seed the roles table with default roles."""
    from .role import Role
    
    # Define default roles
    default_roles = [
        'agent',
        'team_leader',
        'area_manager',
        'regional_manager',
        'national_manager',
        'admin',
        'super_admin'
    ]
    
    # Add roles if they don't exist
    for role_name in default_roles:
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            session.add(role)
    
    session.commit()