from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from users.models import User
from users.serializers import UserCreateSerializer, UsersSerializer


@api_view(["GET"])
def get_users(request):
    users = User.objects.all().order_by("-pk")
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@parser_classes([JSONParser])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
