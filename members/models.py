from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.
class MemberInfo(models. Model):
    firstname = models.CharField(max_length=255) 
    lastname = models.CharField(max_length=255)


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
        ('Buyer', 'Buyer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Buyer')
    # real estate agent Approvel
    is_agent_application_pending = models.BooleanField(default=False)
    # real estate agent Reject
    was_agent_application_rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()



# models.py

class Property(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)    
    ownership_proof = models.ImageField(upload_to='ownership_proofs/')
    land_owner_photo = models.ImageField(upload_to='owner_photos/')
    description = models.CharField(max_length=1000, blank=True, null=True)
    water_source = models.CharField(max_length=255)
    electricity_connection = models.CharField(max_length=255)
    land_type = models.CharField(max_length=255)
    total_area = models.CharField(max_length=255)
    soil_type = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    map_link = models.URLField(blank=True, null=True)  # New field to store the Google Maps URL
    phone = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return f"{self.land_type} land in {self.city}"


class LandImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='land_images')
    image = models.ImageField(upload_to='land_images/')

    

class Review(models.Model):
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, related_name="reviews", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)  # New field

    def __str__(self):
        return f"Review by {self.author.username} for {self.property.title}"
    

# like button 
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')  # Prevent duplicate likes



class VisitRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='visit_requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_visit_requests')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_visit_requests')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    message = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Visit request by {self.buyer.username} for {self.property}"
    


# contact
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} from {self.name}"
