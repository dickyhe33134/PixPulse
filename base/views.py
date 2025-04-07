from django.shortcuts import render
from .models import User, Post

# Create your views here.



def home(request):
    users= User.objects.all
    context = {'allppl':users}
    return render(request, 'base/home.html',context)

def about(request,userid):
    post_con=Post.objects.get(user_id=userid)
    context = {'content':post_con}
    return render(request, 'base/groot.html',context)