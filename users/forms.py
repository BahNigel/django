from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile,Blog,Event
from django.utils.dates import MONTHS, WEEKDAYS
from django.utils.html import format_html
from django.utils.translation import gettext as _

class ExtendedUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['profile_picture'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    profile_picture = forms.ImageField(required=False)
    address = forms.CharField(max_length=500)
    account_typ = [
        ('', 'Select account type'),
        ('1', 'Ductor'),
        ('2', 'Patient'),
    ]
    type = forms.ChoiceField(choices=account_typ, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name','username', 'email',  'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()

        profile = UserProfile(user=user,address=self.cleaned_data['address'],type=self.cleaned_data['type'], profile_picture=self.cleaned_data['profile_picture'])
        profile.save()


class blogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(blogForm, self).__init__(*args, **kwargs)
        self.fields['blog_image'].widget.attrs['class'] = 'form-control'
        self.fields['summary'].widget.attrs['class'] = 'form-control'
        self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['class'] = 'form-control'
    categorys = [
    ('', 'Select category'),
    ('Mental Health', 'Mental Health'),
    ('Heart Disease', 'Heart Disease'),
    ('Covid19', 'Covid19'),
    ('Immunization', 'Immunization'),
    ]
    category = forms.ChoiceField(choices=categorys, widget=forms.Select(attrs={'class': 'form-select'}))
    state = [
    ('', 'Select category'),
    ('1', 'Publish'),
    ('2', 'Draft'),
    ]
    status = forms.ChoiceField(choices=state, widget=forms.Select(attrs={'class': 'form-select'}))
    user_id = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Blog
        fields = ('title', 'category','summary', 'content',  'blog_image', 'status', 'user_id')