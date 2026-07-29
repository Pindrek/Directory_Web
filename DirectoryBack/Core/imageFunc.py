from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_image(
    file_name = "test_2.jpg",
    size = (100, 100),
    color = "red",
    image_format = "JPEG",
):
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    buffer.seek(0)
    return SimpleUploadedFile(
        name=file_name,
        content=buffer.read(),
        content_type=f"Image/{image_format.lower()}",
    )

def delete_test_image(image_field):
    if image_field:
        image_field.delete(save=False)