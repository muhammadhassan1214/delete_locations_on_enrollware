from selenium.webdriver.common.by import By
from Utils.utils import (
    safe_navigate_to_url,
    check_element_exists,
    input_element,
    click_element_by_js,
    select_by_text
)
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables and validate
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validate required environment variables
REQUIRED_ENV_VARS = ["ENROLLWARE_USERNAME", "ENROLLWARE_PASSWORD"]


def validate_environment_variables() -> bool:
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    return True


def login_to_enrollware_and_navigate_to_settings_locations(driver, max_retries: int = 3) -> bool:
    if not validate_environment_variables():
        return False

    for attempt in range(max_retries):
        try:
            if not safe_navigate_to_url(driver, "https://enrollware.com/admin"):
                continue

            # Check if already logged in
            validation_button = check_element_exists(driver, (By.ID, "loginButton"), timeout=5)

            if validation_button:
                # Input credentials with validation
                if not input_element(driver, (By.ID, "username"), os.getenv("ENROLLWARE_USERNAME")):
                    logger.error("Failed to input username")
                    continue

                if not input_element(driver, (By.ID, "password"), os.getenv("ENROLLWARE_PASSWORD")):
                    logger.error("Failed to input password")
                    continue

                # Optional remember me checkbox
                click_element_by_js(driver, (By.ID, "rememberMe"))

                if not click_element_by_js(driver, (By.ID, "loginButton")):
                    logger.error("Failed to click login button")
                    continue

                # Wait for login to complete
                time.sleep(20)

                # Verify login success
                if "admin" in driver.current_url.lower():
                    logger.info("Successfully logged into Enrollware")
                else:
                    logger.warning("Login may have failed, checking current URL")
                    continue

            return navigate_to_settings_locations(driver)

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue

    logger.error("Failed to login to Enrollware after all attempts")
    return False


def navigate_to_settings_locations(driver, max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
        try:
            url = "https://www.enrollware.com/admin/ts-location-list.aspx"
            if safe_navigate_to_url(driver, url):
                logger.info("Successfully navigated to Settings -> Locations")
                # apply all filters
                select_by_text(driver, (By.XPATH, "//div[@class='dataTables_length']//select"), 'All')
                return True
        except Exception as e:
            logger.error(f"Navigation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

    logger.error("Failed to navigate to Settings -> Locations after all attempts")
    return False
