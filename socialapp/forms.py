# Django
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import ClearableFileInput
# from captcha.fields import ReCaptchaField, ReCaptchaV3


# App
from socialapp.models import Profile, GENDER, Interest, Package, PackageItem, List, ListProfile, Conversation, Message

class AvatarFileWidget(ClearableFileInput):
    template_name = 'socialapp/widgets/avatar_field.html'

class ProfileForm(forms.ModelForm):
    url = forms.URLField(label='Blog or website url', required=False, widget=forms.URLInput(attrs={ 'class': 'input', 'placeholder': 'http://example.com' }))
    politics = forms.BooleanField(label='I am interested in political campaigns', required=False)
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Start typing location...'}))
    bio = forms.CharField(label='Short bio', widget=forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Tell us a little bit about yourself', 'rows': 4}))
    interests = forms.ModelMultipleChoiceField(queryset=Interest.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    avatar = forms.FileField(label='', widget=AvatarFileWidget(attrs={ 'mimetype': 'image/jpg' }))
    class Meta:
        model = Profile
        fields = ['location', 'gender', 'url', 'politics', 'interests', 'bio', 'avatar']

class UserForm(forms.ModelForm):
    first_name = forms.CharField(label='First name', widget=forms.TextInput(attrs={ 'class': 'input' }))
    last_name = forms.CharField(label='Last name', widget=forms.TextInput(attrs={ 'class': 'input' }))
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class PackageForm(forms.ModelForm):
    title = forms.CharField(label='Package title', widget=forms.TextInput(attrs={ 'class': 'input', 'placeholder': 'Package title' }))
    error_css_class = 'is-danger'
    class Meta:
        model = Package
        fields = ['title']

class PackageItemForm(forms.ModelForm):
    title = forms.CharField(label='Item', widget=forms.TextInput(attrs={ 'class': 'input', 'placeholder': 'e.g 2 Twitter posts' }))
    cost = forms.CharField(label='Cost', widget=forms.NumberInput(attrs={ 'class': 'input', 'placeholder': '0.00' }))
    error_css_class = 'is-danger'
    class Meta:
        model = PackageItem
        fields = ['title', 'cost']


class ListForm(forms.ModelForm):
    name = forms.CharField(label='List title', widget=forms.TextInput(attrs={ 'class': 'input', 'placeholder': 'Name of list' }))
    error_css_class = 'is-danger'
    class Meta:
        model = List
        fields = ['name']


class ConversationForm(forms.Form):
    conversation = forms.CharField(label='', widget=forms.Textarea(attrs={ 'class': 'textarea', 'placeholder': 'Start a conversation', 'rows': 3 }))

class MessageForm(forms.ModelForm):
    message = forms.CharField(label='', widget=forms.Textarea(attrs={ 'class': 'textarea', 'placeholder': 'Write your response...', 'rows': 2 }))

    class Meta:
        model = Message
        fields = ['message',]

class InstagramInsightsForm(forms.Form):
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'instagram username'}))
    # captcha = ReCaptchaField(widget=ReCaptchaV3)










# End
