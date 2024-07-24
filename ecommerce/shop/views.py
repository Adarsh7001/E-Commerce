from django.shortcuts import render
from shop.models import Category,Product
from django.db.models import Q
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'home.html')


def allcategory(request):
    return render(request,'all_category.html')


def category(request):
    c=Category.objects.all()
    return render(request,'category.html',{'category':c})

def product(request,i):
    c=Category.objects.get(id=i)
    p=Product.objects.filter(category=c)
    return render(request,'product.html',{'category':c,'product':p})

def details(request,i):
    d=Product.objects.get(id=i)
    return render(request,'details.html',{'detail':d})

def search(request):
    q=None
    query=''
    if(request.method=='POST'):
        query=request.POST['q']
        if (query):
            q=Product.objects.filter(Q(name__icontains=query)|Q(description__icontains=query))
    return render(request,'search.html',{'product':q,'query':query})

def register(request):
    if (request.method == 'POST'):
        u = request.POST['u']
        p = request.POST['p']
        cp = request.POST['cp']
        e=request.POST['e']
        f = request.POST['f']
        s = request.POST['s']
        if(cp==p):
            u=User.objects.create_user(username=u,password=p,email=e,first_name=f,last_name=s)
            u.save()
            return home(request)
        else:
            messages.error(request,'password doesnt match')
    return render(request,'register.html')

def user_login(request):
    if(request.method=='POST'):
        u=request.POST['u']
        p=request.POST['p']
        user=authenticate(username=u,password=p)
        if user and user.is_superuser==True:
            login(request,user)
            return category(request)
        if user and user.is_superuser == False:
            login(request,user)
            return category(request)
        else:
            messages.error(request,'invalid credentials')
    return render(request,'login.html')

# @login_required
def user_logout(request):
    logout(request)
    return home(request)