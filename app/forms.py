from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Question, Tag

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput)

    def clean():
        cleaned_data = super().clean()
        if cleaned_data.get('username') == 'admin':
            raise forms.ValidationError('Enter a valid name')
        return cleaned_data
    

class SignupForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput)
    passwordConfirm = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    email = forms.EmailField(max_length=100, label="Email")
    avatar = forms.ImageField(label="Avatar", required=False)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['passwordConfirm']:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data
    
    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)
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