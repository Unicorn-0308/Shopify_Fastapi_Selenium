from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import tempfile

class ShopifyLogin:
    def __init__(self, headless=False):
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1080,760")
        
        # Create a unique user data directory to avoid conflicts
        self.user_data_dir = tempfile.mkdtemp(prefix="chrome_user_data_")
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # Initialize driver
        # driver_path = ChromeDriverManager().install()
        try:
            # self.driver = webdriver.Chrome(service=driver_path, options=chrome_options)
            self.driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException as e:
            print("Error to install WebDriver\n", str(e))
            # parent_dir = os.path.dirname(driver_path)
            # exe_path = os.path.join(parent_dir, 'chromedriver.exe')
            # service = Service(exe_path)
            # self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 180)
    
    def login(self, store_url, email, password):
        """
        Login to Shopify store
        """
        try:
            # Navigate to login page
            login_url = f"{store_url}/account/login"
            print(f"Navigating to: {login_url}")
            self.driver.get(login_url)

            print("\n=== Attempting Login ===")
            
            # Strategy 1: Try targeting specific Shopify login fields by ID
            try:
                print("Trying strategy: Targeting specific Shopify fields by ID")

                self.driver.switch_to.frame("advancedRegForm")
                self.driver.execute_script("""
                    var emailField = document.querySelectorAll('input[name="email"]')[0];
                    console.log(emailField);
                    emailField.value = arguments[0];
                    emailField.dispatchEvent(new Event('input', { bubbles: true }));
                    emailField.dispatchEvent(new Event('change', { bubbles: true }));
                    var passField = document.querySelectorAll('input[name="password"]')[0];
                    console.log(passField);
                    passField.value = arguments[1];
                    passField.dispatchEvent(new Event('input', { bubbles: true }));
                    passField.dispatchEvent(new Event('change', { bubbles: true }));
                    document.querySelectorAll('button[style="width: 100%; margin-top: 1em; background-color: rgb(31, 69, 194) !important;"]')[0].click();
                """, email, password)

                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart-count-bubble")))
                print("\n=== Login Success ===")
                
            except Exception as e1:
                print(f"Strategy failed: {str(e1)}")

            time.sleep(10)
            try:
                old_element = self.driver.find_element(By.CLASS_NAME, "cart-count-bubble")
                self.wait.until(EC.staleness_of(old_element))
                print("\n=== Reload Starts ===")
            except Exception as e2:
                print(f"\n=== Reload failed ===")

            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart-count-bubble")))
            print("\n=== Reload Success ===")
            
            # Check if login was successful
            current_url = self.driver.current_url
            print(f"Current URL after login attempt: {current_url}")
            
            # Check various success indicators
            success_indicators = [
                "/account" in current_url,
                "/challenge" in current_url,
                "/cart" in current_url and login_url not in current_url,  # Redirected to cart after login
                "/checkout" in current_url,
                "welcome" in self.driver.page_source.lower(),
                "logout" in self.driver.page_source.lower(),  # Logout link appears when logged in
                "sign out" in self.driver.page_source.lower()
            ]
            
            if any(success_indicators):
                print("Login successful!")
                    
                return True
            else:
                print("Login may have failed. Check the browser window.")
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_cookies(self):
        """
        Get all cookies from the current session
        """
        try:
            cookies = self.driver.get_cookies()
            return cookies
        except Exception as e:
            print(f"Error getting cookies: {str(e)}")
            return []
    
    def save_cookies_to_file(self, filename="shopify_cookies.json"):
        """
        Save cookies to a JSON file
        """
        cookies = self.get_cookies()
        try:
            with open(filename, 'w') as f:
                json.dump(cookies, f, indent=4)
            print(f"Cookies saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving cookies: {str(e)}")
            return False
    
    def load_cookies_from_file(self, filename="shopify_cookies.json"):
        """
        Load cookies from a JSON file
        """
        try:
            with open(filename, 'r') as f:
                cookies = json.load(f)
            
            # Add cookies to current session
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            print(f"Cookies loaded from {filename}")
            return True
        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            return False
    
    def print_cookies(self):
        """
        Print all cookies in a readable format
        """
        cookies = self.get_cookies()
        print("\n=== COOKIES ===")
        for cookie in cookies:
            print(f"Name: {cookie['name']}")
            print(f"Value: {cookie['value']}")
            print(f"Domain: {cookie['domain']}")
            print(f"Path: {cookie['path']}")
            print(f"Secure: {cookie['secure']}")
            print("-" * 50)
    
    def close(self):
        """
        Close the browser and cleanup temporary user data directory
        """
        self.driver.quit()
        # Cleanup temporary user data directory
        try:
            import shutil
            if hasattr(self, 'user_data_dir') and os.path.exists(self.user_data_dir):
                shutil.rmtree(self.user_data_dir)
                print(f"Cleaned up temporary directory: {self.user_data_dir}")
        except Exception as e:
            print(f"Warning: Could not cleanup temporary directory: {e}")

# Usage example
if __name__ == "__main__":
    # Initialize the login class
    shopify = ShopifyLogin(headless=True)  # Set to True for headless mode
    
    # Store credentials
    STORE_URL = "https://www.uhs-hardware.com"  # Replace with actual store URL
    EMAIL = "ja@autokey.ca"  # Replace with your email
    PASSWORD = "MfeC3ScnMMxLR:!"  # Replace with your password
    
    try:
        # Login to the store
        if shopify.login(STORE_URL, EMAIL, PASSWORD):
            # Get and print cookies
            shopify.print_cookies()
            
            # Save cookies to file
            shopify.save_cookies_to_file("my_shopify_cookies.json")
            
            print(f"Current URL: {shopify.driver.current_url}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close browser
        time.sleep(5)  # Keep browser open for 5 seconds to see results
        shopify.close()
