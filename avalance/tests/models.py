from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models

from uuid import uuid4

from django.db.models import UniqueConstraint
from django.urls import reverse
from django.utils.text import slugify


class TestComplaints(models.IntegerChoices):
    FIRST = 1, 'first'
    SECOND = 2, 'second'

class TestCategories(models.IntegerChoices):
    INTELLIGENCE = 1, 'intelligence' # bulp
    PSYCHOLOGY = 2, 'psychology' # mask of madness
    PROFESSIONAL = 3, 'professional' # briefcase
    ENTERTAINMENT = 4, 'entertainment' # roflan
    EMOTIONAL = 5, 'emotional' # heart

class TestStatuses(models.IntegerChoices):
    UNDERWAY = 1, 'underway' # in progress
    VERIFICATION = 2, 'awaiting verification'  # link unaviable, moderation forbidden
    VISIBLE = 3, 'visible' # link and walkthrough are aviable
    FREEZED = 4, 'freezed'  # link aviable, test closed moderation forbidden | author can set up this state
    INVISIBLE = 5, 'invisible' # link aviable, test moderation and walkthrough 403 | this state is setted up due to huge amount of complaint
    BANNED = 6, 'banned'  # link unaviable 404, test closed by admin

class CriterionFilters(models.IntegerChoices):
    COMPLETED = 1, 'completed'
    UNCOMPLETED = 2, 'uncompleted'

class SortingFilters(models.IntegerChoices):
    POPULARITY = 1, 'popularity'
    NEWNESS = 2, 'newness'
    AZ = 3, 'A-z'
    ZA = 4, 'Z-a'


class UserTrustFactors(models.IntegerChoices):
    FIRST = 0, 'first'
    SECOND = 2, 'second'


class CustomUser(AbstractUser):
    uuid = models.UUIDField(primary_key=False, default=uuid4, editable=False, unique=True)
    description = models.CharField(max_length=180, blank=True, null=True)
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
                                              default=TestStatuses.UNDERWAY)
    preview = models.CharField(max_length=220, blank=False, null=False, validators=[MinLengthValidator(10)])
    preview_slug = models.SlugField(blank=False, null=True, unique=True)
    description = models.TextField(max_length=5000, blank=False, null=False, validators=[MinLengthValidator(10)])#[500, 5000]
    questions_amount = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(2),
                                                                                           MaxValueValidator(150)]) # improve this#[15, 150]
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
    result = models.TextField(max_length=700, blank=False, null=False, validators=[MinLengthValidator(10)])#[100, 700]


class TestUniqueResult(models.Model): # сделать проверку для того чтобы не было несостыковок
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    points_min = models.PositiveSmallIntegerField(blank=False, null=False)
    points_max = models.PositiveSmallIntegerField(blank=False, null=False)
    result = models.TextField(max_length=700, blank=False, null=False, validators=[MinLengthValidator(10)])#[100, 700]


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


class TestQuestion(models.Model):
    question = models.CharField(max_length=110, validators=[MinLengthValidator(10)])
    test = models.ForeignKey(Test, on_delete=models.CASCADE)


class QuestionAnswerChoice(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    criterion = models.ForeignKey(TestCriterion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=110, blank=False, null=False, validators=[MinLengthValidator(2)])
    weight = models.PositiveSmallIntegerField(blank=False, null=False)


class Respondent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=True, blank=False, null=False) # false - uncompleted | true - completed


class Response(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.DO_NOTHING)
    answer = models.ForeignKey(QuestionAnswerChoice, on_delete=models.DO_NOTHING)


class RespondentResult(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE)
    result = models.ForeignKey(TestUniqueResult, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'test_respondent_result'


class Guest(models.Model):
    time_stat = models.DateTimeField(auto_now=True, blank=False, null=False)
    uuid = models.UUIDField(primary_key=False, blank=True, null=False, unique=True)

    class Meta:
        db_table = 'guest'


class GuestRespondent(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=True, blank=False, null=False) # false - uncompleted | true - completed

    class Meta:
        db_table = 'guest_respondent'


class GuestRespondentResult(models.Model):
    guest_respondent = models.ForeignKey(GuestRespondent, on_delete=models.CASCADE)
    result = models.ForeignKey(TestUniqueResult, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'guest_respondent_result'

class GuestResponse(models.Model):
    guest_respondent = models.ForeignKey(GuestRespondent, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuestionAnswerChoice, on_delete=models.CASCADE)

    class Meta:
        db_table = 'guest_response'

