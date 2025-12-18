from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from typing import List

from .forms import SignupForm, LoginForm, AnswerForm
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
    
    if request.method != 'POST':
        form = AnswerForm()
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = AnswerForm(request.POST)
        if not form.is_valid():
            pass
        else:
            answer = form.save(
                author=request.user,
                question=q
            )
            return redirect('question', question_id=question_id)
    
    answers = getAnswers(q)
    answers_page = paginate(request, answers)
    
    return render(
        request=request,
        template_name='question.html',
        context={
            'tags': getTopNTags(),
            'question': q,
            'answers': answers_page.object_list,
            'page_obj': answers_page,
            'form': form,
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
    if request.method != 'POST':
        form = SignupForm()
    else:
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        
    return render(
        request=request,
        template_name='signup.html',
        context={
            'form': form
        }
    )


def login(request):
    if request.method != 'POST':
        form = LoginForm()
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                form.add_error(None, 'Invalid username or password')

    return render(
        request=request,
        template_name='login.html',
        context={
            'form': form
        }
    )


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


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

@login_required
def answer(request, question):
    if request.method != 'POST':
        form = AnswerForm()
    else:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(
                author=request.user,
                question=question
            )
            return redirect('question', question_id=question.id)

    return render(
        request,
        'question.html',
        question_id=request.question.id
    )