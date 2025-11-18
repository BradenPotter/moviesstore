from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django import forms
from django_countries.fields import CountryField

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update( {'class': 'form-control'} )


# class SignupForm(UserCreationForm):
#     country = forms.CharField(max_length=100)
#     region = forms.CharField(
#         max_length=100,
#         label="City or State"
#         )

#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ("username",  "country", "region", "password1", "password2")
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for name, field in self.fields.items():
#             field.widget.attrs.update({"class": "form-control"})


class SignupForm(UserCreationForm):
    country = CountryField().formfield()
    region = forms.CharField(
        max_length=100,
        label="City or State"
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",  "country", "region", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
