from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'quiz', views.QuizViewSet)
router.register(r'question', views.QuestionViewSet)
router.register(r'answer', views.AnswerViewSet)
router.register(r'tracker', views.TrackerViewSet)
router.register(r'webhook', views.HookViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^api/v1/quiz/untaken$',
        views.QuizzesUntaken.as_view()),
    url(r'^api/v1/', include(router.urls)),
]
