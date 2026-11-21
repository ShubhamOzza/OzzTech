import functools
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Parent of every model class; it collects their tables."""


@functools.cache
def get_engine():
    """The one place that knows where the app's database is."""
    load_dotenv()
    url = URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )
    return create_engine(url)


def create_tables():
    Base.metadata.create_all(get_engine())


def transaction():
    """One unit of work: commit if the block finishes, roll back if it raises."""
    Session = sessionmaker(get_engine(), expire_on_commit=False)
    return Session.begin()
