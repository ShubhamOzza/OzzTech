import logging

from portfolio_tracker import cli, database

# Imported so create_tables() knows every table, even though main.py never uses them by name.
from portfolio_tracker.models import account, asset, portfolio, transaction  # noqa: F401

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename="tracker.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Tracker started")
    try:
        database.create_tables()
    except Exception:
        logger.exception("Could not connect to the database at startup")
        print(
            "Could not connect to the database. "
            "Please check that MySQL is running and your .env settings are correct."
        )
        return

    try:
        cli.run()
    except Exception:
        logger.exception("Unexpected error; tracker stopped")
        print("Something unexpected went wrong. Details were written to tracker.log.")


if __name__ == "__main__":
    main()
