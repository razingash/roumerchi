from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from tests.models import CustomUser, Test, TestCriterion, TestUniqueResult, QuestionAnswerChoice, TestQuestion


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


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['category', 'preview', 'description']
        widgets = {
            'preview': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'at least 10 symbols'}),
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


TestQuestionFormSet = forms.inlineformset_factory(Test, TestQuestion, form=TestQuestionForm, extra=0)
TestQuestionAnswersFormSet = forms.inlineformset_factory(TestQuestion, QuestionAnswerChoice, form=TestQuestionAnswersForm, extra=0)


TestQuestionAnswersCreateFormSet = forms.inlineformset_factory(TestQuestion, QuestionAnswerChoice, form=TestQuestionAnswersForm, extra=0)

