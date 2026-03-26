from django import forms
from .models import Listing, Report, Review, User

class User_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        }

class Listing_Form(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['user', 'title', 'description', 'price', 'location', 'condition', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tool'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Condition'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
        }

class Review_Form(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['listing', 'buyer', 'seller', 'rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rating'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment'}),
        }

class Report_Form(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['person_reported', 'reporter', 'transaction', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'What was your issue?'}),
        }

#need an image form

