from pathlib import Path
from unittest.mock import patch

from django import forms
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TransactionTestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.management import call_command
from django.contrib.messages import get_messages

from teams.models import OdooProfile

from awg.models import CalculatorTemplate

from core.models import (
    OdooProfile as CoreOdooProfile,
    ReleaseManager as CoreReleaseManager,
    AssistantProfile as CoreAssistantProfile,
    Todo,
)
from core.user_data import dump_user_fixture, load_user_fixtures


class UserDataAdminTests(TransactionTestCase):
    def setUp(self):
        call_command("flush", verbosity=0, interactive=False)
        User = get_user_model()
        self.user = User.objects.create_superuser("udadmin", password="pw")
        self.client.login(username="udadmin", password="pw")
        data_root = Path(self.user.data_path or Path(settings.BASE_DIR) / "data")
        data_root.mkdir(exist_ok=True)
        user_dir = data_root / self.user.username
        user_dir.mkdir(exist_ok=True)
        for f in user_dir.glob("*.json"):
            f.unlink()
        self.data_root = data_root
        self.data_dir = user_dir
        self.profile = OdooProfile.objects.create(
            user=self.user,
            host="http://test",
            database="db",
            username="odoo",
            password="secret",
        )
        self.fixture_path = self.data_dir / f"core_odooprofile_{self.profile.pk}.json"

    def tearDown(self):
        for path in self.data_dir.glob("*.json"):
            path.unlink(missing_ok=True)
        call_command("flush", verbosity=0, interactive=False)

    def test_userdatum_checkbox(self):
        url = reverse("admin:teams_odooprofile_change", args=[self.profile.pk])
        response = self.client.get(url)
        self.assertContains(response, 'name="_user_datum"')

    def test_user_change_view_hides_user_datum_checkbox(self):
        UserModel = get_user_model()
        admin_model = None
        for model in admin.site._registry:
            if model._meta.concrete_model is UserModel:
                admin_model = model
                break
        self.assertIsNotNone(admin_model)
        url = reverse(
            f"admin:{admin_model._meta.app_label}_{admin_model._meta.model_name}_change",
            args=[self.user.pk],
        )
        response = self.client.get(url)
        self.assertNotContains(response, 'name="_user_datum"')

    def test_save_user_datum_creates_fixture(self):
        url = reverse("admin:teams_odooprofile_change", args=[self.profile.pk])
        data = {
            "user": self.user.pk,
            "host": "http://test",
            "database": "db",
            "username": "odoo",
            "password": "",
            "_user_datum": "on",
            "_save": "Save",
        }
        response = self.client.post(url, data, follow=True)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_user_data)
        self.assertTrue(self.fixture_path.exists())
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any(str(self.fixture_path) in msg for msg in messages))

    def test_unchecking_removes_fixture(self):
        self.profile.is_user_data = True
        self.profile.save()
        url = reverse("admin:teams_odooprofile_change", args=[self.profile.pk])
        data = {
            "user": self.user.pk,
            "host": "http://test",
            "database": "db",
            "username": "odoo",
            "password": "",
            "_save": "Save",
        }
        self.client.post(url, data)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_user_data)
        self.assertFalse(self.fixture_path.exists())

    def test_user_user_data_fixture_includes_profiles(self):
        release_manager = CoreReleaseManager.objects.create(user=self.user)
        chat_profile, _ = CoreAssistantProfile.issue_key(self.user)
        core_profile = CoreOdooProfile.objects.get(pk=self.profile.pk)
        UserModel = get_user_model()
        admin_model = None
        user_admin = None
        for model, admin_instance in admin.site._registry.items():
            if model._meta.concrete_model is UserModel:
                admin_model = model
                user_admin = admin_instance
                break
        self.assertIsNotNone(user_admin)
        admin_user = admin_model.objects.get(pk=self.user.pk)
        rf = RequestFactory()
        request = rf.post("/", {})
        request.user = self.user
        request.session = self.client.session
        setattr(request, "_messages", FallbackStorage(request))

        class SimpleUserForm(forms.ModelForm):
            class Meta:
                model = admin_model
                fields = ["username"]

        form = SimpleUserForm({"username": admin_user.username}, instance=admin_user)
        self.assertTrue(form.is_valid())

        user_admin.save_model(request, admin_user, form, True)

        class DummyInlineForm:
            def __init__(self, instance, cleaned_data):
                self.instance = instance
                self.cleaned_data = cleaned_data

        class DummyFormset:
            def __init__(self, forms):
                self.forms = forms
                self.deleted_objects = []

            def save(self):
                return self.forms

        def run_formset(instance):
            formset = DummyFormset(
                [DummyInlineForm(instance, {"user_datum": True, "DELETE": False})]
            )
            user_admin.save_formset(request, form, formset, True)

        run_formset(core_profile)
        run_formset(release_manager)
        run_formset(chat_profile)

        expected_paths = [
            self.data_dir / f"core_odooprofile_{core_profile.pk}.json",
            self.data_dir / f"core_releasemanager_{release_manager.pk}.json",
            self.data_dir / f"core_assistantprofile_{chat_profile.pk}.json",
        ]
        for path in expected_paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists())

        user_fixture = self.data_dir / f"core_user_{self.user.pk}.json"
        self.assertFalse(user_fixture.exists())

        core_user = UserModel.objects.get(pk=self.user.pk)
        profile_instances = [core_profile, release_manager, chat_profile]
        for instance in [core_user] + profile_instances:
            with self.subTest(instance=instance._meta.label_lower):
                type(instance).all_objects.filter(pk=instance.pk).update(
                    is_user_data=False
                )
                instance.refresh_from_db()
                self.assertFalse(instance.is_user_data)

        load_user_fixtures(self.user)

        for instance in profile_instances:
            with self.subTest(reloaded=instance._meta.label_lower):
                instance.refresh_from_db()
                self.assertTrue(instance.is_user_data)

        core_user.refresh_from_db()
        self.assertFalse(core_user.is_user_data)

    def test_load_user_fixture_marks_user_data_flag(self):
        core_profile = CoreOdooProfile.objects.get(pk=self.profile.pk)
        todo = Todo.objects.create(request="Test TODO")
        calculator = CalculatorTemplate.objects.create(name="Test Template")

        for instance in (core_profile, todo, calculator):
            with self.subTest(model=instance._meta.label_lower):
                path = self.data_dir / (
                    f"{instance._meta.app_label}_{instance._meta.model_name}_{instance.pk}.json"
                )
                type(instance).all_objects.filter(pk=instance.pk).update(
                    is_user_data=True
                )
                instance.refresh_from_db()
                dump_user_fixture(instance, self.user)
                self.assertTrue(path.exists())
                type(instance).all_objects.filter(pk=instance.pk).update(
                    is_user_data=False
                )
                instance.refresh_from_db()
                self.assertFalse(instance.is_user_data)
                load_user_fixtures(self.user)
                instance.refresh_from_db()
                self.assertTrue(instance.is_user_data)

    def test_load_user_fixture_skips_empty_files(self):
        empty = self.data_dir / "core_todo_1.json"
        empty.write_text("[]", encoding="utf-8")

        with patch("core.user_data.call_command") as mock_call:
            load_user_fixtures(self.user)

        self.assertFalse(empty.exists())
        mock_call.assert_not_called()
