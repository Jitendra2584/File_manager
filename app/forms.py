from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import File,Comment

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



class Commentform(ModelForm):
    class Meta:
        model=Comment
        fields=['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'cols': 30}),
        }

class ShareForm(forms.Form):
    shared_with=forms.ModelChoiceField(queryset=User.objects.all())
    shared_file=forms.ModelChoiceField(queryset=File.objects.all(),to_field_name='filename')
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