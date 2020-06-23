from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Requis.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
        labels = {
            'username': _("Nom d'utilisateur"),
            'email': _("Adresse email valide"),
        }
        help_texts = {
        }
