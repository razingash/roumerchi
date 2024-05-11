from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from tests.models import CustomUser


class RegisterCustomUserForm(UserCreationForm):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'input__nickname', 'placeholder': 'input username...'}))
    email = forms.EmailField(label='email', widget=forms.EmailInput(attrs={'class': 'input__mail', 'placeholder': 'input email...'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'input__password', 'placeholder': 'input password...'}))
    password2 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'input__password', 'placeholder': 'repeat password...'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class LoginCustomUserForm(AuthenticationForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'input__password',
                                                                                   'placeholder': 'input password...'}))
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'input__nickname',
                                                                               'placeholder': 'input username...'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

