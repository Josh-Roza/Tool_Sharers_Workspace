from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from Tool_Sharers_App.models import User, Listing, Category
import time

class TwoBrowserTransactionTest(StaticLiveServerTestCase):

    
    
    def setUp(self):
            # 1. Create your database users (Make sure these are the ONLY user creations)
            self.lender = User.objects.create_user(
                username='lender1', 
                email='lender@test.com', 
                password='testpassword'
            )
            self.borrower = User.objects.create_user(
                username='borrower1', 
                email='borrower@test.com', 
                password='testpassword'
            )
            
            # ... (Create your listing and category here) ...

            # 2. Spin up TWO completely isolated browsers
            self.borrower_browser = webdriver.Chrome() 
            self.lender_browser = webdriver.Chrome()   


            
            # Position them side-by-side on your screen for the presentation
            self.borrower_browser.set_window_rect(x=0, y=0, width=800, height=800)
            self.lender_browser.set_window_rect(x=800, y=0, width=800, height=800)

    def tearDown(self):
        # Close both when the test finishes
        time.sleep(1000)
        self.borrower_browser.quit()
        self.lender_browser.quit()

    def test_live_booking_interaction(self):
        # --- BORROWER ACTION ---
        self.borrower_browser.get(f"{self.live_server_url}/login/")
        self.borrower_browser.find_element(By.NAME, "username").send_keys("borrower1")
        self.borrower_browser.find_element(By.NAME, "password").send_keys("testpassword")
        self.borrower_browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # (Borrower clicks 'Book Tool')

        # --- LENDER ACTION ---
        # The Lender logs in on their separate browser window at the same time
        self.lender_browser.get(f"{self.live_server_url}/login/")
        self.lender_browser.find_element(By.NAME, "username").send_keys("lender1")
        self.lender_browser.find_element(By.NAME, "password").send_keys("testpassword")
        self.lender_browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # (Lender approves the request)
        
        # --- VERIFICATION ---
        # Switch back to the borrower browser and refresh to see the update
        self.borrower_browser.refresh()
        # Assert the status changed on the borrower's screen