from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            try:
                user_get = User.objects.get(username=username)
            except:
                raise forms.ValidationError("Sorry, account {} doesn't exists in our database. Please try again.".format(username))

            if not user_get.is_active:
                raise forms.ValidationError("Sorry, your account is not activated. Check spam folder in your email inbox.")
            else:
                raise forms.ValidationError("Sorry, invalid password. Please try again.")

        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=255, required=False,)
    email = forms.EmailField(max_length=254, required=False, widget=forms.EmailInput())

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if not username and not email:
            raise forms.ValidationError("Please, enter your email or username and try again.")

        if not email:
            try:
                User.objects.get(username=username)
            except:
                raise forms.ValidationError("Sorry, account '{}' doesn't exists in our database. Please try again.".format(username))
        else:
            try:
                User.objects.get(email=email)
            except:
                raise forms.ValidationError("Sorry, account with '{}' email address doesn't exists in our database. Please try again.".format(email))
        return self.cleaned_data

    def get_user(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        user = User.objects.filter(Q(email=email)|Q(username=username))[0]
        return user

class SetNewPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2