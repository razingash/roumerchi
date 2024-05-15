from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from tests.models import CustomUser, Test, TestCriterion, TestUniqueResult


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


class CreateTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['category', 'preview', 'description']
        widgets = {
            'preview': forms.TextInput(attrs={'cols': 60, 'rows': 1, 'class': 'form__input', 'placeholder': 'at least 40 symbols'}),
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form__textarea',
                                                 'placeholder': 'at least 500 symbols'})
        }


class CreateTestCriterionForm(forms.ModelForm):
    class Meta:
        model = TestCriterion
        fields = ['criterion', 'result']
        widgets = {
            'criterion': forms.TextInput(attrs={'cols': 60, 'rows': 1, 'class': 'form__input', 'maxlength': 25,
                                                'minlength': 3, 'placeholder': 'from 3 to 25 symbols'}),
            'result': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form__textarea', 'placeholder': 'at least 100 symbols'})
        }


class CreateTestUniqueResultForm(forms.ModelForm):
    class Meta:
        model = TestUniqueResult
        fields = ['points_min', 'points_max', 'result']
        widgets = {
            'points_min': forms.NumberInput(attrs={'max': 32767, 'cols': 40, 'rows': 1, 'class': 'form__input'}),
            'points_max': forms.NumberInput(attrs={'max': 32767, 'cols': 40, 'rows': 1, 'class': 'form__input'}),
            'result': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form__textarea'})
        }

CriterionFormSet = forms.inlineformset_factory(Test, TestCriterion, form=CreateTestCriterionForm, extra=1)

unique_result_forms = forms.inlineformset_factory(Test, TestUniqueResult, form=CreateTestUniqueResultForm, extra=1)
