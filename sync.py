import logging
import os

from google_calendar_manager import GoogleCalendarManager
from gakko_scraper import GakkoHomeworkScraper


def main():
    logging.info("Starting Gakko → Google Calendar sync...")

    try:
        scraper = GakkoHomeworkScraper(
            username=os.environ.get("GAKKO_USERNAME", ""),
            password=os.environ.get("GAKKO_PASSWORD", ""),
        )
        events = scraper.get_homework()

        if not events:
            logging.info("❌ No events found.")
            return

        manager = GoogleCalendarManager()
        manager.post_events(events)
        logging.info("Sync complete!")

    except Exception as e:
        logging.error(f"Error during sync: {e}")

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/sync.log"),
            logging.StreamHandler()
        ]
    )

    main()
