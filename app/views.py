from django.shortcuts import render,HttpResponse,redirect,get_object_or_404,reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
from .models import File,Comment
from .forms import FileForm,Commentform,ShareForm

# Create your views here.
@login_required(login_url='login')
def HomePage(request):
    files = File.objects.filter(display_name=request.user)
    user_id=User.objects.get(username=request.user).id
    shared_files=File.objects.filter(shared_with=user_id)
    if request.method=='POST':
        form=FileForm(request.POST,request.FILES)
        if form.is_valid():
            uploaded_file=form.cleaned_data['file']
            if File.objects.filter(filename=uploaded_file):
                errors = "please change pdf file name, already exit"
                return render (request,'home.html',{"form":form,"files":files,"shared_files":shared_files,'errors':errors})
            filename=form.cleaned_data['file']
            name=request.user
            file=File(file=uploaded_file,display_name=name,filename=filename)
            file.save()
            return redirect(reverse('home'))
        else:
            errors = "please provide PDF File Only"
            return render (request,'home.html',{"form":form,"files":files,"shared_files":shared_files,'errors':errors})
    else:
        form=FileForm()
    return render(request,'home.html',{"form":form,"files":files,"shared_files":shared_files})

@login_required(login_url='login')
def access_shared_file(request, unique_link):
    uploaded_file=File.objects.get(unique_link=unique_link)
    if request.method=='POST':
        form = Commentform(request.POST)
        if form.is_valid():
            content=form.cleaned_data['content']
            comment = form.save(commit=False)
            comment.file = uploaded_file
            comment.user = request.user
            comment.save()
            # return redirect('access_shared_file', uuid=unique_link)
    comment_form=Commentform()
    comments = uploaded_file.comments.all()
    return render(request, 'access_shared_file.html', {'file':uploaded_file,'form':comment_form,'comments':comments})


@login_required(login_url='login')
def Sharepage(request):
    if request.method=='POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            file=form.cleaned_data['shared_file']
            file.shared_with.add(form.cleaned_data['shared_with'])
            # file.shared_with.add(form.cleaned_data['shared_with'])
            # print(form.cleaned_data['shared_with'])
        else:
            print('wrong')
    form=ShareForm(current_user=request.user)
    return render(request, 'share.html', {'form':form})
    

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if  User.objects.filter(username=uname).exists():
            return HttpResponse("Your username is already exist!")
        if  User.objects.filter(email=email).exists():
            return HttpResponse("Your email is already exist!")
        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:  
            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')
    return render (request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')
# Create your views here.
