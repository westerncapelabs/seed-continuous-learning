from .models import Quiz, Question
from rest_hooks.models import Hook
from rest_framework import serializers


class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        read_only_fields = ('created_at', 'updated_at')
        fields = ('id', 'description', 'metadata', 'created_at',
                  'created_by', 'updated_at', 'updated_by')


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        read_only_fields = ('created_at', 'updated_at')
        fields = ('id', 'version', 'question_type', 'question', 'answers',
                  'response_correct', 'response_incorrect', 'active',
                  'created_at', 'created_by', 'updated_at', 'updated_by')


class HookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hook
        read_only_fields = ('user',)
