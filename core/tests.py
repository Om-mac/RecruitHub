from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .forms import UserProfileForm


class FileAccessFailure:
    """Simulate a storage-backed file whose .size raises an exception (e.g., missing S3 object)"""
    def __init__(self, name):
        self.name = name

    @property
    def size(self):
        raise Exception('Simulated storage access failure')


class FileValidatorTests(TestCase):
    def test_clean_profile_photo_missing_stored_file_raises_validation_error(self):
        user = User.objects.create_user(username='testuser', password='test')
        profile = user.profile
        form = UserProfileForm(instance=profile)
        # Simulate that the cleaned_data contains a stored file that errors on size access
        form.cleaned_data = {'profile_photo': FileAccessFailure('avatar.jpg')}
        with self.assertRaises(ValidationError):
            form.clean_profile_photo()

    def test_clean_profile_photo_with_fresh_upload_passes(self):
        user = User.objects.create_user(username='testuser2', password='test')
        profile = user.profile
        form = UserProfileForm(instance=profile)
        jpeg_content = b'\xff\xd8\xff\x00dummyjpeg'
        upload = SimpleUploadedFile('avatar.jpg', jpeg_content, content_type='image/jpeg')
        form.cleaned_data = {'profile_photo': upload}
        # Should not raise
        result = form.clean_profile_photo()
        self.assertIs(result, upload)

    def test_generate_presigned_url_access_denied_returns_none(self):
        """Simulate S3 ClientError AccessDenied and ensure helper returns None"""
        from botocore.exceptions import ClientError
        # Monkeypatch get_s3_client to return a fake client that raises AccessDenied
        import core.s3_utils as s3u

        class FakeClient:
            def generate_presigned_url(self, *args, **kwargs):
                raise ClientError({'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}}, 'GetObject')

        orig_get = s3u.get_s3_client
        try:
            s3u.get_s3_client = lambda: FakeClient()
            url = s3u.generate_presigned_url('resumes/1/some.pdf', expiration=60)
            self.assertIsNone(url)
        finally:
            s3u.get_s3_client = orig_get
