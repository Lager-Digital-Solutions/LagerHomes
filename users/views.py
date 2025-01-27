from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Import your CustomUser model
from airbnb.models import AffiliateLink  # Import the AffiliateLink model

# Custom User Creation Form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('host', 'Host'), ('customer', 'Customer')],  # Restrict choices
        required=True
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'profile_picture']

# Registration View
def register(request):
    # Retrieve affiliate code from the GET parameter
    affiliate_code = request.GET.get('affiliate_code', None)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Save the new user
            
            # Attach the affiliate code to the user if it exists
            if affiliate_code:
                try:
                    affiliate = AffiliateLink.objects.get(link_code=affiliate_code).affiliate
                    user.affiliate_code = affiliate_code  # Attach affiliate code to the user
                    user.save()  # Save the updated user
                except AffiliateLink.DoesNotExist:
                    messages.error(request, "Invalid affiliate code. User created without affiliate link.")
            
            # Log the user in after registration
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            return redirect('airbnb:index')  # Redirect to the homepage or dashboard
        else:
            # Form is invalid, display errors in the template
            pass
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})