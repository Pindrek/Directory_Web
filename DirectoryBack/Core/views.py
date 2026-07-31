from django.contrib.auth import authenticate
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError

from .models import UserProfile, Directory, File, User
from Core.serializers.userProfileSerializers import UserProfileSerializer
from Core.serializers.directorySerializers import DirectoryCreateSerializer, DirectorySerializer
from Core.serializers.fileSerializers import FileSerializer, FileCreateSerializer
from Core.pagination import FilePagination

# Create your views here.
class SignUp(APIView):
    @transaction.atomic
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "missing username or password"}, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "existing username"}, status=HTTP_409_CONFLICT)
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        UserProfile.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=HTTP_201_CREATED)

class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "missing username or password"}, status=HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "invalid credentials"}, status=HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=HTTP_200_OK)

class Home(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userProfile = get_object_or_404(UserProfile, user=request.user)
        userProfileSerializer = UserProfileSerializer(userProfile, many=False)

        directories = Directory.objects.filter(owner=request.user)
        directoriesSerializer = DirectorySerializer(directories, many=True)

        return Response({
            "userProfile": userProfileSerializer.data,
            "directories": directoriesSerializer.data,
        })

class UnAuth(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({"error": "missing refresh"}, status=HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response({"error": "invalid refresh"}, status=HTTP_400_BAD_REQUEST)
        return Response({"logout": True}, status=HTTP_200_OK)

class Directories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DirectoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def patch(self, request):
        directory = get_object_or_404(Directory, id=request.data.get("id"), owner=request.user)
        serializer = DirectorySerializer(directory, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        directory = get_object_or_404(Directory, id=request.data.get("id"), owner=request.user)
        directory.delete()
        return Response({"delete": True}, status=HTTP_200_OK)

class Files(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = FilePagination

    def post(self, request):
        serializer = FileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        directory = serializer.validated_data['directory']
        if directory.owner != request.user:
            return Response({"error": "invalid owner"}, status=HTTP_401_UNAUTHORIZED)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def patch(self, request):
        file = get_object_or_404(File, id=request.data.get("id"), directory__owner=request.user)
        serializer = FileSerializer(file, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    def get(self, request):
        files = File.objects.filter(directory=request.query_params.get("directory_id"), directory__owner=request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(files, request)
        serializer = FileSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def delete(self, request):
        file = get_object_or_404(File, id=request.data.get("id"), directory__owner=request.user)
        file.delete()
        return Response({"delete": True}, status=HTTP_200_OK)