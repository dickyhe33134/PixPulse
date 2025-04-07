import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class Setting(models.Model):
    bio=models.TextField()
    language=models.TextField()
    notifications=models.BooleanField()

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=20, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=True)
    profile_picture = models.URLField(max_length=500, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    friends = models.ManyToManyField('self', blank=True)
    settings = models.OneToOneField(
        'Setting', 
        on_delete=models.CASCADE, 
        null=True,
        blank=True
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return self.username

class Comment(models.Model):
    comment_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id=models.UUIDField(default=uuid.uuid4, editable=False)
    content=models.TextField(null=False)
    created_at =models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return self.content


class Post(models.Model):
    post_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id=models.UUIDField(default=uuid.uuid4, editable=False)
    content=models.TextField(null=False)
    media_url=models.JSONField(null=False,default=list,blank=True)
    created_at =models.DateTimeField(auto_now_add = True)
    updated_at =models.DateTimeField(auto_now = True)
    likes =models.ManyToManyField(User, default=list, blank=True)
    comments=models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.content
 
class Message(models.Model):
    class Status(models.TextChoices):
        SENT = 'sent'
        DELIIVERED = 'delivered'
        READ = 'read'
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.UUIDField(default=uuid.uuid4, editable=False)
    receiver_id = models.UUIDField(default=uuid.uuid4, editable=False)
    content = models.TextField(null=False)
    media_url=models.JSONField(null=False,default=list,blank=True)
    created_at =models.DateTimeField(auto_now_add = True)
    status =models.CharField(max_length=10, choices=Status.choices, default=Status.SENT)
    def __str__(self):
        return self.content[0:50]