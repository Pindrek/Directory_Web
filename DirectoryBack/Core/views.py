from django.contrib.auth import login, logout, authenticate
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from Core.serializers.userProfileSerializers import UserProfileSerializer
from Core.serializers.directorySerializers import DirectoryCreateSerializer, DirectorySerializer
from Core.serializers.fileSerializers import FileSerializer, FileCreateSerializer

# Create your views here.
class SignUp(APIView):
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
        login(request, user)
        UserProfile.objects.create(user=request.user)
        return Response({"sign_up": True})

class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "missing username or password"}, status=HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"login": True})
        else:
            return Response({"error": "invalid credentials"}, status=HTTP_401_UNAUTHORIZED)

class Home(APIView):
    def get(self, request):
        userProfile = UserProfile.objects.get(user=request.user)
        userProfileSerializer = UserProfileSerializer(userProfile, many=False)

        directories = Directory.objects.filter(owner=request.user)
        directoriesSerializer = DirectorySerializer(directories, many=True)

        files = File.objects.filter(directory__owner=request.user)
        filesSerializer = FileSerializer(files, many= True)

        return Response({
            "userProfile": userProfileSerializer.data,
            "directories": directoriesSerializer.data,
            "files": filesSerializer.data,
        })

class Directories(APIView):
    def post(self, request):
        serializer = DirectoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, HTTP_200_OK)

    def patch(self, request):
        object_ = Directory.objects.get(id=request.data.get('id'))
        object_.directory_name = request.data.get('directory_name')
        object_.save()
        serializer = DirectorySerializer(object_)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        pass

class Files(APIView):
    def post(self, request):
        serializer = FileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        directory = serializer.validated_data['directory']
        if directory.owner != request.user:
            return Response({"error": "invalid owner"}, status=HTTP_401_UNAUTHORIZED)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def patch(self, request):
        object_ = File.objects.get(id=request.data.get('id'))
        object_.file_name = request.data.get('file_name')
        object_.save()
        serializer = FileSerializer(object_)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        pass