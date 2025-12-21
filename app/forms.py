from django import forms
from django.contrib.auth import get_user_model
from app.models import Profile, Question, Tag, Answer


UserModel = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('username') == 'admin':
            raise forms.ValidationError('Enter a valid name')
        return cleaned_data


class SettingsForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username', required=False)
    avatar = forms.ImageField(label='Profile image', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and 'username' not in self.data:
            self.fields['username'].initial = self.user.username

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username and self.user:
            return self.user.username
            
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters long')
        
        if self.user:
            if UserModel.objects.filter(username=username).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError('Username already taken')
        
        return username

    def clean(self):
        cleaned_data = super().clean()
        if 'username' not in cleaned_data or not cleaned_data['username']:
            if self.user:
                cleaned_data['username'] = self.user.username
        
        return cleaned_data
    
    def save(self, user):
        username = self.cleaned_data.get('username')
        avatar = self.cleaned_data.get('avatar')
        
        has_changes = False

        if username and username != user.username:
            user.username = username
            has_changes = True
        
        if avatar:
            user.avatar = avatar
            has_changes = True
        
        if has_changes:
            user.save()
        
        return has_changes


class SignupForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput)
    passwordConfirm = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    avatar = forms.ImageField(label="Avatar", required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['passwordConfirm']:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data
    
    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        avatar = self.cleaned_data.get('avatar')

        user = Profile(
            username=username,
            avatar=avatar
        )

        user.set_password(password)
        user.save()

        return user
    

class AskQuestionForm(forms.Form):
    title = forms.CharField(max_length=200, label='Title')
    text = forms.CharField(widget=forms.Textarea, label='Details')
    tags = forms.CharField(max_length=200, label='Tags')

    # TODO: add validation for title, text and tags

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    def save(self, author):
        question = Question.objects.create(
            title=self.cleaned_data['title'],
            text=self.cleaned_data['text'],
            author=author
        )

        # Separate tags by comma
        tag_names = [tag.strip() for tag in self.cleaned_data['tags'].split(',') if tag.strip()]
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)
        
        return question


class AnswerForm(forms.Form):
    text = forms.CharField(max_length=200, label='Answer')

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    def save(self, author, question):
        answer = Answer.objects.create(
            text=self.cleaned_data['text'],
            author=author,
            question=question,
        )

        return answer