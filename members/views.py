from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Property, LandImage,  Review, Like, VisitRequest
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, IntegerField
from members.models import Property
from .models import UserProfile
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail  # Optional: if sending email
from .models import ContactMessage

# error handling
def custom_404(request, exception):
    return render(request, 'error_page.html', status=404)

def custom_500(request):
    return render(request, 'error_page.html', status=500)

def custom_403(request, exception):
    return render(request, 'error_page.html', status=403)

def custom_400(request, exception):
    return render(request, 'error_page.html', status=400)


# Create your views here.
# def index(request):
#     return render(request, "index.html")
# def index(request):
#     if request.user.is_authenticated:
#         profile = request.user.userprofile
#         if profile.role == 'Admin':
#             return redirect('admin_dashboard') 
#     return render(request, "index.html")
def index(request):
    if request.user.is_authenticated:
        profile = request.user.userprofile
        if profile.role == 'Admin':
            return redirect('admin_dashboard')
        elif profile.was_agent_application_rejected:
            messages.error(request, "❌Admin has not approved your request.")
            # Clear the rejection flag after showing the message once
            profile.was_agent_application_rejected = False
            profile.save()
    return render(request, "index.html")



@login_required
def admin_dashboard(request):
    if request.user.userprofile.role != 'Admin':
        return redirect('index')
    pending_users = UserProfile.objects.filter(is_agent_application_pending=True)
    return render(request, 'admin_dashboard.html', {'pending_users': pending_users})


def seller_dashboard(request):
    return render(request, 'seller_dashboard.html')

def buyer_dashboard(request):
    return render(request, 'buyer_dashboard.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        name = request.POST.get('name')
        role = request.POST.get('role')

        if not username or not password or not email or not name or not role:
            messages.error(request, "All fields are required.")
            return redirect('register')

        try:
            # If role is Admin, create a superuser
            if role == 'Admin':
                user = User.objects.create_superuser(username=username, email=email, password=password)
                user.first_name = name
                user.save()
            else:
                # For Seller or Buyer, create a normal user
                user = User.objects.create_user(username=username, email=email, password=password, first_name=name)

            # Create the associated UserProfile
            UserProfile.objects.create(user=user, role=role)

            messages.success(request, "Account created successfully.")
            return redirect('userlogin')

        except IntegrityError:
            messages.error(request, "Username already exists.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'pages-register.html')


def userlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            messages.success(request, '🔓 Login successful!')  # ✅ Add this line

            role = user.userprofile.role  # Access role from UserProfile
            if role == 'Admin':
                return redirect('admin_dashboard')
            elif role == 'Seller':
                return redirect('seller_dashboard')
            elif role == 'Buyer':
                return redirect('buyer_dashboard')
            else:
                return redirect('index')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'pages-login.html')






def user_logout(request):
    logout(request)
    messages.success(request, '🔒 Logged out successfully!')
    return redirect('index')


def newproperty(request):
    if request.method == "POST":
        land_owner_photo = request.FILES.get('land_owner_photo')
        ownership_proof = request.FILES.get('ownership_proof')
        description = request.POST.get('description')
        water_source = request.POST.get('water_source')
        electricity_connection = request.POST.get('electricity_connection')
        land_type = request.POST.get('land_type')
        total_area = request.POST.get('total_area')
        soil_type = request.POST.get('soil_type')
        state = request.POST.get('state')
        city = request.POST.get('city')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        map_link = generate_google_maps_link(state, city, location)

        # First save property
        new_property = Property.objects.create(
            owner=request.user,
            land_owner_photo=land_owner_photo,
            ownership_proof=ownership_proof,
            description=description,
            water_source=water_source,
            electricity_connection=electricity_connection,
            land_type=land_type,
            total_area=total_area,
            soil_type=soil_type,
            state=state,
            city=city,
            location=location,
            phone=phone,
            email=email,
            map_link=map_link,
        )

        # Save each uploaded land image
        for img in request.FILES.getlist('land_image'):
            LandImage.objects.create(property=new_property, image=img)
            messages.success(request, '✅ Property added successfully!')
        return redirect('success_page')

    return render(request, 'newproperty.html')




def all_properties(request):
    all_properties = Property.objects.all()
    return render(request, 'properties.html', {'properties': all_properties})


def success_page(request):
    return render(request, 'success.html')

def error_page(request):
    return render(request, 'error_page.html')

# Property id creater
def single_property(request, id):
    property_instance = get_object_or_404(Property, id=id)
    for review in property_instance.reviews.all():
        review.star_range = range(review.rating)
    return render(request, 'property-single.html', {'Property': property_instance})


# property delete
def delete_property(request, id):
    property = get_object_or_404(Property, id=id)

    # Allow if owner or admin
    if property.owner != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this property.")

    if request.method == 'POST':
        property.delete()
        messages.success(request, "🗑 Property deleted successfully.")
        return redirect('all_properties')

    return redirect('property_single', id=id)





# property edit
def edit_property(request, id):
    property_instance = get_object_or_404(Property, id=id)

    # Allow if owner or admin
    if property_instance.owner != request.user and not request.user.is_superuser:
        return redirect('unauthorized')

    if request.method == "POST":
        # Update image fields only if a new file is uploaded
        if request.FILES.get('ownership_proof'):
            property_instance.ownership_proof = request.FILES['ownership_proof']

        if request.FILES.get('land_owner_photo'):
            property_instance.land_owner_photo = request.FILES['land_owner_photo']

        land_images = request.FILES.getlist('land_image')
        if land_images:
            # Delete old land images
            property_instance.land_images.all().delete()
            # Save new land images
            for img in land_images:
                LandImage.objects.create(property=property_instance, image=img)

        # Existing field updates
        property_instance.description = request.POST.get('description')
        property_instance.water_source = request.POST.get('water_source')
        property_instance.electricity_connection = request.POST.get('electricity_connection')
        property_instance.land_type = request.POST.get('land_type')
        property_instance.total_area = request.POST.get('total_area')
        property_instance.soil_type = request.POST.get('soil_type')
        property_instance.state = request.POST.get('country')
        property_instance.city = request.POST.get('city')
        property_instance.location = request.POST.get('location')
        property_instance.phone = request.POST.get('phone')
        property_instance.email = request.POST.get('email')

        property_instance.save()
        messages.success(request, '')
        messages.success(request, '✏ Your property has been updated successfully!')
        return redirect('single_property', id=id)

    return render(request, 'edit.html', {'Property': property_instance})


# add review
def add_review(request, id):
    if request.method == "POST":
        property_instance = get_object_or_404(Property, id=id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        review = Review.objects.create(
            property=property_instance,
            author=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, '⭐ Review submitted successfully!')
        return redirect('single_property', id=property_instance.id)


# delete review
def delete_review(request, property_id, review_id):
    review = get_object_or_404(Review, id=review_id, property_id=property_id)
    if review.author == request.user:
        review.delete()
    return redirect('single_property', id=property_id)


# profile
def my_profile(request):
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        if 'delete_picture' in request.POST:
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)
                profile.profile_picture = None
                profile.save()
                messages.success(request, 'Profile picture deleted successfully.')
            return redirect('my_profile')

        elif 'save_profile' in request.POST:
            username = request.POST.get('username')

    # Optional: check if username is unique
            if username and User.objects.exclude(pk=user.pk).filter(username=username).exists():
                messages.error(request, "❌ Username already taken.")
            else:
                user.username = username
                user.first_name = request.POST.get('fullName')
                user.email = request.POST.get('email')
                user.save()

                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                    profile.save()

                messages.success(request, '👤 Profile updated successfully.')


        elif 'change_password' in request.POST:
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newpassword')
            confirm_password = request.POST.get('renewpassword')

            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, '👤 Profile updated successfully!')

        return redirect('my_profile')

    return render(request, 'my_profile.html', {'user': user, 'profile': profile})








# search property
def search_properties(request):
    query_state = request.GET.get('state', '').strip()
    query_city = request.GET.get('city', '').strip()
    query_location = request.GET.get('location', '').strip()

    if query_state or query_city or query_location:
        properties = Property.objects.annotate(
            match_score=Case(
                When(
                    Q(state__iexact=query_state) &
                    Q(city__iexact=query_city) &
                    Q(location__icontains=query_location),
                    then=3
                ),
                When(
                    Q(state__iexact=query_state) &
                    Q(city__iexact=query_city),
                    then=2
                ),
                When(
                    Q(city__iexact=query_city) |
                    Q(state__iexact=query_state) |
                    Q(location__icontains=query_location),
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ).filter(match_score__gt=0).order_by('-match_score')
    else:
        properties = Property.objects.none()

    return render(request, 'properties.html', {'properties': properties})


def manage_properties(request):
    properties = Property.objects.all()
    return render(request, 'manage_properties.html', {'properties': properties})



# Booking Visit
def book_visit(request, id):
    property_instance = get_object_or_404(Property, id=id)
    if request.method == 'POST':
        VisitRequest.objects.create(
            property=property_instance,
            buyer=request.user,
            seller=property_instance.owner,  # Assuming you have owner = models.ForeignKey(User,...) in Property
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone_number=request.POST.get('phone_number'),
            message=request.POST.get('message'),
        )
        messages.success(request, '📅 Visit booked successfully!')
    return redirect('single_property', id=id)


def visit_requests_received(request):
    requests = VisitRequest.objects.filter(seller=request.user).order_by('-requested_at')
    return render(request, 'book_visit.html', {'requests': requests})


# contact
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        user = request.user if request.user.is_authenticated else None

        ContactMessage.objects.create(
            user=user,
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, '📩 Thanks for your message! We will contact you soon.')

        return redirect('contact')  # Or wherever you want to redirect
    return render(request, 'contact.html')  # Your contact form template



def handle_contact(request):
    contact_messages = ContactMessage.objects.all().order_by('-timestamp')
    return render(request, 'handling_contact.html', {
        'contact_messages': contact_messages
    })


# like button
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    existing_like = Like.objects.filter(user=request.user, review=review).first()

    if existing_like:
        existing_like.delete()  # Unlike if already liked
    else:
        Like.objects.create(user=request.user, review=review)

    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Redirect back




# apply real estate agent
# def apply_agent(request):
#     if request.method == 'POST':
#         profile = UserProfile.objects.get(user=request.user)
#         profile.role = 'Admin' 
#         profile.save()
#         messages.success(request, "🧑‍💼 Your role has been updated to Admin.")
#         return redirect('admin_dashboard')  
#     return redirect('index') 
@login_required
def apply_agent(request):
    if request.method == 'POST':
        profile = UserProfile.objects.get(user=request.user)
        if profile.role == 'Admin':
            messages.warning(request, "⚠ You are already an Admin.")
        elif profile.is_agent_application_pending:
            messages.info(request, "🕒 You have already applied. Wait for admin approval.")
        else:
            profile.is_agent_application_pending = True
            profile.save()
            messages.success(request, "✅ Application sent to Admin for approval.")
        return redirect('index')  # Change to your user dashboard view name
    return redirect('index')


@login_required
def approve_agents(request):
    if request.user.userprofile.role != 'Admin':
        return redirect('home')
    pending_users = UserProfile.objects.filter(is_agent_application_pending=True)
    return render(request, 'approve_agents.html', {'pending_users': pending_users})


@login_required
def approve_agent(request, user_id):
    if request.user.userprofile.role != 'Admin':
        return redirect('home')
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.role = 'Admin'
    profile.is_agent_application_pending = False
    profile.save()
    messages.success(request, f"{profile.user.username} is now an Admin.")
    return redirect('approve_agents')

@login_required
def reject_agent(request, user_id):
    if request.user.userprofile.role != 'Admin':
        messages.error(request, "Permission denied.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile
    if profile.is_agent_application_pending:
        profile.is_agent_application_pending = False
        profile.was_agent_application_rejected = True  # Set rejection flag
        profile.save()
        messages.error(request, f"❌You have rejected {user.username}'s agent application.")
    
    return redirect('approve_agents')

# Map link
from urllib.parse import quote_plus

def generate_google_maps_link(state, city, location):
    full_address = f"{location}, {city}, {state}"
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(full_address)}"



# ======================API================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, PropertyListSerializer, PropertySerializer, VisitRequestSerializer

from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]  # Ensure no authentication required
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework import generics
class PropertyListView(generics.ListAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyListSerializer
    permission_classes = [AllowAny]  # Public access; change to [IsAuthenticated] if needed

class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]  # Public access; change to [IsAuthenticated] if needed

from rest_framework.permissions import IsAuthenticated

class VisitRequestCreateView(generics.CreateAPIView):
    queryset = VisitRequest.objects.all()
    serializer_class = VisitRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)