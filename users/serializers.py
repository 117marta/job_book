from rest_framework import serializers

from users.models import User


class UsersSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    trades = serializers.StringRelatedField(many=True, read_only=True)
    role = serializers.CharField(source="get_role_display")

    class Meta:
        model = User
        fields = (
            "date_joined",
            "is_active",
            "is_admin",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "trades",
            "birth_date",
            "avatar",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}
