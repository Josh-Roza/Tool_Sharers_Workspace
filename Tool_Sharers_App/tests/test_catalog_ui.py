import time
from datetime import date, timedelta
from selenium.webdriver.support.ui import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.urls import reverse
from Tool_Sharers_App.models import User, Listing, Category, Booking, Message, SupportTicket, Review, Report

class CatalogSeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner1', email='owner@test.com', password='testpassword123')
        
        self.borrower = User.objects.create_user(username='borrower1', email='borrower@test.com', password='testpassword123')
        
        self.category, _ = Category.objects.get_or_create(name='Power Tools')
        self.listing = Listing.objects.create(
            user=self.owner, title='DeWalt Drill', description='Works great.',
            price=15.00, location='Omaha', category=self.category
        )

        self.browser = webdriver.Firefox() 
        self.browser.implicitly_wait(5) 

    def tearDown(self):
        self.browser.quit()

    def login_user(self, username, password):

        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        time.sleep(2)
        self.browser.find_element(By.NAME, "username").send_keys(username)
        self.browser.find_element(By.NAME, "password").send_keys(password)
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)

    # --- 1. User can create an account ---
    def test_user_can_create_account(self):
        self.browser.get(f"{self.live_server_url}{reverse('add_user')}")
        
        self.browser.find_element(By.NAME, "username").send_keys("newguy")
        self.browser.find_element(By.NAME, "email").send_keys("new@test.com")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.NAME, "phone_number").send_keys("5551234567")
        

        self.browser.find_element(By.NAME, "accept_waiver").click()
        
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


        self.assertEqual(User.objects.count(), 3)

    # --- 2. User can log in with valid credentials ---
    def test_user_can_log_in_valid_credentials(self):
        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        
        self.browser.find_element(By.NAME, "username").send_keys("owner1")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(5)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/")

    # --- 3. Invalid login is rejected ---
    def test_invalid_login_rejected(self):
        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        
        self.browser.find_element(By.NAME, "username").send_keys("owner1")
        self.browser.find_element(By.NAME, "password").send_keys("WRONGPASSWORD")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        

        self.assertIn("login", self.browser.current_url)

   # --- 4. User can create a listing ---
    def test_user_can_create_listing(self):

        self.browser.get(f"{self.live_server_url}{reverse('login')}")
        self.browser.find_element(By.NAME, "username").send_keys("owner1")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        import time
        time.sleep(4) 

        self.browser.get(f"{self.live_server_url}{reverse('create_listing')}")
        
        time.sleep(2)
        

        self.browser.find_element(By.NAME, "title").send_keys("Hammer")
        self.browser.find_element(By.NAME, "description").send_keys("Standard hammer")
        self.browser.find_element(By.NAME, "price").send_keys("5.00")
        self.browser.find_element(By.NAME, "location").send_keys("Omaha")
        

        condition_dropdown = Select(self.browser.find_element(By.NAME, "condition"))
        condition_dropdown.select_by_visible_text("Good")
        
        category_dropdown = Select(self.browser.find_element(By.NAME, "category"))
        category_dropdown.select_by_visible_text("Power Tools") 
        
        self.browser.find_element(By.NAME, "title").submit()
        

        time.sleep(2)
        
        self.assertEqual(Listing.objects.count(), 2)

# --- 5. User can edit their own listing ---
    def test_user_can_edit_own_listing(self):
        self.login_user("owner1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('edit_listing', args=[self.listing.listing_id])}")
        time.sleep(2)
        
        title_input = self.browser.find_element(By.NAME, "title")
        title_input.clear() # Clear the old "DeWalt Drill" text
        title_input.send_keys("Updated DeWalt Drill")
        title_input.submit()
        time.sleep(2)
        
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Updated DeWalt Drill")

    # --- 6. User can delete their own listing ---
    def test_user_can_delete_own_listing(self):
        self.login_user("owner1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('delete_listing', args=[self.listing.listing_id])}")
        time.sleep(2)

        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(4)
        self.assertEqual(Listing.objects.count(), 0)

    # --- 7. User CANNOT edit or delete someone else's listing ---
    def test_user_cannot_edit_someone_elses_listing(self):
        self.login_user("borrower1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('edit_listing', args=[self.listing.listing_id])}")
        time.sleep(2)

        self.assertNotIn("Updated DeWalt Drill", self.browser.page_source)
        
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "DeWalt Drill")

    # --- 8. User can search listings by keyword/title ---
    def test_search_listings_by_keyword(self):
   
        self.browser.get(f"{self.live_server_url}{reverse('home')}?q=DeWalt")
        time.sleep(2)
        self.assertIn("DeWalt Drill", self.browser.page_source)

    # --- 9. User can filter listings by Category ---
    def test_filter_listings_by_category(self):
        self.browser.get(f"{self.live_server_url}{reverse('home')}?category={self.category.id}")
        time.sleep(2)
        self.assertIn("DeWalt Drill", self.browser.page_source)

    #--- 10. Borrower can send a message to the owner ---
    def test_borrower_can_send_message(self):
        self.login_user("borrower1", "testpassword123")
        
        # 1. Go to the listing
        self.browser.get(f"{self.live_server_url}{reverse('view_listing', args=[self.listing.listing_id])}")
        time.sleep(1)
     
        self.browser.get(f"{self.live_server_url}{reverse('send_message', args=[self.listing.listing_id])}")
        time.sleep(1)
        
        # 3. Now the 'content' box should be visible
        self.browser.find_element(By.NAME, "content").send_keys("Is this available?")
        self.browser.find_element(By.NAME, "content").submit()
        time.sleep(2)
        self.assertEqual(Message.objects.count(), 1)

    # --- 11. User can submit a support ticket ---
    def test_user_can_submit_support_ticket(self):
        self.login_user("borrower1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('create_ticket')}")
        time.sleep(2)
        
        self.browser.find_element(By.NAME, "subject").send_keys("Missing part")
        self.browser.find_element(By.NAME, "description").send_keys("Help!")
        Select(self.browser.find_element(By.NAME, "category")).select_by_value("dispute")
        
        self.browser.find_element(By.NAME, "subject").submit()
        time.sleep(4)
        self.assertEqual(SupportTicket.objects.count(), 1)
        
# --- 12. User can submit a review ---
    def test_user_can_submit_review(self):
        Booking.objects.create(
            listing=self.listing, borrower=self.borrower,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() - timedelta(days=2),
            status=Booking.Status.RETURNED
        )
        
        self.login_user("borrower1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('create_review')}?seller_id={self.owner.user_id}")
        time.sleep(2)

    
        listing_dropdown = Select(self.browser.find_element(By.ID, "id_listing"))
        listing_dropdown.select_by_index(1) 
        
        self.browser.find_element(By.NAME, "rating").send_keys("5")
        self.browser.find_element(By.NAME, "comment").send_keys("Great tool!")
        self.browser.find_element(By.NAME, "comment").submit()
        time.sleep(4)
        
        self.assertEqual(Review.objects.count(), 1)

    # --- 13. User can submit a report ---
    def test_user_can_submit_report(self):
        self.login_user("borrower1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('create_report', args=[self.owner.user_id])}")
        time.sleep(2)
        
        self.browser.find_element(By.NAME, "reason").send_keys("Rude behavior")
        self.browser.find_element(By.NAME, "reason").submit()
        time.sleep(4)
        self.assertEqual(Report.objects.count(), 1)

    # --- 14. User cannot submit a review for an incomplete transaction ---
    def test_cannot_review_incomplete_transaction(self):
        self.login_user("borrower1", "testpassword123")
        self.browser.get(f"{self.live_server_url}{reverse('create_review')}?seller_id={self.owner.user_id}")
        time.sleep(2)
        
        self.browser.find_element(By.NAME, "rating").send_keys("1")
        self.browser.find_element(By.NAME, "comment").send_keys("Bad!")
        self.browser.find_element(By.NAME, "comment").submit()
        time.sleep(4)
        
       
        self.assertEqual(Review.objects.count(), 0)