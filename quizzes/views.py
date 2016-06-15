from .models import Quiz, Question, Tracker, Answer
from rest_hooks.models import Hook
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .serializers import (QuizSerializer, QuestionSerializer, AnswerSerializer,
                          TrackerSerializer, HookSerializer)


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
    API endpoint that allows Quiz models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_fields = ('active', 'metadata')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Question models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_fields = ('question_type', 'active')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class AnswerViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Answer models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    filter_fields = ('question', 'tracker', 'answer_correct')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class TrackerViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows Tracker models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Tracker.objects.all()
    serializer_class = TrackerSerializer
    filter_fields = ('identity', 'quiz', 'complete', 'started_at',
                     'completed_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class QuizzesUntaken(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizSerializer

    def get_queryset(self):
        """
        This view should return a list of all the quizzes the identity in
        query parameters hasn't taken.
        Always excludes quizzes with active = False
        """
        identity_id = self.request.query_params['identity']
        taken = Tracker.objects.filter(
            complete=True, identity=identity_id).values_list('quiz', flat=True)
        return Quiz.objects.filter(active=True).exclude(id__in=taken)
