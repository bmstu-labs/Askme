from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Question

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