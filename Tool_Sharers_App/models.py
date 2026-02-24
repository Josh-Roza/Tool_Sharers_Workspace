from django.db import models

class Monster(models.Model):
    name = models.CharField(max_length=100)
    HP = models.IntegerField()
    AC = models.IntegerField()
    CR = models.CharField(max_length=10)
    speed = models.CharField(max_length=300)
    stats = models.CharField(max_length=100)
    skills = models.TextField()
    attributes = models.TextField()
    actions = models.TextField()
    legendaryActions = models.TextField()
    rangedAttack = models.BooleanField(default=False)
    pack = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):
    user_id = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Listing(models.Model):
    listing__id = models.IntegerField()
    user = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    condition = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Image(models.Model):
    image_id = models.IntegerField()
    listing = models.ForeignKey(Listing)
    image_url = models.URLField()

    def __str__(self):
        return self.name

class Sale(models.Model):
    sale_id = models.IntegerField()
    listing = models.ForeignKey(Listing)
    buyer = models.ForeignKey(User)
    seller = models.ForeignKey(User)
    sale_date = models.DateTimeField(auto_now_add=True)
    listed_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_status = models.CharField(max_length=100)
    rental_status = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Review(models.Model):
    review_id = models.IntegerField()
    listing = models.ForeignKey(Listing)
    buyer_id = models.ForeignKey(User)
    seller_id = models.ForeignKey(User)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return self.name

class Report(models.Model):
    report_id = models.IntegerField()
    person_reported = models.ForeignKey(User)
    reporter = models.ForeignKey(User)
    sale = models.ForeignKey(Sale)
    reason = models.TextField()
    report_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

