from django.contrib import admin
from .models import User, Listing, Transaction, Report, Image, Review, Category, Message, SupportTicket, TicketMessage

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Transaction)
admin.site.register(Report)
admin.site.register(Image)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Message)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "created_by", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("subject", "description")


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "sender", "created_at")