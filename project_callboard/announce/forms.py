from django import forms
from .models import Note
from ckeditor.widgets import CKEditorWidget
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class NoteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].required = False

    class Meta:
        model = Note
        fields = ['author', 'header', 'text', 'category']
        widgets = {
            'text': CKEditorWidget(config_name='awesome_ckeditor')
        }


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_users = Group.objects.get(name="units")
        user.groups.add(common_users)
        return user
