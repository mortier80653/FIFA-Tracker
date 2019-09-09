from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)
    is_active = serializers.BooleanField(required=False, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Username {} is already taken.".format(value),
                code='unique'
            )
        return value

    def validate_email(self, value):
        if "@gmail.com" in value:
            value = value.replace(".", "")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "There is already an account with this email: {}".format(value),
                code='unique'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.is_active = False
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_active')
