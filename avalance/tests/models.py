from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models

from uuid import uuid4
import re

from django.db.models import UniqueConstraint
from django.urls import reverse
from django.utils.text import slugify


class TestComplaints(models.IntegerChoices):
    FIRST = 1, 'first'
    SECOND = 2, 'second'

class TestCategories(models.IntegerChoices):
    FIRST = 1, 'first'
    SECOND = 2, 'second'

class TestStatuses(models.IntegerChoices):
    VISIBLE = 1, 'visible'
    CHECKING = 2, 'awaiting verification' # link aviable, test temporarily closed
    FREEZED = 3, 'freezed' # link aviable, test closed / author can set up this state
    BANNED = 4, 'banned' # link aviable, test closed

class UserTrustFactors(models.IntegerChoices):
    FIRST = 0, 'first'
    SECOND = 2, 'second'

def user_avatar_upload(instance, filename):
    filename = 'avatar' + re.search(r'\.(.*)', filename)[0]
    return f'user/{instance.pk}/avatar/{filename}'

def validate_file_size(value):
    max_size = 2 * 512 * 512
    if value.size > max_size:
        raise ValidationError(f'Maximum file size mustn\'t exceed {max_size} bytes.')

def validate_image_size(image):
    required_width = 512
    required_height = 512
    img = Image.open(image)
    (width, height) = img.size
    if width > required_width or height > required_height:
        raise ValidationError(f'Image mustn\'t be more {required_width}x{required_height} pixels.')
    if width != height:
        raise ValidationError('Image must be square')


class CustomUser(AbstractUser):
    uuid = models.UUIDField(primary_key=False, default=uuid4, editable=False, unique=True)
    description = models.CharField(max_length=180, blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_upload, null=True, blank=True,
                               validators=[validate_file_size, validate_image_size,
                                           FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    trust_factor = models.PositiveSmallIntegerField(choices=UserTrustFactors.choices, blank=False, null=False,
                                                    default=UserTrustFactors.FIRST)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'profile_uuid': self.uuid})

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'custom_user'
        constraints = [
            UniqueConstraint(fields=['username'], name='unique_customuser_username'),
            UniqueConstraint(fields=['email'], name='unique_customuser_email')
        ]


class Test(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    category = models.PositiveSmallIntegerField(choices=TestCategories.choices, blank=False, null=False)
    status = models.PositiveSmallIntegerField(choices=TestStatuses.choices, blank=False, null=False,
                                              default=TestStatuses.CHECKING)
    preview = models.CharField(max_length=220, blank=False, null=False, validators=[MinLengthValidator(40)])
    preview_slug = models.SlugField(blank=False, null=True, unique=True)
    description = models.TextField(max_length=5000, blank=False, null=False, validators=[MinLengthValidator(500)])
    questions_amount = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(15),
                                                                                           MaxValueValidator(150)]) # improve this
    grade = models.SmallIntegerField(default=0, blank=False, null=False)
    reputation = models.SmallIntegerField(default=50, blank=False, null=False)
    publication_date = models.DateTimeField(auto_now=True, blank=False, null=False)
    change_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def clean(self):
        if self._state.adding:
            self.preview_slug = slugify(self.preview)
            super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('test', kwargs={'test_preview': self.preview_slug})


class TestCriterion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    criterion = models.CharField(max_length=25, blank=False, null=False, validators=[MinLengthValidator(3)])
    result = models.TextField(max_length=700, blank=False, null=False, validators=[MinLengthValidator(100)])


class TestUniqueResult(models.Model): # сделать проверку для того чтобы не было несостыковок
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    points_min = models.PositiveSmallIntegerField(blank=False, null=False)
    points_max = models.PositiveSmallIntegerField(blank=False, null=False)
    result = models.TextField(max_length=700, blank=False, null=False, validators=[MinLengthValidator(100)])


class Complaint(models.Model):
    cause = models.PositiveSmallIntegerField(choices=TestComplaints.choices, blank=False, null=False)
    weight = models.PositiveSmallIntegerField(blank=False, null=False)


class TestComplaint(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    complaint = models.ForeignKey(Complaint, on_delete=models.DO_NOTHING)
    test = models.ForeignKey(Test, on_delete=models.DO_NOTHING)


class Grade(models.Model):
    grade = models.BooleanField(blank=False, null=False)


class TestGrade(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)


class Question(models.Model):
    question = models.CharField(max_length=110, validators=[MinLengthValidator(10)])


class TestQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class QuestionAnswerChoice(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    criterion = models.ForeignKey(TestCriterion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=110, blank=False, null=False)
    weight = models.PositiveSmallIntegerField(blank=False, null=False)


class Respondent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)


class Response(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    answer = models.ForeignKey(QuestionAnswerChoice, on_delete=models.DO_NOTHING)


class RespondentResult(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE)
    result = models.ForeignKey(TestUniqueResult, on_delete=models.CASCADE)
