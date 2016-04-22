import uuid

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Quiz(models.Model):

    """
    Base Quiz model, does not hold questions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    metadata = JSONField(null=True, blank=True)
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
