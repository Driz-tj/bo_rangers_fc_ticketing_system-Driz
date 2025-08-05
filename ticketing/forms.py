from django import forms
from .models import Ticket, News, TicketCategory, Match
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class AdminCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class TicketBookingForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['ticket_category', 'quantity']
        widgets = {
            'ticket_category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'body', 'image', 'video', 'category', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GatemanCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['title', 'date', 'home_team', 'home_team_logo', 'opponent', 'opponent_logo', 'venue', 'status', 'matchday']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Match Title'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'home_team': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home Team Name'}),
            'home_team_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'opponent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opponent Team'}),
            'opponent_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'matchday': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
