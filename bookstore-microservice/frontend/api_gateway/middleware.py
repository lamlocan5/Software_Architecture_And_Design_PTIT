import jwt
from django.contrib.auth.models import AnonymousUser

class SimpleProfile:
    def __init__(self, customer_id):
        self.customer_id = customer_id

class MockGroups:
    def __init__(self, role):
        self.role = role

    def filter(self, name):
        class MockResult:
            def __init__(self, exists_bool):
                self._exists = exists_bool
            def exists(self):
                return self._exists
        return MockResult(self.role == name)

class SimpleUser:
    def __init__(self, token_data):
        self.id = token_data.get('user_id') or token_data.get('id')
        self.username = token_data.get('username') or token_data.get('email')
        self.email = token_data.get('email')
        self.first_name = token_data.get('name') or self.username
        self.is_active = True
        self.role = token_data.get('role', 'customer')
        self.is_superuser = token_data.get('is_superuser') or (self.role == 'admin')
        self.profile = SimpleProfile(token_data.get('profile_id'))
        self.groups = MockGroups(self.role)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return self.is_superuser or (self.role in ['staff', 'manager', 'admin'])

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = AnonymousUser()
        
        user_id = request.META.get('HTTP_X_USER_ID')
        if user_id:
            try:
                request.user = SimpleUser({
                    'id': int(user_id),
                    'username': request.META.get('HTTP_X_USER_USERNAME') or request.META.get('HTTP_X_USER_EMAIL'),
                    'email': request.META.get('HTTP_X_USER_EMAIL'),
                    'role': request.META.get('HTTP_X_USER_ROLE', 'customer'),
                    'profile_id': int(request.META.get('HTTP_X_USER_PROFILE_ID')) if request.META.get('HTTP_X_USER_PROFILE_ID') else None,
                    'is_superuser': request.META.get('HTTP_X_USER_SUPERUSER') == '1'
                })
            except Exception:
                pass
        else:
            token = request.session.get('access_token') or request.COOKIES.get('access_token')
            if token:
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    request.user = SimpleUser(payload)
                except Exception:
                    pass
        return self.get_response(request)
