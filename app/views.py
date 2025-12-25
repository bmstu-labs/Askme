from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from typing import List
import json

from .forms import SignupForm, LoginForm, AskQuestionForm, AnswerForm, SettingsForm
from .models import Question, Tag, Answer, QuestionLike


@login_required
def markCorrectAnswer(request, question_id: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        
        if not answer_id:
            return JsonResponse({'error': 'Answer ID is required'}, status=400)
        
        question = Question.objects.get(id=question_id)
        answer = Answer.objects.get(id=answer_id, question=question)
        
        if question.author != request.user:
            return JsonResponse(
                {
                    'error': 'Only the author of the question can mark correct answer'
                },
                status=403
            )
        
        if answer.is_correct:
            answer.is_correct = False
            answer.save()
        else:
            answer.is_correct = True
            answer.save()
        
        return JsonResponse({
            'success': True,
            'is_correct': answer.is_correct,
            'answer_id': answer_id
        })
    
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def voteQuestion(request, question_id: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        question = Question.objects.get(id=question_id)
        value = int(data.get('value'))

        # Check value

        can_vote = QuestionLike.canVote(request.user, question)
        if not can_vote:
            return JsonResponse(
                {
                    'error': 'Cannot vote'
                },
                status=403
            )
        
        like, created = QuestionLike.objects.update_or_create(
            user=request.user,
            question=question,
            defaults={'value': value}
        )
        
        return JsonResponse({
            'success': True,
            'action': 'like' if value == 1 else 'dislike'
        })
    
    except Question.DoesNotExist:
        return JsonResponse(
            {
                'error': 'Question not found'
            },
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {
                'error': str(e)
            },
            status=500
        )
    

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

@login_required(login_url='login')
def settings(request):
    if request.method != 'POST':
        settingsForm = SettingsForm(user=request.user)
    else:
        settingsForm = SettingsForm(
            request.POST,
            request.FILES,
            user=request.user
        )
        
        if settingsForm.is_valid():
            hasChanges = settingsForm.save(request.user)
            if hasChanges:
                messages.success(request, 'Your profile updated')
            
            return redirect('settings')

    return render(
        request=request,
        template_name='settings.html',
        context={
            'form': settingsForm,
            'user': request.user
        }
    )


@login_required
def ask(request):
    if request.method != 'POST':
        form = AskQuestionForm()
    else:
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect('question', question_id=question.id)

    return render(
        request=request,
        template_name='ask.html',
        context={
            'form': form
        }
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