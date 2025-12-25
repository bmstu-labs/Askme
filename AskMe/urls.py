"""
URL configuration for AskMe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.newQuestions, name='index'),
    path('questions/', views.newQuestions, name='questions'),
    path('hot/', views.hotQuestions, name='hot'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('settings/', views.settings, name='settings'),
    path('ask/', views.ask, name='ask'),
    path('tag/<str:tagName>/', views.tag, name='tag'),
    path('question/<int:question_id>/vote/', views.voteQuestion, name='vote_question'),
    path('question/<int:question_id>/mark_correct/', views.markCorrectAnswer, name='mark_correct_answer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)