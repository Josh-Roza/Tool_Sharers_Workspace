from django.contrib import admin
from .models import User, Listing, Transaction, Report, Image, Review, Category, Message

# Register your models here.

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Transaction)
admin.site.register(Report)
admin.site.register(Image)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Message)