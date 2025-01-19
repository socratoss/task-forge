from dj_rest_auth.views import UserDetailsView as BaseUserDetailsView
from rest_framework.parsers import JSONParser, MultiPartParser


class UserDetailView(BaseUserDetailsView):
    parser_classes = [JSONParser, MultiPartParser]