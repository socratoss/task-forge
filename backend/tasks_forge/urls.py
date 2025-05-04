from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from allauth.account.views import ConfirmEmailView, EmailVerificationSentView
from dj_rest_auth.registration.views import (
    RegisterView,
    ResendEmailVerificationView,
)
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)


# Authentication URLs (unchanged)
auth_patterns = [
    path("login/", csrf_exempt(LoginView.as_view()), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="rest_password_change"),
    path("signup/", RegisterView.as_view(), name="rest_register"),
    path(
        "signup/account-confirm-email/<str:key>/",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "signup/confirm-email/",
        EmailVerificationSentView.as_view(),
        name="email_verification_sent",
    ),
    path(
        "signup/resend-email/",
        ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
]


# Main API patterns
api_patterns = [
    path("authentication/", include(auth_patterns)),
    path("user/", include("user.urls")), # User profile etc.
    path("project/", include("project.urls")), # Project list/details/users

    # --- Include Task URLs under Projects ---
    # This makes task URLs project-specific, e.g., /api/project/123/tasks/
    path("project/<int:project_id>/tasks/", include("task.urls")),
]


# Main URL Configuration
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_patterns)), # Include all API endpoints under /api/
]


# Serve media files during development (unchanged)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
