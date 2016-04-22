from django.contrib import admin

from .models import Quiz, Question


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

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
