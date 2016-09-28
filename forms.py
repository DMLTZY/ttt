from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField, PasswordChangeForm
from .models import MyUser
from django import forms


def _clean_mobile(value):
    try:
        value = int(value)
    except Exception as e:
        # print(e)
        raise forms.ValidationError(
            'Not a number, please enter a correct mobile number.',
            code='mobile_wrong',
        )

    if not (13000000000 < value < 20000000000):
        raise forms.ValidationError(
            'Please enter a correct mobile number.',
            code='mobile_wrong',
        )
    return value


class MyUserCreationForm(UserCreationForm):

    def clean_mobile(self):
        value = self.cleaned_data['mobile']
        return _clean_mobile(value)

    class Meta:
        model = MyUser
        fields = ("username", 'mobile', 'email', 'password1', 'password2')
        field_classes = {'username': UsernameField}


class MyUserChangeForm(UserChangeForm):

    def clean_mobile(self):
        value = self.cleaned_data['mobile']
        return _clean_mobile(value)

    class Meta:
        model = MyUser
        fields = '__all__'
        field_classes = {'username': UsernameField}


class RegistrationForm(MyUserCreationForm):

    class Meta:
        model = MyUser
        fields = ("username", 'mobile', 'email', 'password1', 'password2')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(
            attrs={'placeholder': 'username', 'class': 'form-control top'})
        self.fields['mobile'].widget = forms.TextInput(
            attrs={'placeholder': 'mobile', 'class': 'form-control middle'})
        self.fields['email'].widget = forms.EmailInput(
            attrs={'placeholder': 'mail@domain.com', 'class': 'form-control middle'})
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'placeholder': 'password', 'class': 'form-control middle'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'placeholder': 're-password', 'class': 'form-control bottom'})


class LoginForm(forms.ModelForm):
    username_or_mobile = forms.CharField(max_length=150)
    # password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('username_or_mobile', 'password',)
        # field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username_or_mobile'].widget = forms.TextInput(
            attrs={'placeholder': 'username/mobile', 'class': 'form-control top'})
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'placeholder': 'password', 'class': 'form-control middle'})


class ChangeProfileForm(PasswordChangeForm):
    username = forms.CharField()
    email = forms.EmailField()
    mobile = forms.CharField()

    def clean_username(self):
        try:
            user = MyUser.objects.get(username=self.cleaned_data.get('username'))
        except MyUser.DoesNotExist:
            return self.cleaned_data['username']
        else:
            if user.username != self.request.user.username:
                raise forms.ValidationError('This username is already exist. Try again.')
            else:
                return self.cleaned_data['username']

    def clean_mobile(self):
        try:
            user = MyUser.objects.get(mobile=self.cleaned_data.get('mobile'))
        except MyUser.DoesNotExist:
            value = self.cleaned_data['mobile']
            return _clean_mobile(value)
        else:
            if user.mobile != self.request.user.mobile:
                raise forms.ValidationError('This mobile is already exist. Try again.')
            else:
                value = self.cleaned_data['mobile']
                return _clean_mobile(value)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ChangeProfileForm, self).__init__(self.request.user, *args, **kwargs)
        self.fields['username'].widget = forms.TextInput(
            attrs={'placeholder': 'username', 'class': 'form-control top'})
        self.fields['mobile'].widget = forms.TextInput(
            attrs={'placeholder': 'mobile', 'class': 'form-control middle'})
        self.fields['email'].widget = forms.EmailInput(
            attrs={'placeholder': 'mail@domain.com', 'class': 'form-control middle'})
        self.fields['old_password'].widget = forms.PasswordInput(
            attrs={'placeholder': 'old_password', 'class': 'form-control middle'})
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={'placeholder': 'new password', 'class': 'form-control middle'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={'placeholder': 're-new-password', 'class': 'form-control bottom'})
    field_order = ['username', 'mobile', 'email', 'old_password', 'new_password1', 'new_password2']

    def save(self, commit=True):
        user = super(ChangeProfileForm, self).save(commit=False)
        user.username = self.cleaned_data.get('username')
        user.mobile = self.cleaned_data.get('mobile')
        user.email = self.cleaned_data.get('email')
        if commit:
            self.user.save()
        return self.user
