import uuid

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('multiplechoice', "Multiple Choice"),
        ('truefalse', "True/False"),
        ('freetext', "Freeform Input")
    )
    """
    Base Question model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.IntegerField(default=1)
    question_type = models.CharField(max_length=50,
                                     choices=QUESTION_TYPE_CHOICES)
    question = models.CharField(max_length=200)
    answers = JSONField(null=True, blank=True)
    response_correct = models.CharField(max_length=200)
    response_incorrect = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='questions_created',
                                   null=True)
    updated_by = models.ForeignKey(User, related_name='questions_updated',
                                   null=True)
    user = property(lambda self: self.created_by)

    def serialize_hook(self, hook):
        # optional, there are serialization defaults
        # we recommend always sending the Hook
        # metadata along for the ride as well
        return {
            'hook': hook.dict(),
            'data': {
                'id': str(self.id),
                'version': self.version,
                'question_type': self.question_type,
                'question': self.question,
                'answers': self.answers,
                'response_correct': self.response_correct,
                'response_incorrect': self.response_incorrect,
                'active': self.active,
                'created_at': self.created_at.isoformat(),
                'created_by': self.created_by.username,
                'updated_at': self.updated_at.isoformat(),
                'updated_by': self.updated_by.username
            }
        }

    def __str__(self):  # __unicode__ on Python 2
        return str(self.id)


@python_2_unicode_compatible
class Quiz(models.Model):

    """
    Base Quiz model, does not hold questions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    metadata = JSONField(null=True, blank=True)
    questions = models.ManyToManyField(Question, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='quizzes_created',
                                   null=True)
    updated_by = models.ForeignKey(User, related_name='quizzes_updated',
                                   null=True)
    user = property(lambda self: self.created_by)

    def serialize_hook(self, hook):
        # optional, there are serialization defaults
        # we recommend always sending the Hook
        # metadata along for the ride as well
        return {
            'hook': hook.dict(),
            'data': {
                'id': str(self.id),
                'description': self.description,
                'metadata': self.metadata,
                'created_at': self.created_at.isoformat(),
                'created_by': self.created_by.username,
                'updated_at': self.updated_at.isoformat(),
                'updated_by': self.updated_by.username
            }
        }

    def __str__(self):  # __unicode__ on Python 2
        return str(self.id)
