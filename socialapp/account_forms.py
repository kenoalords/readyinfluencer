from allauth.account.forms import LoginForm, ResetPasswordForm, SignupForm, SetPasswordForm
from django import forms
from allauth.compat import ugettext, ugettext_lazy as _
from .models import Profile

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Username or Email Address'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'})

        self.fields['password'].label = ''
        self.fields['login'].label = ''


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Email Address'})
        self.fields['email'].label = ''

class CustomSignupForm(SignupForm):
    error_css_class = 'is-danger'
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Email Address'})
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Username'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Confirm password'})
        self.fields['is_influencer'] = forms.CharField(label="Yes, I am an influencer", widget=forms.CheckboxInput(attrs={'value': 1}), required=False)

        self.fields['password1'].label = ''
        self.fields['password2'].label = ''
        self.fields['email'].label = ''
        self.fields['username'].label = ''

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        # Custom processing here
        is_influencer = request.POST.get('is_influencer', False)
        if is_influencer:
            influencer = bool(request.POST['is_influencer'])
            profile = Profile(is_influencer=influencer, user=user)
            profile.save()
        return user



class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Confirm password'})

        self.fields['password1'].label = ''
        self.fields['password2'].label = ''
