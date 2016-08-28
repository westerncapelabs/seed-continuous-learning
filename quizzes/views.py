from .models import Quiz, Question, Tracker, Answer
from rest_hooks.models import Hook
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
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
    filter_fields = ('active', 'metadata', 'archived')

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


class QuizResultsCSV(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (r.CSVRenderer, )

    def get(self, request, format=None):
        """
        Return a list of all results.
        """
        results = Tracker.objects.all()
        content = []
        for tracker in results:
            base = {
                "tracker": tracker.id,
                "quiz": tracker.quiz_id,
                "identity": str(tracker.identity),
                "quiz_started_at": tracker.started_at,
                "quiz_complete": tracker.complete,
                "quiz_completed_at": tracker.completed_at
            }
            answers = tracker.answers.all()
            if answers.count() > 0:
                for answer in answers:
                    line = base.copy()
                    line.update({
                        "question_id": answer.question_id,
                        "question_text": answer.question_text,
                        "answer_text": answer.answer_text,
                        "answer_value": answer.answer_value,
                        "answer_correct": answer.answer_correct,
                        "answer_created_at": answer.created_at
                    })
                    content.append(line)
        return Response(content)
