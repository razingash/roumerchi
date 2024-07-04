from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _

from tests.models import CustomUser, Test, TestCriterion, TestUniqueResult, QuestionAnswerChoice, TestQuestion, \
    Notification

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.EmailInput(attrs={"autocomplete": "email", 'class': 'form_input', 'placeholder': 'input email...'}))


class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form_input', 'placeholder': 'input password...'}))
    new_password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'class': 'form_input', 'placeholder': 'repeat password...'}))


class RegisterCustomUserForm(UserCreationForm):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'auth-form-input input__nickname', 'placeholder': 'input username...'}))
    email = forms.EmailField(label='email', widget=forms.EmailInput(attrs={'class': 'auth-form-input input__mail', 'placeholder': 'input email...'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'auth-form-input input__password', 'placeholder': 'input password...'}))
    password2 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'auth-form-input input__password', 'placeholder': 'repeat password...'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class LoginCustomUserForm(AuthenticationForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'auth-form-input input__password',
                                                                                   'placeholder': 'input password...'}))
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'auth-form-input input__nickname',
                                                                               'placeholder': 'input username...'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class ChangeCustomUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'description']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form_input'}),
            'description': forms.TextInput(attrs={'class': 'form_input'})
        }


class ChangeCustomUserPasswordForm(SetPasswordForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form_input'}))
    new_password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'class': 'form_input'}))

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match1.")
        user = self.user
        if not user.check_password(old_password):
            raise forms.ValidationError("Your old password was entered incorrectly.")
        return cleaned_data

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password1', 'new_password2']
        widgets = {
            'old_password': forms.PasswordInput(attrs={'class': 'form_input'}),
            'new_password1': forms.PasswordInput(attrs={'class': 'form_input'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form_input'})
        }



class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['category', 'show_criterions_description', 'preview', 'description']
        widgets = {
            'preview': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'at least 10 symbols'}),
            'show_criterions_description': forms.CheckboxInput(attrs={'class': 'form__input', 'placeholder': 'at least 10 symbols'}),
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form__textarea',
                                                 'placeholder': 'at least 500 symbols'})
        }


class TestCriterionForm(forms.ModelForm):
    class Meta:
        model = TestCriterion
        fields = ['criterion', 'result']
        widgets = {
            'criterion': forms.TextInput(attrs={'class': 'form__input', 'maxlength': 25, 'minlength': 3,
                                                'placeholder': 'from 3 to 25 symbols'}),
            'result': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form__textarea', 'placeholder': 'at least 100 symbols'})
        }


class TestUniqueResultForm(forms.ModelForm):
    class Meta:
        model = TestUniqueResult
        fields = ['points_min', 'points_max', 'result']
        widgets = {
            'points_min': forms.NumberInput(attrs={'max': 32767, 'cols': 40, 'rows': 1, 'class': 'form__input'}),
            'points_max': forms.NumberInput(attrs={'max': 32767, 'cols': 40, 'rows': 1, 'class': 'form__input'}),
            'result': forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class': 'form__textarea', 'placeholder': 'at least 100 symbols'})
        }

CriterionFormSet = forms.inlineformset_factory(Test, TestCriterion, form=TestCriterionForm, extra=2)
UniqueResultFormSet = forms.inlineformset_factory(Test, TestUniqueResult, form=TestUniqueResultForm, extra=2)

TestCriterionFormSet = forms.inlineformset_factory(Test, TestCriterion, form=TestCriterionForm, extra=0)
TestUniqueResultFormSet = forms.inlineformset_factory(Test, TestUniqueResult, form=TestUniqueResultForm, extra=0)


class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = TestQuestion
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'cols': 60, 'rows': 4, 'class': 'form__textarea', 'placeholder': 'at least 10 symbols'})
        }


class TestQuestionAnswersForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswerChoice
        fields = ['id', 'answer', 'weight']
        widgets = {
            'answer': forms.Textarea(attrs={'cols': 60, 'rows': 3, 'class': 'form__textarea', 'placeholder': 'at least 2 symbols'}),
            'weight': forms.NumberInput(attrs={'max': 32767, 'cols': 40, 'rows': 1, 'class': 'form__input'})
        }


TestQuestionFormSet = forms.inlineformset_factory(Test, TestQuestion, form=TestQuestionForm, extra=0, can_delete=False)
TestQuestionAnswersFormSet = forms.inlineformset_factory(TestQuestion, QuestionAnswerChoice, form=TestQuestionAnswersForm, extra=0, can_delete=False)


TestQuestionAnswersCreateFormSet = forms.inlineformset_factory(TestQuestion, QuestionAnswerChoice, form=TestQuestionAnswersForm, extra=0, can_delete=False)


class NofiticationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['type', 'content']
        widgets = {
            'type': forms.Select(attrs={'class': 'form__select'}),
            'content': forms.Textarea(attrs={'cols': 30, 'rows': 6, 'class': 'form__textarea', 'placeholder': 'at least 10 symbols'}),
        }
