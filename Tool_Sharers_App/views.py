from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Review, Report, Image, Transaction
from .forms import User_Form, Listing_Form, Image_Form, Review_Form, Report_Form, Edit_Profile_Form
from django.contrib.auth import get_user_model

def homePage(request):
    #get all tools and then display
    listings = Listing.objects.all().order_by('-listing_id')
    form = Listing_Form()
    return render(request, 'index.html', {'listings': listings, 'form': form})

def add_user(request):
    if request.method == 'POST':
        form = User_Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = User_Form()
    return render(request, "add_user.html", {"form": form})

@login_required
def create_listing(request):
    #create new post for item
    if request.method == "POST":
        form = Listing_Form(request.POST, request.FILES)
        if form.is_valid():
            #create listing object but don't save to db yet
        
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            
            if request.FILES.get('listing_image'):
                Image.objects.create(
                    listing=listing,
                    image=request.FILES['listing_image']
                )
            
            return redirect('home')
    else:
        form = Listing_Form()
    return render(request, 'create_listing.html', {'form': Listing_Form()})

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, listing_id=listing_id, user=request.user)

    if request.method == "POST":
        form = Listing_Form(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('my_listings')
    else:
        form = Listing_Form(instance=listing)
    return render(request, 'create_listing.html', {'form': form, 'edit_mode': True})

def view_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    images = listing.image_set.all()
    
    return render(request, 'listing_detail.html', {
        'listing': listing,
        'images': images
    })

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, listing_id=listing_id, user=request.user)

    if request.method == "POST":
        listing.delete()
        return redirect('my_listings')
    
    return render(request, 'delete_confirm.html', {'listing': listing});

@login_required
def my_listings(request):
    user_listings = Listing.objects.filter(user=request.user).order_by('-listing_id')
    return render(request, 'my_listings.html', {'listings': user_listings})

@login_required
def create_review(request):
    seller_id = request.GET.get('seller_id')
    seller = get_object_or_404(User, user_id=seller_id) if seller_id else None

    if request.method == "POST":
        form = Review_Form(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.buyer = request.user
            review.seller = seller

            if review.seller == request.user:
                form.add_error(None, "You cannot review yourself.")
                return render(request, "create_review.html", {"form": form, "seller": seller})

            review.save()
            return redirect('view_profile', user_id=review.seller.user_id)
    else:
        form = Review_Form()

    return render(request, "create_review.html", {"form": form, "seller": seller})

@login_required
def create_report(request, user_id):
    reported_user = get_object_or_404(User, pk=user_id)

    if reported_user == request.user:
        return redirect('view_profile', user_id=reported_user.user_id)

    if request.method == 'POST':
        form = Report_Form(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.person_reported = reported_user
            report.save()
            return redirect('view_profile', user_id=reported_user.user_id)
    else:
        form = Report_Form()

    return render(request, 'create_report.html', {
        'form': form,
        'reported_user': reported_user
    })

@login_required
def delete_user(request):
    if request.method == "POST":
        request.user.delete()
        return redirect('home')

    return render(request, 'delete_user_confirm.html')

@login_required
def delete_review(request, review_id):
    # Get the review, or 404 if it doesn't exist
    review = get_object_or_404(Review, review_id=review_id)

    # Only allow the buyer who wrote the review to delete it
    if review.buyer != request.user:
        return redirect('view_profile', user_id=review.seller.user_id)

    # Delete the review
    review.delete()

    # Redirect back to the seller's profile
    return redirect('view_profile', user_id=review.seller.user_id)

#Unnecessary, leave as pass, will be handled in admin
@login_required
def delete_report(request):
    pass

def add_image(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.method == "POST":
        form = Image_Form(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.listing = listing # link img to listing
            new_image.save()
            return redirect('home')
    else:
        form = Image_Form()
    
    return render(request, 'add_image.html', {'form': form, 'listing': listing})

@login_required
def my_profile(request):
    reviews = Review.objects.filter(seller=request.user)

    return render(request, 'my_profile.html', {
        'profile_user': request.user,
        'reviews': reviews
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = Edit_Profile_Form(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = Edit_Profile_Form(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

def view_profile(request, user_id):
    UserModel = get_user_model()
    profile_user = get_object_or_404(UserModel, pk=user_id)
    reviews = Review.objects.filter(seller=profile_user)

    return render(request, 'view_profile.html', {
        'profile_user': profile_user,
        'reviews': reviews
    })