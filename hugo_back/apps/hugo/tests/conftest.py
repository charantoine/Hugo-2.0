import os
from importlib.util import find_spec

# Legacy P0 is the default for unit/integration tests; opt in per module with
# @override_settings(HUGO_P0_V17_ENABLED=True). Prevents local env from flipping behaviour.
os.environ["HUGO_P0_V17_ENABLED"] = "false"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
HAS_PYTEST_DJANGO = find_spec("pytest_django") is not None

if not HAS_PYTEST_DJANGO:
    import django

    django.setup()

import pytest
from django.core.management import call_command
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)
from rest_framework.test import APIClient

from apps.accounts.models import Organisation, Role, User
from apps.referentials.models import Group


@pytest.fixture
def organisation(db):
    return Organisation.objects.create(name="Org Hugo")


@pytest.fixture
def group(db, organisation):
    return Group.objects.create(organisation=organisation, name="Groupe Hugo")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def learner_user(db, organisation):
    return User.objects.create_user(
        username="learner_fixture",
        password="pass",
        organisation=organisation,
        role=Role.LEARNER,
    )


@pytest.fixture
def morning_reconf_baseline_b(db):
    """Fixture complète reconfiguration chats tuteur/formateur — baseline B."""
    from apps.hugo.tests.morning_reconf_fixtures import build_morning_reconf_baseline_b

    return build_morning_reconf_baseline_b()


if not HAS_PYTEST_DJANGO:
    @pytest.fixture
    def django_user_model():
        return User


    @pytest.fixture(scope="session", autouse=True)
    def django_test_environment():
        setup_test_environment()
        db_config = setup_databases(verbosity=0, interactive=False)
        yield
        teardown_databases(db_config, verbosity=0)
        teardown_test_environment()


    @pytest.fixture
    def db():
        call_command("flush", verbosity=0, interactive=False)
