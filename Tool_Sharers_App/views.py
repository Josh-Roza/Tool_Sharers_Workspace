from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import User, Listing, Review, Report, Image, Transaction
from .forms import User_Form, Listing_Form, Review_Form, Report_Form

def homePage(request):
    return render(request, 'index.html')

def create_user(request):
    success = False
    added_user = None
    if request.method == 'POST':
        form = User_Form(request.POST)
        if form.is_valid():
            added_user = form.save()
            success = True
            return render(
                request,
                "add_user.html",
                {"form": form,
                 "success": success,
                 "added_user": added_user},
                )
    else:
        form = User_Form()
    return render(
        request,
        "add_user.html",
        {"form": form,
         "success": success,
         "added_user": added_user},
    )


def create_listing(request):
    pass

def create_review(request):
    pass

def create_report(request):
    pass

def delete_user(request):
    pass

def delete_listing(request):
    pass

def delete_review(request):
    pass

def delete_report(request):
    pass

