# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.core.validators import RegexValidator



    

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z_]+$',  # Allows only letters and underscores
                message="Username can only contain letters and underscores, no numbers allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )

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
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# class LoginForm(AuthenticationForm):
#     username = forms.CharField(label="Username or Email")
#     password = forms.CharField(widget=forms.PasswordInput)


from django import forms
from .models import Review, UserProfile

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'rating', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Give your review a title', 'class': 'form-control'}),
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'placeholder': 'Write your comment here', 'rows': 4, 'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False)  # ✅ Allow empty input
    address = forms.CharField(required=False)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address']

        def clean(self):
            cleaned_data = super().clean()
            for field in self.fields:
                if not cleaned_data.get(field):
                    cleaned_data[field] = None  # ✅ Store empty fields as NULL in the DB
            return cleaned_data

from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["full_name", "last_name", "email", "phone", "state", "street_address", "city", "country", "postal_code", "is_default"]



from .models import Subscriber

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email"]


from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']