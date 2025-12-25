from django.db import models
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.utils import timezone
from typing import Union


class Profile(AbstractUser):
    avatar = models.ImageField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = 'default.png'
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')

    def hot(self):
        return self.annotate(
            likes_cnt=models.Count('likes')
        ).order_by('-likes_cnt', '-created_at')

    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-created_at')


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    tags = models.ManyToManyField(Tag, related_name='questions', through='QuestionTag')

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_url(self):
        return f"/question/{self.id}/"
    
    @property
    def rating(self):
        from django.db.models import Sum
        result = self.likes.aggregate(total=Sum('value'))
        return result['total'] or 0


class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'tag')


class Answer(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"Answer #{self.id} to Q{self.question_id}"
    
    def save(self, *args, **kwargs):
        if self.is_correct and self.question:
            Answer.objects.filter(question=self.question).exclude(id=self.id).update(is_correct=False)
        super().save(*args, **kwargs)


class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f'{self.user} -> {self.question} ({self.value})'
    
    @classmethod
    def canVote(cls, user: 'Profile', question: 'Question'):
        if user.is_anonymous:
            return False, "You must be logged in to vote"
        
        if question.author == user:
            return False, "You cannot vote for your own question"
        
        if cls.objects.filter(user=user, question=question).exists():
            return False, "You have already voted for this question"
        
        return True, ""


class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VALUE_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.user} -> {self.answer} ({self.value})'
