from django.test import TestCase, Client
from django.urls import reverse
import json
from django.contrib.auth.models import User

from .models import Directory, File, UserProfile
from .imageFunc import create_test_image, delete_test_image

# Create your tests here.

class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(username="test_user", password="12345678")

    def test_sign_up_success(self):
        response = self.client.post(reverse('sign_up'),
        data=json.dumps({"username": "user", "password": "12345678"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sign_up"], True)
        self.assertEqual(User.objects.filter(username="user").count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertIn("_auth_user_id", self.client.session)

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
        self.assertEqual(response.json()["login"], True)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn("_auth_user_id", self.client.session)

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
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", password="12345678")
        self.profile = UserProfile.objects.create(user=self.user, image_profile="ProfileImages/test.jpg")
        self.directory = Directory.objects.create(owner=self.user, directory_name="test_directory")
        self.file = File.objects.create(img="Images/test.jpg", file_name="test_file", directory=self.directory)


    def test_home_get_method(self):
        self.client.force_login(self.user)
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

        self.assertEqual(data["files"][0]["id"], 1)
        self.assertEqual(data["files"][0]["img"], "/Images/test.jpg")
        self.assertEqual(data["files"][0]["file_name"], "test_file")
        self.assertEqual(data["files"][0]["directory"], 1)
        self.assertEqual(File.objects.count(), 1)

    def test_home_create_directory(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('directory'),
        data=json.dumps({"directory_name": "test_directory_2"}), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["directory_name"], "test_directory_2")
        self.assertEqual(Directory.objects.count(), 2)
        self.assertEqual(Directory.objects.filter(directory_name="test_directory_2").count(), 1)
        self.assertEqual(Directory.objects.filter(owner=1).count(), 2)

    def test_home_create_file(self):
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
        response = self.client.patch(reverse('file'),
        data = json.dumps({"file_name": "new_test_file", "id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(File.objects.filter(file_name="new_test_file").count(), 1)
        self.assertEqual(File.objects.count(), 1)

    def test_home_wrong_update_file(self):
        self.client.force_login(self.user)
        response = self.client.patch(reverse('file'),
        data = json.dumps({"file_name": "new_test_file", "id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(File.objects.filter(file_name="test_file").count(), 1)
        self.assertEqual(File.objects.count(), 1)

    def test_home_delete_directory(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse('directory'),
        data = json.dumps({"id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["delete"], True)
        self.assertEqual(Directory.objects.count(), 0)

    def test_home_wrong_delete_directory(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse('directory'),
        data = json.dumps({"id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Directory.objects.filter(directory_name="test_directory").count(), 1)
        self.assertEqual(Directory.objects.count(), 1)

    def test_home_delete_file(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse('file'),
        data = json.dumps({"id": 1}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["delete"], True)
        self.assertEqual(File.objects.count(), 0)

    def test_home_wrong_delete_file(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse('file'),
        data = json.dumps({"id": 792}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(File.objects.filter(file_name="test_file").count(), 1)
        self.assertEqual(File.objects.count(), 1)

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["logout"], True)
        self.assertNotIn("_auth_user_id", self.client.session)