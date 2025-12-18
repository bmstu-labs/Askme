from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from typing import List

from .models import Question, Tag, Answer


def paginate(request, objects, per_page=5):
    paginator = Paginator(objects, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def getAnswers(q: Question):
    return Answer.objects.filter(question=q)


def question(request, question_id: int):
    q = get_object_or_404(Question, pk=question_id)

    answers = getAnswers(q)
    answers_page = paginate(request, answers)
    
    return render(
        request=request,
        template_name='question.html',
        context={
            'tags': getTopNTags(),
            'question': q,
            'answers': answers_page.object_list,
            'page_obj': answers_page
        }
    )


def newQuestions(request):
    questions = Question.objects.new()
    questions_page = paginate(request, questions)

    return render(
        request=request,
        template_name='questions.html',
        context={
            'tags': getTopNTags(),
            'questions': questions_page.object_list,
            'page_obj': questions_page
        }
    )


def hotQuestions(request):
    questions = Question.objects.hot()
    questions_page = paginate(request, questions)

    return render(
        request=request,
        template_name='hot.html',
        context={
            'tags': getTopNTags(),
            'questions': questions_page.object_list,
            'page_obj': questions_page
        }
    )


def signup(request):
    return render(
        request=request,
        template_name='signup.html'
    )


def login(request):
    return render(
        request=request,
        template_name='login.html'
    )


def settings(request):
    return render(
        request=request,
        template_name='settings.html'
    )


def ask(request):
    return render(
        request=request,
        template_name='ask.html'
    )


def getTopNTags(n: int = 5) -> List[Tag]:
    tags = Tag.objects.all()
    return tags[:n]


def tag(request, tagName: str):
    tag_obj = get_object_or_404(Tag, name=tagName)

    questions = Question.objects.filter(tags=tag_obj).order_by('-created_at')

    questions_page = paginate(request, questions)

    return render(
        request=request,
        template_name='tag.html',
        context={
            'tags': getTopNTags(),
            'tag_name': tag_obj.name,
            'questions': questions_page.object_list,
            'page_obj': questions_page
        }
    )