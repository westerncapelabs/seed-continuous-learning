from django.contrib import admin

from .models import Quiz, Question, Answer, Tracker


class QuizAdmin(admin.ModelAdmin):
    list_display = [
        "id", "description", "active",
        "created_at", "updated_at", "created_by", "updated_by"]
    list_filter = ["active", "created_at"]
    search_fields = ["description"]


class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "version", "question_type", "question",
        "response_correct", "response_incorrect", "active",
        "created_at", "updated_at", "created_by", "updated_by"]
    list_filter = ["active", "question_type", "created_at"]
    search_fields = ["description", "question", "answers"]


class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        "id", "version", "question", "question_text", "answer_value",
        "answer_text", "answer_correct", "response_sent", "tracker",
        "created_at", "created_by", "updated_at", "updated_by"]
    list_filter = ["answer_correct", "question", "created_at"]
    search_fields = ["question_text", "answer_text"]


class TrackerAdmin(admin.ModelAdmin):
    list_display = [
        "id", "identity", "quiz", "complete",
        "started_at", "created_by", "completed_at", "updated_by"]
    list_filter = ["complete", "started_at", "completed_at"]
    search_fields = ["identity"]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tracker, TrackerAdmin)
