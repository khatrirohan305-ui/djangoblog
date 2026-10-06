from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Post

MAX_IMAGE_SIZE_MB = 2
ALLOWED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def validate_uploaded_image(image):
    """Check size and extension, only for newly uploaded files."""
    if not isinstance(image, UploadedFile):
        return image  # nothing uploaded, or an existing/cleared image

    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise forms.ValidationError(f"Image must be smaller than {MAX_IMAGE_SIZE_MB} MB.")

    if not image.name.lower().endswith(ALLOWED_IMAGE_EXTENSIONS):
        raise forms.ValidationError("Only JPG, PNG, GIF or WEBP images are allowed.")

    return image


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "tags", "status", "cover_image", "image"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # field-level validation
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        return title

    def clean_cover_image(self):
        return validate_uploaded_image(self.cleaned_data.get("cover_image"))

    def clean_image(self):
        return validate_uploaded_image(self.cleaned_data.get("image"))

    # form-level validation (compares more than one field)
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        content = cleaned_data.get("content")
        if title and content and title.lower() in content.lower()[:50]:
            raise forms.ValidationError("Don't repeat the title verbatim at the start of the content.")
        return cleaned_data