from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    user_id = models.BigAutoField(primary_key=True, db_column='id')
    reputation = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    venmo_handle = models.CharField(max_length=50, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)

    class PaymentMethod(models.TextChoices):
        VENMO = 'VE', 'Venmo'
        PAYPAL = 'PP', 'PayPal'
        NONE = 'NO', 'None'

    # Add this missing field
    preferred_payment = models.CharField(
        max_length=2,
        choices=PaymentMethod.choices,
        default=PaymentMethod.NONE
    )

    
    def __str__(self):
        return self.username
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories" #fix

    def __str__(self):
        return self.name
    
class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Condition(models.TextChoices):
        NEW = 'NW', 'New'
        EXCELLENT = 'EX', 'Excellent'
        GOOD = 'GD', 'Good'
        FAIR = 'FR', 'Fair'
        WELL_USED = 'WU', 'Well-Used'

    condition = models.CharField(max_length=2, choices=Condition.choices, default=Condition.GOOD)

    @property
    def current_state(self):
        today = timezone.now().date()

        if self.bookings.filter(
            status=Booking.Status.ACTIVE,
            start_date__lte=today,
            end_date__gte=today
        ).exists():
            return "Borrowed"

        if self.bookings.filter(
            status=Booking.Status.APPROVED,
            start_date__lte=today,
            end_date__gte=today
        ).exists():
            return "Reserved"

        if self.bookings.filter(status=Booking.Status.PENDING).exists():
            return "Pending Requests"

        return "Available"

    def __str__(self):
        return f"{self.title} - ({self.listing_id})"


class GeocodedAddress(models.Model):
    query = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.query

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PE', 'Pending'
        APPROVED = 'AP', 'Approved'
        ACTIVE = 'AC', 'Active'
        RETURNED = 'RE', 'Returned'
        CANCELLED = 'CA', 'Cancelled'
        DECLINED = 'DE', 'Declined'
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings_made")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")
        
        overlapping_bookings = Booking.objects.filter(
            listing=self.listing,
            status__in=[self.Status.APPROVED, self.Status.ACTIVE]
            ).filter(
                Q(start_date__lt=self.end_date + timedelta(days=1)) & Q(end_date__gt=self.start_date)
        )
        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)
            
        if overlapping_bookings.exists():
            raise ValidationError("This tool is already booked for the selected dates.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
            
    @property
    def total_cost(self):
        days = (self.end_date - self.start_date).days
        return self.listing.price * days
    
    def __str__(self):
        return f"{self.listing.title} ({self.start_date} to {self.end_date})"

class Transaction(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment_record")
    
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    security_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    payment_sent = models.BooleanField(default=False)
    payment_confirmed = models.BooleanField(default=False)
    deposit_status = models.BooleanField(default=False)
    
    transaction_date = models.DateTimeField(auto_now_add=True)

    @property
    def listing(self):
        return self.booking.listing

    @property
    def borrower(self):
        return self.booking.borrower

    @property
    def lender(self):
        return self.booking.listing.user
    
    # transaction_id = models.AutoField(primary_key=True)
    # listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    # borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_bought")
    # lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_sold")
    # listed_price = models.DecimalField(max_digits=10, decimal_places=2)
    # deposit_status = models.CharField(max_length=100)
    # rental_status = models.CharField(max_length=100)

    def __str__(self):
        return f"Agreement for {self.booking.listing.title}"

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
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        if self.listing:
            return f"Image for {self.listing.title}"
        return f"Image {self.image_id}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_written")
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"{self.rating}/5 Review by {self.borrower.username}"

class Message(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} about {self.listing.title}"

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    CATEGORY_CHOICES = [
        ("dispute", "Dispute"),
        ("report_user", "Report User"),
        ("payment_issue", "Payment Issue"),
        ("other", "Other"),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets"
    )

    subject = models.CharField(max_length=200)
    description = models.TextField()

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)