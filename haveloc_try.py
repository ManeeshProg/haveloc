from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def clear_installpopup(driver, wait):
    """
    Check for Material-UI popup and dismiss it if present
    """
    try:
        print("Checking for install popup...")
        # Use CSS selector for multiple classes, not CLASS_NAME
        popup_elements = driver.find_elements(
            By.CSS_SELECTOR, 
            '.MuiPaper-root.MuiDialog-paper.MuiDialog-paperScrollPaper.MuiDialog-paperWidthSm.MuiPaper-elevation24.MuiPaper-rounded'
        )
        
        if popup_elements:
            print("Install popup found, dismissing...")
            # Click the dismiss button
            dismiss_button = driver.find_element(
                By.CSS_SELECTOR, 
                '.MuiButtonBase-root.MuiButton-root.MuiButton-text'
            )
            dismiss_button.click()
            print("Install popup dismissed successfully")
            return True
        else:
            print("No install popup found")
            return False
        captcha=
            
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error handling popup: {e}")
        return False

try:
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)  # Define wait variable
    
    driver.get('https://app.haveloc.com/login')
    
    assert 'haveloc' in driver.title
    print("Page loaded successfully")
    time.sleep(5)
    # Check for install popup after page loads
    clear_installpopup(driver, wait)
    
    # Fill login credentials
    driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').send_keys('312322202061')
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys('Maneesh12574')
    
    try:
        # Wait for reCAPTCHA iframe to be present and switch to it
        print("Looking for reCAPTCHA iframe...")
        recaptcha_frame = wait.until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[contains(@src, 'recaptcha/api2/anchor')]")
            )
        )
        
        # Click the checkbox using the ID from your HTML structure
        print("Attempting to click reCAPTCHA checkbox...")
        checkbox = wait.until(
            EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
        )
        checkbox.click()
        print("Clicked reCAPTCHA checkbox")
        
        # Switch back to main content
        driver.switch_to.default_content()
        
        # Wait for verification (may trigger image challenges)
        time.sleep(5)
        
    except Exception as e:
        print(f"Automated reCAPTCHA handling failed: {e}")
        # Switch back to main content if iframe switching failed
        driver.switch_to.default_content()
        
        print("\n=== MANUAL CAPTCHA SOLVING REQUIRED ===")
        print("Please solve the CAPTCHA manually in the browser window")
        print("After solving, press Enter to continue...")
        input("Press Enter after completing CAPTCHA: ")
    
    # Click login button
    print("Clicking login button...")
    login_button = driver.find_element(By.CLASS_NAME, 'green_btn')
    login_button.click()
    
    # Wait to see the result and check for popup again after login
    time.sleep(5)
    
    # Check for popup after login attempt
    clear_installpopup(driver, wait)
    
    print("Login process completed")
    
    # Keep browser open to observe results
    input("Press Enter to close browser...")
    
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    driver.quit()
