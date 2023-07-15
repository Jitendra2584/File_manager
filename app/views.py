from django.shortcuts import render,HttpResponse,redirect,get_object_or_404,reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .decorators import authenticated_user_required
from .tokens import account_activation_token
from django.db.models.query_utils import Q
from .models import File,Comment
from .forms import FileForm,Commentform,ShareForm,Userform,SetPasswordForm,PasswordResetForm
import uuid



@authenticated_user_required
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            msg= "Your password has been changed.please log in again"
            print('changed')
            return render(request, 'login.html', {'errors': msg})
            
        else:
            errors=list(form.errors.values())
            return render(request, 'password_reset_confirm.html', {'form': form,'errors': errors})
            
    form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})

# Create your views here.
@authenticated_user_required
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

@authenticated_user_required
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


@authenticated_user_required
def Sharepage(request):
    if request.method=='POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            file=form.cleaned_data['shared_file']
            file.shared_with.add(form.cleaned_data['shared_with'])
            error="file is shared, please return to home page"
            return render(request,'success.html',{'error':error})
        else:
            return HttpResponse(form.errors)
    form=ShareForm(current_user=request.user)
    return render(request, 'share.html', {'form':form})



def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
        print(user)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        print(user.is_active)
        user.save()
        
        errors="Thank you for your email confirmation. Now you can login your account."
        return render(request,'login.html',{'errors':errors})
    else:
        print('wrong none user or invalid user')
        

    return redirect('home')


def activeEmail(request,user,to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        print(f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        print(f'Problem sending email to {to_email}, check if you typed it correctly.')


def SignupPage(request):
    if request.method=='POST':
        form=Userform(request.POST)
        if form.is_valid():
            uname=form.cleaned_data['username']
            email=form.cleaned_data['email']
            pass1=form.cleaned_data['password1']
            pass2=form.cleaned_data['password2']
            if  User.objects.filter(username=uname).exists():
                errors="Your username is already exist! or No username Provide"
                return render (request,'signup.html',{"form":form,'errors':errors})
            if  User.objects.filter(email=email).exists():
                errors="Your email is already exist! or no email provide"
                return render (request,'signup.html',{"form":form,'errors':errors})
            if pass1!=pass2:
                errors="Your password and confrom password are not Same!!"
                return render (request,'signup.html',{"form":form,'errors':errors})
            else:  
                my_user=form.save(commit=False)
                my_user.is_active=False
                my_user.save()
                activeEmail(request,my_user,request.POST.get('email'))
                errors="please activate your account in email"
                return render(request,'login.html',{"form":form,'errors':errors})
        else:
            errors = "username either taken or use only  number,digit and character"
            return render (request,'signup.html',{"form":form,'errors':errors})
    else:
        form=Userform()
        return render (request,'signup.html',{'form':form})


def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
                login(request,user)
                return redirect('home')
        else:
            error="activate your account / Username or Password is incorrect!!!"
            return render(request,'login.html',{'errors':error})
    else:
        return render(request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')
# Create your views here.


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                        form = PasswordResetForm()
                        errors="we have send a link please change your password through the link."
                        return render(request, "password_reset.html",{"form": form,"errors":errors})
                            
                else:
                    print("Problem sending reset password email, <b>SERVER PROBLEM</b>")
            # errer k sath
            else:
                errors="please provide a valid user Email"
                return render(request,"password_reset.html", {"form": form,"errors": errors})    
        else:
            errors=form.errors.values()
            return render(request,"password_reset.html", {"form": form,"errors": errors})
            
    form = PasswordResetForm()
    return render(
        request=request, 
        template_name="password_reset.html", 
        context={"form": form}
        )



def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                login(request,user)
                return redirect('home')
            else:
                errors=form.errors.values()
                return render(request, 'password_reset_confirm.html', {'form': form,'errors':errors})


        form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        errors="please provide a valid link"
        return render(request, 'password_reset_confirm.html', {'form': form,'errors':errors})
