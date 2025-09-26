import time
import logging
from selenium.webdriver.common.by import By
from Utils.utils import (
    get_undetected_driver,
    safe_navigate_to_url,
    check_element_exists,
    get_element_attribute, click_element_by_js,
)

from Utils.functions import login_to_enrollware_and_navigate_to_settings_locations

logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)

class ArchiveLocations:
    def __init__(self):
        self.driver = None

    def initialize(self) -> bool:
        try:
            self.driver = get_undetected_driver()
            if self.driver:
                logger.info("Chrome driver initialized successfully")
                return True
            else:
                logger.error("Failed to initialize Chrome driver")
                return False
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Resources cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

def main():
    processor = ArchiveLocations()
    try:
        if not processor.initialize():
            return

        if not login_to_enrollware_and_navigate_to_settings_locations(processor.driver):
            return

        time.sleep(3)  # Wait for the page to load

        # Find all location rows
        location_rows = []
        location_rows_el = processor.driver.find_elements(By.CSS_SELECTOR, "td > a")
        logger.info(f"Found {len(location_rows_el)} locations")

        for row in location_rows_el:
            url = row.get_attribute("href")
            location_rows.append(url)

        try:
            for location_url in location_rows:
                if not safe_navigate_to_url(processor.driver, location_url):
                    continue

                location_name = get_element_attribute(
                    processor.driver, (By.ID, "mainContent_name"), "value"
                )

                logger.info(f"Processing location: {location_name}")
                # Check if the location is already archived
                archive_button = check_element_exists(processor.driver, (By.ID, "mainContent_isDeleted"), timeout=5)
                if not archive_button:
                    logger.info(f"Location '{location_name}' is already archived or cannot be archived.")
                    continue

                click_element_by_js(processor.driver, (By.ID, "mainContent_isDeleted"))
                click_element_by_js(processor.driver, (By.ID, "mainContent_submitButton"))
                logger.info(f"Archived -> {location_name}")

        except Exception as e:
            logger.error(f"Failed to archive location due to {e}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()
