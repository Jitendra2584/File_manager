from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import File,Comment
from django_select2.forms import Select2Widget
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

# Create the form class.
class FileForm(ModelForm,forms.Form):
    # shared_with = forms.ModelMultipleChoiceField(
    #     queryset=User.objects.all(),
    #     widget=forms.Select(),
    #     required=False
    # )
    class Meta: 
        model = File
        fields = ["file"]



class Userform(ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),required=True,)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Valid Email only'}), required=True)
    class Meta: 
        model = get_user_model()
        fields = ['username']
    def save(self, commit=True):
        user = super(Userform, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class Commentform(ModelForm):
    class Meta:
        model=Comment
        fields=['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'cols': 30}),
        }

class ShareForm(forms.Form):
    shared_with=forms.ModelChoiceField(queryset=User.objects.all(),widget=Select2Widget)
    shared_file=forms.ModelChoiceField(queryset=File.objects.all(),to_field_name='filename',widget=Select2Widget)
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(ShareForm, self).__init__(*args, **kwargs)
        if current_user:
            self.fields['shared_with'].queryset = User.objects.exclude(username=current_user.username)
            user_id=User.objects.get(username=current_user.username).id
            queryset1 = File.objects.filter(display_name=user_id)  # First queryset
            queryset2 = File.objects.filter(shared_with=user_id)   # Second queryset
            combined_queryset = queryset1.union(queryset2)     # Combine the two querysets
            self.fields['shared_file'].queryset = combined_queryset


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)


