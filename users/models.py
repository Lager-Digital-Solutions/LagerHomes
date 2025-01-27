import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_ROLES = [
        ('host', 'Host'),
        ('customer', 'Customer'),
        ('affiliate', 'Affiliate'),

    ]
    role = models.CharField(
        max_length=10,
        choices=USER_ROLES,
        default='customer'  # Default to customer
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    userID = models.CharField(max_length=50, unique=True, editable=False, null=True)
    affiliate_code = models.CharField(max_length=50, blank=True, null=True)



    def save(self, *args, **kwargs):
        if not self.userID:  # Only generate a userID if it doesn't already exist
            self.userID = self.generate_user_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_user_id():
        """
        Generate a custom user ID starting with 'LAGERHOMES-' followed by 8 random alphanumeric characters.
        """
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"LAGERHOMES-{random_part}"
