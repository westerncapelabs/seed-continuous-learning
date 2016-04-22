from .models import Quiz, Question
from rest_hooks.models import Hook
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import (QuizSerializer, QuestionSerializer, HookSerializer)


class HookViewSet(viewsets.ModelViewSet):
    """
    Retrieve, create, update or destroy webhooks.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Hook.objects.all()
    serializer_class = HookSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuizViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows dummy models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows dummy models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
