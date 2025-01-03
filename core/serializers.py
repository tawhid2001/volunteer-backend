from rest_framework import serializers
from .models import VolunteerWork, Review,Profile,User,JoinRequest,Category
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
import requests
from rest_framework.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    profile_picture = serializers.URLField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True)
    contact_info = serializers.CharField(required=False, allow_null=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        data['profile_picture'] = self.validated_data.get('profile_picture', None)
        data['bio'] = self.validated_data.get('bio', '')
        data['contact_info'] = self.validated_data.get('contact_info', '')
        return data

    def save(self, request):
        try:
            user = super().save(request)
            user.first_name = self.validated_data.get('first_name', '')
            user.last_name = self.validated_data.get('last_name', '')
            user.save()

            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "bio": self.validated_data.get('bio', ''),
                    "contact_info": self.validated_data.get('contact_info', ''),
                    "profile_picture": self.validated_data.get('profile_picture')
                }
            )
            print("profile created", profile)
            profile.save()

            logger.info("Profile creation status: %s", "Created" if created else "Already exists")

            # Token and email
            Token.objects.create(user=user)
            send_welcome_email(user.email, user.first_name)
            return user
        except Exception as e:
            logger.error("Error during registration: %s", str(e))
            raise ValidationError("An error occurred during registration.")
    

class UserProfileRegisterSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_picture = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    contact_info = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)  # Add this line
    last_name = serializers.CharField(required=True)   # Add this line

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'bio', 'profile_picture', 'contact_info']

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        # Remove password1 and password2 to get the actual password
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1'],  # Use password1 here
            first_name=validated_data['first_name'],  # Set first name
            last_name=validated_data['last_name']     # Set last name
        )

        # Create profile linked to the user
        Profile.objects.create(
            user=user,
            bio=validated_data.pop('bio', ''),
            profile_picture=validated_data.pop('profile_picture', None),
            contact_info=validated_data.pop('contact_info', '')
        )

        return user



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    rating_display = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'volunteer_work', 'user', 'rating', 'rating_display', 'comment', 'created_at']

    def get_rating_display(self, obj):
        return '⭐' * obj.rating

class VolunteerWorkSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerWork
        fields = ['id', 'title', 'description', 'location', 'date', 'organizer', 'participants', 'category', 'average_rating','image_url']

    def get_average_rating(self, obj):
        return obj.average_rating()
    
    def create(self,validated_data):
        image_url = validated_data.pop('image_url',None)
        volunteer_work = VolunteerWork.objects.create(**validated_data)
        if image_url:
            volunteer_work.image_url = image_url
            volunteer_work.save()
        return volunteer_work
    
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'contact_info']
    
class CustomUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

class JoinRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    volunteer_work_title = serializers.CharField(source='volunteer_work.title', read_only=True)
    volunteer_work = serializers.PrimaryKeyRelatedField(queryset=VolunteerWork.objects.all())

    class Meta:
        model = JoinRequest
        fields = ['id', 'volunteer_work','volunteer_work_title', 'user', 'status', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


def send_welcome_email(user_email, first_name):
    subject = 'Welcome to Our Platform!'
    message = f'Hi {first_name},\n\nWelcome to our platform! We are excited to have you join our community.\n\nBest regards,\nThe Team'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def send_html_welcome_email(user_email, first_name):
    subject = 'Welcome to Our Platform!'
    message = f'Hi {first_name}, Welcome to our platform!'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    html_message = f"""
    <html>
        <body>
            <p>Hi <strong>{first_name}</strong>,</p>
            <p>Welcome to our platform! We are excited to have you join us.</p>
            <p>Best regards,</p>
            <p>The Team</p>
        </body>
    </html>
    """

    send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)