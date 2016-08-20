from .models import Quiz, Question, Tracker, Answer
from rest_hooks.models import Hook
from rest_framework import serializers


class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        read_only_fields = ('created_at', 'updated_at')
        fields = ('id', 'description', 'metadata', 'questions', 'active',
                  'archived', 'created_at', 'created_by', 'updated_at',
                  'updated_by')


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        read_only_fields = ('created_at', 'updated_at')
        fields = ('id', 'version', 'question_type', 'question', 'answers',
                  'response_correct', 'response_incorrect', 'active',
                  'created_at', 'created_by', 'updated_at', 'updated_by')


class TrackerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tracker
        read_only_fields = ('started_at', )
        fields = ('id', 'identity', 'quiz', 'complete', 'metadata',
                  'started_at', 'created_by', 'completed_at', 'updated_by')


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        read_only_fields = ('created_at', 'updated_at')
        fields = ('id', 'version', 'question', 'question_text', 'answer_value',
                  'answer_text', 'answer_correct', 'response_sent', 'tracker',
                  'created_at', 'created_by', 'updated_at', 'updated_by')


class HookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hook
        read_only_fields = ('user',)
