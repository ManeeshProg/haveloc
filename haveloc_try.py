from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


def clear_installpopup(driver, wait):
    """Check for Material-UI popup and dismiss it if present."""
    try:
        print("Checking for install popup...")
        popup_elements = driver.find_elements(
            By.CSS_SELECTOR,
            '.MuiPaper-root.MuiDialog-paper.MuiDialog-paperScrollPaper.MuiDialog-paperWidthSm.MuiPaper-elevation24.MuiPaper-rounded'
        )
        if popup_elements:
            print("Install popup found, dismissing...")
            dismiss_button = driver.find_element(
                By.CSS_SELECTOR,
                '.MuiDialog-paper .MuiButtonBase-root.MuiButton-root.MuiButton-text'
            )
            dismiss_button.click()
            print("Install popup dismissed successfully")
            return True
        else:
            print("No install popup found")
            return False
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error handling popup: {e}")
        return False


def wait_for_login_button_green(driver, max_seconds=300, poll=0.5):
    """
    Poll until the login button has 'green_btn' class and is enabled/visible.
    Returns True if condition met within max_seconds, else False.
    """
    print("Waiting for login button to be active/green...")
    end = time.time() + max_seconds
    while time.time() < end:
        try:
            btn = driver.find_element(By.CLASS_NAME, 'green_btn false')
            if btn.is_displayed() and btn.is_enabled():
                return True
        except Exception:
            pass
        time.sleep(poll)
    print("Timeout exceeded waiting for the login button to be active.")
    return False


def human_intervention_if_image_challenge(driver, wait, max_minutes=10):
    """
    After checking the checkbox, detect if the image-select challenge appears.
    If present, keep checking if login button is green and print human intervention message.
    Returns True if captcha present, False if not.
    """
    # The image challenge is rendered in a different iframe whose src contains 'recaptcha/api2/bframe'
    driver.switch_to.default_content()
    print("Checking for image challenge iframe...")
    try:
        # Short wait to see if the bframe (challenge) appears
        challenge_iframe = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")
            )
        )
        # If we get here, the challenge iframe is present
        print("Image challenge detected!")
        # Switch into the challenge iframe and verify rc-imageselect exists
        driver.switch_to.frame(challenge_iframe)
        try:
            _ = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "rc-imageselect"))
            )
        except TimeoutException:
            # Even if id isn't immediately visible, still assume challenge is present
            pass

        # Now monitor login button and wait for it to turn green
        driver.switch_to.default_content()
        end_time = time.time() + 60 * max_minutes
        while time.time() < end_time:
            # Check if challenge iframe disappeared (human solved it)
            if not driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']"):
                print("Human solved the image challenge.")
                return True

            # Check if login button has green_btn class
            try:
                driver.find_element(By.CLASS_NAME, 'green_btn false')
                print("Human intervention needed - Login button is green!")
            except Exception:
                print("Human intervention needed - green_btn false")

            time.sleep(2)

        print("Timed out waiting for human to solve image challenge.")
        return True

    except TimeoutException:
        # No challenge iframe; likely passed with checkbox only
        print("No image challenge shown. Proceeding automatically.")
        return False


def handle_captcha(driver, wait):
    """
    Click the reCAPTCHA checkbox in its anchor iframe.
    If an image challenge appears, monitor and wait for human intervention.
    If no image challenge, proceed to click login automatically.
    """
    try:
        print("Looking for reCAPTCHA anchor iframe...")
        wait.until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[contains(@src, 'recaptcha/api2/anchor')]")
            )
        )
        print("Attempting to click reCAPTCHA checkbox...")
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
        checkbox.click()
        print("Clicked reCAPTCHA checkbox")
    except Exception as e:
        print(f"Could not click checkbox automatically: {e}")
    finally:
        # Always return to main DOM
        driver.switch_to.default_content()

    # Check if an image challenge appears
    image_captcha_present = human_intervention_if_image_challenge(driver, wait)

    if image_captcha_present:
        # Image captcha was present and (hopefully) solved by human
        # Wait for login button to be green before proceeding
        wait_for_login_button_green(driver)
    else:
        # No image captcha - just wait briefly for button to be ready
        print("No image captcha. Waiting for login button to be ready...")
        wait_for_login_button_green(driver, max_seconds=10)

    return True


def main():
    driver = None
    try:
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 15)
        driver.get('https://app.haveloc.com/login')
        assert 'haveloc' in driver.title.lower()
        print("Page loaded")

        time.sleep(2)
        clear_installpopup(driver, wait)

        # Fill login credentials
        driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').send_keys('312322202061')
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys('Maneesh12574')

        # Handle CAPTCHA end-to-end
        handle_captcha(driver, wait)

        print("Clicking login button...")
        login_button = driver.find_element(By.CSS_SELECTOR, 'button.green_btn')
        login_button.click()

        time.sleep(5)
        clear_installpopup(driver, wait)
        print("Login process completed")

        input("Press Enter to close browser...")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
