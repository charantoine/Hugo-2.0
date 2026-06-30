from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_usermanager_bootstrap"),
    ]

    # NOTE:
    # This migration is intentionally a no-op at the SQL level for the app DB user,
    # because altering RLS policies requires being the table owner. RLS behaviour
    # for bootstrap/admin login is instead handled in app_core.middleware.TenantRLSMiddleware.
    operations = []

