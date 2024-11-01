from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated,AllowAny
from .models import VolunteerWork, Review,JoinRequest,Category
from .serializers import VolunteerWorkSerializer, ReviewSerializer,JoinRequestSerializer,CategorySerializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsOrganizerOrReadOnly,IsOrganizer
from dj_rest_auth.registration.views import RegisterView
from rest_framework.views import APIView
from .serializers import CustomRegisterSerializer,CustomUserSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from .models import Profile
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)

class CustomRegisterView(RegisterView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = CustomRegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save(request)
                return Response({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in registration: {e}")
            return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class VolunteerWorkViewSet(viewsets.ModelViewSet):
    queryset = VolunteerWork.objects.all()
    serializer_class = VolunteerWorkSerializer

    def get_permissions(self):
        # Apply different permissions for different actions
        if self.action in ['list', 'retrieve','details']:
            permission_classes = [AllowAny]
        elif self.action in ['my_works', 'participated_works']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.organizer != request.user:
            return Response({"detail": "You do not have permission to edit this volunteer work."}, status=403)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.organizer != request.user:
            return Response({"detail": "You do not have permission to delete this volunteer work."}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_works(self, request):
        """List of volunteer work organized by the user."""
        queryset = VolunteerWork.objects.filter(organizer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def participated_works(self, request):
        """List of volunteer work the user has participated in."""
        queryset = VolunteerWork.objects.filter(participants=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Details of a specific volunteer work."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UserDetailViewById(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')  # Get user ID from the URL
        try:
            user = User.objects.get(pk=user_id)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        volunteer_work_id = self.request.query_params.get('volunteer_work', None)
        if volunteer_work_id is not None:
            return Review.objects.filter(volunteer_work_id=volunteer_work_id)
        return Review.objects.all()
    
    def perform_create(self, serializer):
        # Ensure the user can't review the same volunteer work more than once
        volunteer_work = serializer.validated_data['volunteer_work']
        if Review.objects.filter(volunteer_work=volunteer_work, user=self.request.user).exists():
            raise serializers.ValidationError("You have already reviewed this volunteer work.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Allow the user to update their review only
        if self.get_object().user != self.request.user:
            raise serializers.ValidationError("You do not have permission to edit this review.")
        serializer.save()

    def perform_destroy(self, instance):
        # Allow the user to delete their review only
        if instance.user != self.request.user:
            raise serializers.ValidationError("You do not have permission to delete this review.")
        instance.delete()  

@api_view(['GET'])
def has_reviewed(request, volunteer_work_id):
    user = request.user
    if not user.is_authenticated:
        return Response({'reviewed': False})

    # Check if the user has already reviewed this volunteer work
    has_reviewed = Review.objects.filter(volunteer_work_id=volunteer_work_id, user=user).exists()
    return Response({'reviewed': has_reviewed})

    


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

class UserEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Update user fields
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)

        # Save user changes
        user.save()

        # Update or create profile fields
        profile, created = Profile.objects.get_or_create(user=user)

        # Update profile fields
        profile.bio = data.get('bio', profile.bio)
        profile.contact_info = data.get('contact_info', profile.contact_info)

        # If profile_picture URL is provided, update it
        profile_picture_url = data.get('profile_picture')
        if profile_picture_url:
            profile.profile_picture = profile_picture_url  # Directly set the URL

        # Save profile changes
        profile.save()

        # Return success response
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile': {
                'bio': profile.bio,
                'profile_picture': profile.profile_picture,
                'contact_info': profile.contact_info,
            }
        }, status=status.HTTP_200_OK)
      

class JoinRequestViewSet(viewsets.ModelViewSet):
    queryset = JoinRequest.objects.all()
    serializer_class = JoinRequestSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        """
        Optionally restricts the returned join requests to those for the current user's volunteer works.
        """
        user = self.request.user
        return JoinRequest.objects.filter(volunteer_work__organizer=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        join_request = self.get_object()
        join_request.status = 'approved'
        join_request.save()
        join_request.volunteer_work.participants.add(join_request.user)
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        join_request = self.get_object()
        join_request.status = 'rejected'
        join_request.save()
        return Response({'status': 'rejected'})
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryworklistViewSet(APIView):
    def get(self,request,slug=None):
        category = get_object_or_404(Category,slug=slug)
        VolunteerWorks = VolunteerWork.objects.filter(category=category)
        serializer = VolunteerWorkSerializer(VolunteerWorks,many=True)
        return Response(serializer.data)