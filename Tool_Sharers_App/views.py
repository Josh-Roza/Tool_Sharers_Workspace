from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Review, Report, Image, Transaction
from .forms import User_Form, Listing_Form, Image_Form, Review_Form, Report_Form

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
    pass

@login_required
def create_report(request):
    pass


@login_required
def delete_user(request):
    pass


@login_required
def delete_review(request):
    pass

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

