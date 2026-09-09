from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrPhoneBackend(ModelBackend):
    """Authenticate active users by email or, when present, by phone."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get("email") or kwargs.get("telefono")
        if identifier is None or password is None:
            return None

        identifier = str(identifier).strip()
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(
                Q(email__iexact=identifier) | Q(telefono=identifier)
            )
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
