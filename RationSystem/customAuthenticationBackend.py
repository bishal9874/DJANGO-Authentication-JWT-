from django.contrib.auth.backends import BaseBackend
from .models import RationUser
from django.db.models import Q
class RationUserAuthenticationBackend(BaseBackend):
    def authenticate(self, request, email=None, rationId=None, password=None, **kwargs):
        try:
            user = RationUser.objects.get(Q(email=email) and Q(rationId=rationId))
            print(user)
            if user.check_password(password):
                return user
        except RationUser.DoesNotExist:
            return None
