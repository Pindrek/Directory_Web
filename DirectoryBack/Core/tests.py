from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
import json
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Directory, File, UserProfile
from .imageFunc import create_test_image, delete_test_image

# Create your tests here.

class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(username="test_user", password="12345678")

    def test_sign_up_success(self):
        response = self.client.post(reverse('sign_up'),
        data=json.dumps({"username": "user", "password": "12345678"}), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.filter(username="user").count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_sign_up_no_user(self):
        response = self.client.post(reverse('sign_up'),
        data=json.dumps({"username": "", "password": "12345678"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "missing username or password")
        self.assertEqual(User.objects.count(), 1)

    def test_sign_up_no_password(self):
        response = self.client.post(reverse('sign_up'),
        data=json.dumps({"username": "user", "password": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "missing username or password")
        self.assertEqual(User.objects.count(), 1)

    def test_sign_up_exists_user(self):
        response = self.client.post(reverse('sign_up'),
        data=json.dumps({"username": "test_user", "password": "87654321"}), content_type="application/json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"], "existing username")
        self.assertEqual(User.objects.count(), 1)

    def test_login_success(self):
        response = self.client.post(reverse('login'),
        data=json.dumps({"username": "test_user", "password": "12345678"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(User.objects.count(), 1)

    def test_login_no_user(self):
        response = self.client.post(reverse('login'),
        data=json.dumps({"username": "", "password": "12345678"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "missing username or password")
        self.assertEqual(User.objects.count(), 1)

    def test_login_no_password(self):
        response = self.client.post(reverse('login'),
        data=json.dumps({"username": "user", "password": ""}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "missing username or password")
        self.assertEqual(User.objects.count(), 1)

    def test_login_wrong(self):
        response = self.client.post(reverse('login'),
        data=json.dumps({"username": "wrong", "password": "wrong777"}), content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "invalid credentials")
        self.assertEqual(User.objects.count(), 1)

class TestHome(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test_user", password="12345678")
        self.profile = UserProfile.objects.create(user=self.user, image_profile="ProfileImages/test.jpg")
        self.directory = Directory.objects.create(owner=self.user, directory_name="test_directory")
        self.file = File.objects.create(img="Images/test.jpg", file_name="test_file", directory=self.directory)
        self.refresh = refresh = RefreshToken.for_user(self.user)
        self.access = access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_home_get_method(self):
        response = self.client.get(reverse('home'))
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["userProfile"]["id"], 1)
        self.assertEqual(data["userProfile"]["image_profile"], "/ProfileImages/test.jpg")
        self.assertEqual(data["userProfile"]["user"], 1)
        self.assertEqual(UserProfile.objects.count(), 1)

        self.assertEqual(data["directories"][0]["id"], 1)
        self.assertEqual(data["directories"][0]["directory_name"], "test_directory")
        self.assertEqual(data["directories"][0]["owner"], 1)
        self.assertEqual(Directory.objects.count(), 1)

    def test_home_create_directory(self):
        response = self.client.post(reverse('directory'),
        data=json.dumps({"directory_name": "test_directory_2"}), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["directory_name"], "test_directory_2")
        self.assertEqual(Directory.objects.count(), 2)
        self.assertEqual(Directory.objects.filter(directory_name="test_directory_2").count(), 1)
        self.assertEqual(Directory.objects.filter(owner=1).count(), 2)

    def test_home_create_file(self):
        image = create_test_image()
        response = self.client.post(reverse('file'),{"img": image, "file_name": "test_file_2", "directory": self.directory.id},)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["img"], "/Images/test_2.jpg")
        self.assertEqual(data["file_name"], "test_file_2")
        self.assertEqual(data["directory"], self.directory.id)
        self.assertEqual(File.objects.count(), 2)
        self.assertEqual(File.objects.filter(file_name="test_file_2").count(), 1)
        self.assertEqual(File.objects.count(), 2)
        created_file = File.objects.get(file_name="test_file_2")
        delete_test_image(created_file.img)

    def test_home_update_directory(self):
        response = self.client.patch(reverse('directory'),
        data = json.dumps({"directory_name": "new_test_directory", "id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Directory.objects.filter(directory_name="new_test_directory").count(), 1)
        self.assertEqual(Directory.objects.count(), 1)

    def test_home_wrong_update_directory(self):
        self.client.force_login(self.user)
        response = self.client.patch(reverse('directory'),
        data = json.dumps({"directory_name": "new_test_directory", "id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Directory.objects.filter(directory_name="test_directory").count(), 1)
        self.assertEqual(Directory.objects.count(), 1)

    def test_home_update_file(self):
        response = self.client.patch(reverse('file'),
        data = json.dumps({"file_name": "new_test_file", "id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(File.objects.filter(file_name="new_test_file").count(), 1)
        self.assertEqual(File.objects.count(), 1)

    def test_home_wrong_update_file(self):
        response = self.client.patch(reverse('file'),
        data = json.dumps({"file_name": "new_test_file", "id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(File.objects.filter(file_name="test_file").count(), 1)
        self.assertEqual(File.objects.count(), 1)

    def test_home_delete_directory(self):
        response = self.client.delete(reverse('directory'),
        data = json.dumps({"id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["delete"], True)
        self.assertEqual(Directory.objects.count(), 0)

    def test_home_wrong_delete_directory(self):
        response = self.client.delete(reverse('directory'),
        data = json.dumps({"id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Directory.objects.filter(directory_name="test_directory").count(), 1)
        self.assertEqual(Directory.objects.count(), 1)

    def test_home_delete_file(self):
        response = self.client.delete(reverse('file'),
        data = json.dumps({"id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["delete"], True)
        self.assertEqual(File.objects.count(), 0)

    def test_home_wrong_delete_file(self):
        response = self.client.delete(reverse('file'),
        data = json.dumps({"id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(File.objects.filter(file_name="test_file").count(), 1)
        self.assertEqual(File.objects.count(), 1)

    def test_logout_success(self):
        response = self.client.delete(reverse('logout'), data=json.dumps({"refresh": str(self.refresh)}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["logout"], True)

    def test_logout_not_refresh(self):
        response = self.client.delete(reverse('logout'))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "missing refresh")

    def test_validator_name(self):
        response = self.client.post(reverse('directory'),
        data = json.dumps({"directory_name": "@$(#&!"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Directory.objects.count(), 1)
        self.assertEqual(Directory.objects.filter(directory_name="@$(#&!").count(), 0)

    def test_file_get(self):
        self.dir = Directory.objects.create(directory_name="test_directory_2", owner=self.user)
        File.objects.create(img="Images/test_2.jpg", file_name="test_file_2", directory=self.dir)
        File.objects.create(img="Images/test_3.jpg", file_name="test_file_3", directory=self.dir)
        response = self.client.get(reverse('file'), {"directory_id": self.dir.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["file_name"], "test_file_2")
        self.assertEqual(response.data["results"][1]["file_name"], "test_file_3")

    def test_pagination(self):
        self.dir = Directory.objects.create(directory_name="test_directory_2", owner=self.user)
        for i in range(100):
            File.objects.create(file_name=f"test_pagination_{i}", directory=self.dir)
        response_1 = self.client.get(reverse('file'), {"directory_id": self.dir.id})
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_1.data["count"], 100)
        self.assertEqual(len(response_1.data["results"]), 24)
        response_2 = self.client.get(reverse('file'), {"directory_id": self.dir.id, "page": 5})
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_2.data["count"], 100)
        self.assertEqual(len(response_2.data["results"]), 4)