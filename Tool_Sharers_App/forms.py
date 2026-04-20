from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Listing, Report, Review, User, Image, Message, SupportTicket, TicketMessage

class User_Form(forms.ModelForm):
    accept_waiver = forms.BooleanField(
        required=True,
        label="I agree to the liability waiver"
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class Edit_Profile_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'venmo_handle', 'paypal_email', 'preferred_payment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'venmo_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venmo Username (no @)'}),
            'paypal_email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PayPal Email'}),
            'preferred_payment': forms.Select(attrs={'class': 'form-control'}),
        }

class Listing_Form(forms.ModelForm):
    listing_image = forms.ImageField(required=False, label="Upload Photo")
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'location', 'condition', 'category']
        labels = {
            'price': 'Price per day',
        }
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tool'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price per day'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'condition': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Condition'}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Category'}),
        }

class Review_Form(forms.ModelForm):
    rating = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rating (0-5)',
            'min': 0,
            'max': 5
        })
    )

    class Meta:
        model = Review
        fields = ['listing', 'rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment'}),
        }

class Report_Form(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explain why you are reporting this user'
            }),
        }

class Image_Form(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class Message_Form(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your message...',
                'rows': 4,
            }),
        }

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["subject", "description", "category"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }

class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Type your reply..."
            }),
        }