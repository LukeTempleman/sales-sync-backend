#!/usr/bin/env python
import os
import uuid
import click
from flask.cli import FlaskGroup

from app import create_app
from models import Base
from models.role import Role
from models.tenant import Tenant
from models.user import User
from models.brand import Brand
from models.survey import Survey
from models.question import Question
from services.auth_service import create_tenant, create_user


app = create_app()
cli = FlaskGroup(create_app=lambda: app)


@cli.command('init-db')
def init_db():
    """Initialize the database."""
    from sqlalchemy import create_engine
    
    # Create engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    
    # Create tables
    Base.metadata.create_all(engine)
    
    click.echo('Initialized the database.')


@cli.command('seed-db')
def seed_db():
    """Seed the database with initial data."""
    # Seed roles
    seed_roles()
    
    click.echo('Database seeded successfully.')


@cli.command('seed-roles')
def seed_roles():
    """Seed roles."""
    # Get session
    session = app.db_session
    
    # Seed roles
    roles = ['agent', 'team_leader', 'area_manager', 'regional_manager', 'national_manager', 'admin', 'super_admin']
    for role_name in roles:
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            session.add(role)
    
    session.commit()
    click.echo('Seeded roles.')


@cli.command('create-superadmin')
@click.option('--email', prompt=True, help='Superadmin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Superadmin password')
@click.option('--first-name', prompt=True, help='Superadmin first name')
@click.option('--last-name', prompt=True, help='Superadmin last name')
def create_superadmin(email, password, first_name, last_name):
    """Create a superadmin user."""
    # Get session
    session = app.db_session
    
    # Create tenant
    tenant = create_tenant(session, 'System', 'system')
    
    # Create superadmin
    user = create_user(
        session,
        tenant.id,
        email,
        password,
        first_name,
        last_name,
        None,
        ['super_admin']
    )
    
    click.echo(f'Created superadmin user: {user.email}')


@cli.command('create-tenant-admin')
@click.option('--tenant-name', prompt=True, help='Tenant name')
@click.option('--subdomain', prompt=True, help='Tenant subdomain')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--first-name', prompt=True, help='Admin first name')
@click.option('--last-name', prompt=True, help='Admin last name')
def create_tenant_admin(tenant_name, subdomain, email, password, first_name, last_name):
    """Create a tenant and admin user."""
    # Get session
    session = app.db_session
    
    # Create tenant
    tenant = create_tenant(session, tenant_name, subdomain)
    
    # Create admin
    user = create_user(
        session,
        tenant.id,
        email,
        password,
        first_name,
        last_name,
        None,
        ['admin']
    )
    
    click.echo(f'Created tenant: {tenant.name} and admin user: {user.email}')


@cli.command('create-agent')
@click.option('--tenant-id', prompt=True, help='Tenant ID')
@click.option('--email', prompt=True, help='Agent email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Agent password')
@click.option('--first-name', prompt=True, help='Agent first name')
@click.option('--last-name', prompt=True, help='Agent last name')
@click.option('--phone', prompt=True, help='Agent phone number')
def create_agent(tenant_id, email, password, first_name, last_name, phone):
    """Create an agent user."""
    # Get session
    session = app.db_session
    
    # Create agent
    user = create_user(
        session,
        tenant_id,
        email,
        password,
        first_name,
        last_name,
        phone,
        ['agent']
    )
    
    click.echo(f'Created agent user: {user.email}')


@cli.command('create-brand')
@click.option('--tenant-id', prompt=True, help='Tenant ID')
@click.option('--name', prompt=True, help='Brand name')
@click.option('--slug', prompt=True, help='Brand slug')
def create_brand(tenant_id, name, slug):
    """Create a brand."""
    # Get session
    session = app.db_session
    
    # Check if brand already exists
    brand = session.query(Brand).filter_by(tenant_id=tenant_id, name=name).first()
    if brand:
        click.echo(f'Brand with name "{name}" already exists for this tenant.')
        return
    
    # Create brand
    brand = Brand(
        tenant_id=tenant_id,
        name=name,
        slug=slug,
        active=True
    )
    session.add(brand)
    session.commit()
    
    click.echo(f'Created brand: {brand.name} with ID: {brand.id}')


@cli.command('create-survey')
@click.option('--tenant-id', prompt=True, help='Tenant ID')
@click.option('--name', prompt=True, help='Survey name')
@click.option('--type', prompt=True, type=click.Choice(['individual', 'shop']), help='Survey type')
@click.option('--brand-id', help='Brand ID (optional)')
@click.option('--created-by', help='User ID who created the survey (optional)')
def create_survey(tenant_id, name, type, brand_id, created_by):
    """Create a survey."""
    # Get session
    session = app.db_session
    
    # Check if survey already exists
    survey = session.query(Survey).filter_by(tenant_id=tenant_id, name=name).first()
    if survey:
        click.echo(f'Survey with name "{name}" already exists for this tenant.')
        return
    
    # Create survey
    survey = Survey(
        tenant_id=tenant_id,
        name=name,
        type=type,
        brand_id=brand_id,
        created_by=created_by,
        active=True
    )
    session.add(survey)
    session.commit()
    
    click.echo(f'Created survey: {survey.name} with ID: {survey.id}')


@cli.command('add-question')
@click.option('--tenant-id', prompt=True, help='Tenant ID')
@click.option('--survey-id', prompt=True, help='Survey ID')
@click.option('--question-text', prompt=True, help='Question text')
@click.option('--input-type', prompt=True, type=click.Choice(['text', 'select', 'boolean', 'photo', 'number']), help='Input type')
@click.option('--order-num', type=int, default=0, help='Order number')
def add_question(tenant_id, survey_id, question_text, input_type, order_num):
    """Add a question to a survey."""
    # Get session
    session = app.db_session
    
    # Create question
    question = Question(
        tenant_id=tenant_id,
        survey_id=survey_id,
        question_text=question_text,
        input_type=input_type,
        order_num=order_num
    )
    session.add(question)
    session.commit()
    
    click.echo(f'Added question to survey with ID: {question.id}')


if __name__ == '__main__':
    cli()