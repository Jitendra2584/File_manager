from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def authenticated_user_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated,
        login_url='login'
    )(view_func)
    return decorated_view_func