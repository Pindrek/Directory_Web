from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from .validators import validator_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image_profile = models.ImageField(upload_to='ProfileImages/', blank=True, max_length=256)

    class Meta:
        indexes = [
            models.Index(fields=['image_profile'], name='user_profile_images')
        ]
        ordering = ['user']

    def __str__(self):
        return f"profile_name: {self.user.username} | Image: {str(self.image_profile)}"

class Directory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='directories')
    directory_name = models.CharField(max_length=256, validators=[validator_name])
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['directory_name'], name='directory_name'),
            models.Index(fields=['created_at'], name='directory_created'),
        ]
        ordering = ['owner', 'directory_name']
        unique_together = ['owner', 'directory_name']

    def __str__(self):
        local_time = timezone.localtime(self.created_at)
        formatted_date = local_time.strftime("%Y.%m.%d %H:%M:%S")
        return f"Owner: {self.owner} | Name: {self.directory_name} | dir_Date:  {formatted_date}"


class File(models.Model):
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name='files')
    img = models.ImageField(upload_to='Images/', max_length=256)
    file_name = models.CharField(max_length=128, validators=[validator_name])
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['file_name'], name='file_name'),
            models.Index(fields=['date'], name='file_date'),
        ]
        ordering = ['directory', 'file_name']
        unique_together = ['directory', 'file_name']

    def __str__(self):
        local_time = timezone.localtime(self.date)
        formatted_date = local_time.strftime("%Y.%m.%d %H:%M:%S")
        return f"Name: {self.file_name} | Image: {str(self.img)} | file_Date: {formatted_date} | Directory: {str(self.directory)}"