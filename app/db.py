from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from app.core import config as app_config


def _alembic_get_current_rev(config, script):
    """
    Works sorta like alembic.command.current

    :param config: alembic Config
    :return: current revision
    :rtype: str
    """
    config._curr_rev = None

    def display_version(rev, _):
        for rev in script.get_all_current(rev):
            config._curr_rev = rev.cmd_format(False)
        return []

    with EnvironmentContext(config, script, fn=display_version):
        script.run_env()
    if config._curr_rev is not None and " " in config._curr_rev:
        config._curr_rev = config._curr_rev.strip().split(" ")[0]
    return config._curr_rev


def init_db():
    """
    Check for the revision and apply the
    migrations accordingly
    """
    print("Initializing DB")
    print("Checking for database migrations")

    alembic_config = Config("alembic.ini")
    alembic_config.attributes["configure_logger"] = False

    script = ScriptDirectory.from_config(alembic_config)
    curr_rev = _alembic_get_current_rev(alembic_config, script)
    head_rev = script.get_revision("head").revision

    print(f"Head Rev: {head_rev}, Current Rev: {curr_rev}")
    if curr_rev != head_rev or curr_rev is None:
        print(
            f"Alembic head is {head_rev} but this DB is at {curr_rev}; running migrations"
        )
        command.upgrade(alembic_config, "head")
        print("Migrations complete")
    else:
        print("No migrations are required")
    print("Done initializing DB")


async_engine = create_async_engine(app_config.settings.DATABASE_URI, pool_pre_ping=True)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def listen_to_notifications():
    async with async_engine.begin() as conn:
        await conn.run_sync(listen_to_notifications)
