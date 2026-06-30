"""Create MinIO/S3 bucket if missing (for evidence, exports)."""
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = "Ensure the default storage bucket exists (MinIO/S3)."

    def handle(self, *args, **options):
        try:
            conn = default_storage.connection
            bucket_name = default_storage.bucket_name
            try:
                conn.head_bucket(Bucket=bucket_name)
                self.stdout.write("Bucket %s already exists." % bucket_name)
            except ClientError as e:
                if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                    conn.create_bucket(Bucket=bucket_name)
                    self.stdout.write(self.style.SUCCESS("Bucket %s created." % bucket_name))
                else:
                    raise
        except Exception as e:
            self.stdout.write(self.style.WARNING("Bucket check/skip: %s" % e))
