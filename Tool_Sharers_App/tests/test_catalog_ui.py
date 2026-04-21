from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from django.urls import reverse
from Tool_Sharers_App.models import User, Listing, Category
import time

class CatalogSeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        # 1. Database Setup (Same as before)
        self.owner = User.objects.create_user(username='owner1', email='owner@test.com', password='testpassword123')
        self.category, _ = Category.objects.get_or_create(name='Power Tools')
        self.listing = Listing.objects.create(
            user=self.owner, title='DeWalt Drill', description='Works great.',
            price=15.00, location='Omaha', category=self.category
        )

        # 2. Selenium Setup
        self.browser = webdriver.Firefox() 
        self.browser.implicitly_wait(10) # Tell the browser to wait for pages to load

    def tearDown(self):
        self.browser.quit()

    # --- 1. User can create an account ---
    def test_user_can_create_account(self):
        self.browser.get(f"{self.live_server_url}{reverse('add_user')}")
        
        self.browser.find_element(By.NAME, "username").send_keys("newguy")
        self.browser.find_element(By.NAME, "email").send_keys("new@test.com")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.NAME, "phone_number").send_keys("5551234567")
        
        # Click the required liability waiver checkbox!
        self.browser.find_element(By.NAME, "accept_waiver").click()
        
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify the database updated
        self.assertEqual(User.objects.count(), 2)

    # --- 2. User can log in with valid credentials ---
    def test_user_can_log_in_valid_credentials(self):
        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        
        self.browser.find_element(By.NAME, "username").send_keys("owner1")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(5)
        # Check if the URL changed to the homepage after logging in
        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/")

    # --- 3. Invalid login is rejected ---
    def test_invalid_login_rejected(self):
        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        
        self.browser.find_element(By.NAME, "username").send_keys("owner1")
        self.browser.find_element(By.NAME, "password").send_keys("WRONGPASSWORD")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Verify we are still stuck on the login page
        self.assertIn("login", self.browser.current_url)

   # --- 4. User can create a listing ---
    def test_user_can_create_listing(self):
        # 1. Log in
        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        self.browser.find_element(By.NAME, "username").send_keys("owner1")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # STOP THE RACE CONDITION: Let the browser actually finish logging in!
        import time
        time.sleep(2) 
        
        # 2. Navigate to create listing
        self.browser.get(f"{self.live_server_url}{reverse('create_listing')}")
        
        # LET THE DOM SETTLE: Prevent the Stale Element Exception
        time.sleep(1)
        
        # 3. Fill text fields
        self.browser.find_element(By.NAME, "title").send_keys("Hammer")
        self.browser.find_element(By.NAME, "description").send_keys("Standard hammer")
        self.browser.find_element(By.NAME, "price").send_keys("5.00")
        self.browser.find_element(By.NAME, "location").send_keys("Omaha")
        
        # 4. Handle Dropdowns
        condition_dropdown = Select(self.browser.find_element(By.NAME, "condition"))
        condition_dropdown.select_by_visible_text("Good")
        
        category_dropdown = Select(self.browser.find_element(By.NAME, "category"))
        category_dropdown.select_by_visible_text("Power Tools") 
        
        # 5. Submit the form directly (DO NOT CLICK THE BUTTON)
        self.browser.find_element(By.NAME, "title").submit()
        

        time.sleep(2)
        
        # Verify it saved
        self.assertEqual(Listing.objects.count(), 2)