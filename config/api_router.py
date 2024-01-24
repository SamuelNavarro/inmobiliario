from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from inmobiliario.chat.api.views import AdviceView, AnswerView, ProfileViewSet, QuestionView
from inmobiliario.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("profiles", ProfileViewSet, basename="profiles")


app_name = "api"

urlpatterns = [
    path("questions/", QuestionView.as_view(), name="questions"),
    path("answer/", AnswerView.as_view(), name="answer"),
    path("advice/", AdviceView.as_view(), name="advice"),
]


urlpatterns += router.urls
