import logging

from portfolio_tracker import cli

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        filename="tracker.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Tracker started")
    try:
        cli.run()
    except Exception:
        logger.exception("Unexpected error; tracker stopped")
        print("Something unexpected went wrong. Details were written to tracker.log.")


if __name__ == "__main__":
    main()
