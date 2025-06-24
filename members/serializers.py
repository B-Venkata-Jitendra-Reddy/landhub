from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, VisitRequest

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role', 'profile_picture']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    role = serializers.CharField(read_only=True)
    profile_picture = serializers.ImageField(read_only=True, allow_null=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                try:
                    profile = user.userprofile
                    role = profile.role
                    profile_picture = profile.profile_picture.url if profile.profile_picture else None
                except UserProfile.DoesNotExist:
                    role = None
                    profile_picture = None

                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)

                return {
                    'username': user.username,
                    'user_id': user.id,
                    'role': role,
                    'profile_picture': profile_picture,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            else:
                raise serializers.ValidationError("Invalid credentials.")
        else:
            raise serializers.ValidationError("Must include username and password.")


from .models import Property, LandImage, Review, Like

class LandImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandImage
        fields = ['id', 'image']

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'author', 'created_at', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

class PropertySerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    land_images = LandImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'description', 'water_source', 'electricity_connection',
            'land_type', 'total_area', 'soil_type', 'state', 'city', 'location',
            'phone', 'email', 'land_images', 'reviews'
        ]

class PropertyListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    land_images = LandImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'land_type', 'city', 'total_area', 'owner', 'land_images','map_link']
        



from django.core.validators import RegexValidator
class VisitRequestSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller = serializers.CharField(source='seller.username', read_only=True)
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    phone_number = serializers.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Invalid phone number format.")],
        max_length=15
    )

    class Meta:
        model = VisitRequest
        fields = [
            'id', 'property', 'buyer_username', 'seller', 'full_name', 'email',
            'phone_number', 'message', 'requested_at', 'status'
        ]

    def validate(self, data):
        property = data.get('property')
        if not property.owner:
            raise serializers.ValidationError("Property must have an owner.")
        if self.context['request'].user == property.owner:
            raise serializers.ValidationError("You cannot request a visit for your own property.")
        email = data.get('email')
        if not email or '@' not in email:
            raise serializers.ValidationError("Invalid email format.")
        return data

    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        validated_data['seller'] = validated_data['property'].owner
        return super().create(validated_data)