from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username
    
class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    condition = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} - ({self.listing_id})"

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_bought")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_sold")
    transaction_date = models.DateTimeField(auto_now_add=True)
    listed_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_status = models.CharField(max_length=100)
    rental_status = models.CharField(max_length=100)

    def __str__(self):
        return f"Transaction: {self.listing.title} to {self.buyer.username}"

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    person_reported = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_sent")
    transaction = models.ForeignKey(Transaction, null=True, blank=True, on_delete=models.CASCADE)
    reason = models.TextField()
    report_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report {self.report_id}"

class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True, blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.URLField()

    def __str__(self):
        if self.listing:
            return f"Image for {self.listing.title}"
        return f"Image {self.image_id}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_written")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"{self.rating}/5 Review by {self.buyer.username}"