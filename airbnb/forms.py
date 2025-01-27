from django import forms
from users.models import CustomUser
from django.contrib.auth import get_user_model


User = get_user_model()



class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_picture']  # Add `profile_picture` field to your model


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture',]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


# class AdditionalUserInfoForm(forms.Form):
#     national_id = forms.CharField(
#         max_length=20,
#         required=True,
#         label="National ID Number",
#         widget=forms.TextInput(attrs={"placeholder": "Enter your National ID Number"})
#     )
#     selfie = forms.ImageField(
#         required=True,
#         label="Selfie",
#         widget=forms.FileInput(attrs={"accept": "image/*"})
#     )



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
