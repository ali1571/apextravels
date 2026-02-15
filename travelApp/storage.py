# fleet/storage.py (or yourapp/storage.py)
from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client
from io import BytesIO
import mimetypes


class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET_NAME

    def _save(self, name, content):
        """Upload file to Supabase"""
        file_content = content.read()

        # Detect content type
        content_type = content.content_type if hasattr(content, 'content_type') else mimetypes.guess_type(name)[0]

        # Upload to Supabase storage
        self.client.storage.from_(self.bucket_name).upload(
            path=name,
            file=file_content,
            file_options={"content-type": content_type or "application/octet-stream"}
        )
        return name

    def _open(self, name, mode='rb'):
        """Download file from Supabase"""
        response = self.client.storage.from_(self.bucket_name).download(name)
        return BytesIO(response)

    def exists(self, name):
        """Check if file exists in Supabase"""
        try:
            self.client.storage.from_(self.bucket_name).download(name)
            return True
        except:
            return False

    def url(self, name):
        """Get public URL for the file"""
        # This is the key method - returns Supabase URL
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{name}"

    def delete(self, name):
        """Delete file from Supabase"""
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except:
            pass

    def size(self, name):
        """Get file size"""
        try:
            response = self.client.storage.from_(self.bucket_name).download(name)
            return len(response)
        except:
            return 0