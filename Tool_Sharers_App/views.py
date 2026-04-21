from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import User, Listing, Review, Report, Image, Transaction, Category, Booking, Message, SupportTicket, TicketMessage
from .forms import User_Form, Listing_Form, Image_Form, Review_Form, Report_Form, Edit_Profile_Form, Message_Form, SupportTicketForm, TicketMessageForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.views import LoginView

from .geocoding import geocode_address, haversine_miles


def homePage(request):
    
    today = timezone.now().date()
    
    listings = Listing.objects.exclude(
        bookings__status__in=[Booking.Status.APPROVED, Booking.Status.ACTIVE],
        bookings__start_date__lte=today,
        bookings__end_date__gte=today).distinct().order_by('-listing_id')

    categories = Category.objects.all().order_by('name')

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    condition = request.GET.get('condition', '').strip()
    location_query = request.GET.get('location', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    max_distance = request.GET.get('max_distance', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if category_id:
        listings = listings.filter(category_id=category_id)

    if condition:
        listings = listings.filter(condition=condition)

    if min_price:
        try:
            listings = listings.filter(price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=max_price)
        except ValueError:
            pass

    listings_list = list(listings)

    origin_coords = geocode_address(location_query) if location_query else None
    max_distance_value = None

    if max_distance:
        try:
            max_distance_value = float(max_distance)
        except ValueError:
            max_distance_value = None

    for listing in listings_list:
        listing.distance_display = None
        listing.distance_miles = None

        if origin_coords is not None:
            listing_coords = geocode_address(listing.location) if listing.location else None
            if listing_coords is not None:
                miles = haversine_miles(origin_coords, listing_coords)
                listing.distance_miles = miles
                listing.distance_display = f"{miles:.1f} mi"

    if origin_coords is not None and max_distance_value is not None:
        listings_list = [
            listing for listing in listings_list
            if listing.distance_miles is not None and listing.distance_miles <= max_distance_value
        ]

    if sort_by == 'nearest' and origin_coords is not None:
        listings_list.sort(key=lambda l: (l.distance_miles is None, l.distance_miles or 0.0))
    elif sort_by == 'price_low':
        listings_list.sort(key=lambda l: l.price)
    elif sort_by == 'price_high':
        listings_list.sort(key=lambda l: l.price, reverse=True)
    else:
        listings_list.sort(key=lambda l: l.listing_id, reverse=True)

    listings = listings_list

    form = Listing_Form()

    return render(request, 'index.html', {
        'listings': listings,
        'form': form,
        'categories': categories,
        'selected_query': query,
        'selected_location': location_query,
        'selected_category': category_id,
        'selected_condition': condition,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_max_distance': max_distance,
        'selected_sort': sort_by,
        'condition_choices': Listing.Condition.choices,
        'distance_choices': ["5", "10", "25", "50", "100"],
    })

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
    return render(request, 'create_listing.html', {'form': form})

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

    reserved_bookings = listing.bookings.filter(
        status__in=[Booking.Status.APPROVED, Booking.Status.ACTIVE]
    ).order_by('start_date')

    return render(request, 'listing_detail.html', {
        'listing': listing,
        'images': images,
        'reserved_bookings': reserved_bookings,
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
    lender_id = request.GET.get('seller_id') 
    lender_obj = get_object_or_404(User, user_id=lender_id) if lender_id else None

    if request.method == "POST":

        review_instance = Review(borrower=request.user, lender=lender_obj)
        form = Review_Form(request.POST, instance=review_instance)
        
        if form.is_valid():
            if lender_obj == request.user:
                form.add_error(None, "You cannot review yourself.")
                return render(request, "create_review.html", {"form": form, "seller": lender_obj})

            form.save()
            return redirect('view_profile', user_id=lender_obj.user_id)
    else:
        form = Review_Form()

    return render(request, "create_review.html", {"form": form, "seller": lender_obj})

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
    if request.method == "POST":
        seller_id = review.seller.user_id
        review.delete()
        return redirect('view_profile', user_id=seller_id)

    # Redirect back to the seller's profile
    return redirect('view_profile', user_id=review.seller.user_id)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, review_id=review_id, buyer=request.user)

    if request.method == "POST":
        form = Review_Form(request.POST, instance=review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.buyer = request.user
            updated_review.seller = review.seller
            updated_review.save()
            return redirect('view_profile', user_id=review.seller.user_id)
    else:
        form = Review_Form(instance=review)

    return render(request, 'edit_review.html', {
        'form': form,
        'review': review
    })

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
    reviews = Review.objects.filter(lender=request.user)

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
    reviews = Review.objects.filter(lender=profile_user)

    listing_id = request.GET.get('listing_id')
    context_listing = None

    if listing_id:
        context_listing = Listing.objects.filter(pk=listing_id).first()

    return render(request, 'view_profile.html', {
        'profile_user': profile_user,
        'reviews': reviews,
        'context_listing': context_listing,
    })

@login_required
def start_profile_message(request, user_id, listing_id):
    other_user = get_object_or_404(User, pk=user_id)
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.user == other_user:
        return redirect('view_profile', user_id=other_user.user_id)

    # Only allow messaging if the listing is relevant to either the viewer or the profile user
    if listing.user != request.user and listing.user != other_user:
        booking_exists = Booking.objects.filter(
            listing=listing
        ).filter(
            Q(borrower=request.user, listing__user=other_user) |
            Q(borrower=other_user, listing__user=request.user)
        ).exists()

        if not booking_exists:
            return redirect('view_profile', user_id=other_user.user_id)

    return redirect('conversation', listing_id=listing.listing_id, user_id=other_user.user_id)

@login_required
def request_booking(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        booking = Booking(
            listing = listing,
            borrower = request.user,
            start_date = start_date,
            end_date = end_date,
            status = Booking.Status.PENDING
        )
        
        try:
            booking.full_clean()
            booking.save()
            return redirect('manage_bookings')
        except ValidationError as e:
            images = listing.image_set.all()
            reserved_bookings = listing.bookings.filter(
                status__in=[Booking.Status.APPROVED, Booking.Status.ACTIVE]
            ).order_by('start_date')

            return render(request, 'listing_detail.html', {
                'listing': listing,
                'images': images,
                'reserved_bookings': reserved_bookings,
                'error': e.message_dict if hasattr(e, 'message_dict') else e.messages
            })
    return redirect('view_listing', listing_id=listing_id)

@login_required
def manage_bookings(request):
    my_rentals = Booking.objects.filter(borrower=request.user).order_by('-created_at')
    
    incoming_requests = Booking.objects.filter(listing__user=request.user).order_by('-created_at')
    
    return render(request, 'manage_bookings.html', {
        'my_rentals': my_rentals,
        'incoming_requests': incoming_requests
    })
    
@login_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, listing__user=request.user)
    
    if request.method == "POST":
        booking.status = Booking.Status.APPROVED
        booking.save()
        
        Transaction.objects.get_or_create(
            booking=booking,
            defaults={
                'final_price': booking.total_cost,
                'payment_sent': False,
                'payment_confirmed': False
            }
        )
        return redirect('manage_bookings')
    
@login_required
def action_booking(request, booking_id, action):
    booking = get_object_or_404(Booking, pk=booking_id)

    is_lender = booking.listing.user == request.user
    is_borrower = booking.borrower == request.user

    if not (is_lender or is_borrower):
        return redirect('manage_bookings')
    
    if request.method == "POST":
        if action == 'decline' and is_lender and booking.status == Booking.Status.PENDING:
            booking.status = Booking.Status.DECLINED

        elif action == 'cancel' and is_borrower and booking.status in [Booking.Status.PENDING, Booking.Status.APPROVED]:
            booking.status = Booking.Status.CANCELLED

        elif action == 'pickup' and is_borrower and booking.status == Booking.Status.APPROVED:
            if hasattr(booking, 'payment_record') and booking.payment_record.payment_confirmed:
                booking.status = Booking.Status.ACTIVE

        elif action == 'return' and is_lender and booking.status == Booking.Status.ACTIVE:
            booking.status = Booking.Status.RETURNED

        booking.save()

    return redirect('manage_bookings')

@login_required
def mark_payment_sent(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, pk=booking_id, borrower=request.user)

        if booking.status != Booking.Status.APPROVED:
            return redirect('manage_bookings')

        transaction = booking.payment_record
        transaction.payment_sent = True
        transaction.save()

    return redirect('manage_bookings')

@login_required
def confirm_payment(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, pk=booking_id, listing__user=request.user)

        if booking.status != Booking.Status.APPROVED:
            return redirect('manage_bookings')

        transaction = booking.payment_record

        if transaction.payment_sent:
            transaction.payment_confirmed = True
            transaction.save()

    return redirect('manage_bookings')

@login_required
def inbox(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).select_related('listing', 'sender', 'recipient').order_by('-timestamp')

    conversations = []
    seen = set()

    for message in messages:
        other_user = message.recipient if message.sender == request.user else message.sender
        key = (message.listing.listing_id, other_user.user_id)

        if key not in seen:
            seen.add(key)
            conversations.append({
                'listing': message.listing,
                'other_user': other_user,
                'last_message': message,
            })

    return render(request, 'inbox.html', {
        'conversations': conversations
    })


@login_required
def conversation(request, listing_id, user_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    other_user = get_object_or_404(User, pk=user_id)

    messages = Message.objects.filter(
        listing=listing
    ).filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')

    if request.user != listing.user and not messages.exists():
        return redirect('inbox')

    Message.objects.filter(
        listing=listing,
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    if request.method == 'POST':
        form = Message_Form(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.listing = listing
            new_message.sender = request.user
            new_message.recipient = other_user
            new_message.save()
            return redirect('conversation', listing_id=listing.listing_id, user_id=other_user.user_id)
    else:
        form = Message_Form()

    return render(request, 'conversation.html', {
        'listing': listing,
        'other_user': other_user,
        'messages': messages,
        'form': form,
    })

@login_required
def send_message(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.user == listing.user:
        return redirect('view_listing', listing_id=listing.listing_id)

    if request.method == 'POST':
        form = Message_Form(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.listing = listing
            message.sender = request.user
            message.recipient = listing.user
            message.save()
            return redirect('conversation', listing_id=listing.listing_id, user_id=listing.user.user_id)

    return redirect('view_listing', listing_id=listing.listing_id)

@login_required
def create_ticket(request):
    if request.method == "POST":
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            return redirect("ticket_detail", ticket.id)
    else:
        form = SupportTicketForm()

    return render(request, "create_ticket.html", {"form": form})


@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(created_by=request.user)
    return render(request, "ticket_list.html", {"tickets": tickets})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    if request.method == "POST":
        form = TicketMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.ticket = ticket
            msg.sender = request.user
            msg.save()
            return redirect("ticket_detail", ticket.id)
    else:
        form = TicketMessageForm()

    return render(request, "ticket_detail.html", {
        "ticket": ticket,
        "form": form
    })

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        return form