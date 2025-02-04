from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import User
from users.serializers import UsersSerializer


@api_view(["GET"])
def get_users(request):
    users = User.objects.all().order_by("-pk")
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data)
