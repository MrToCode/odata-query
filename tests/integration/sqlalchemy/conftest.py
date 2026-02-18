import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def db_session(db_engine):
    session = sessionmaker(db_engine)
    return session
