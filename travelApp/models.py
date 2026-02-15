from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django.core.validators import MinValueValidator


class VehicleCategory(models.Model):
    """Categories for different types of vehicles"""
    name = models.CharField(max_length=100, help_text="e.g., SUV & Sedan, All Party Buses")
    slug = models.SlugField(unique=True, help_text="URL-friendly version (auto-generated)")
    description = models.TextField(blank=True, help_text="Brief description of this category")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")

    class Meta:
        verbose_name_plural = "Vehicle Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """Individual vehicles in the fleet"""
    category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.CASCADE,
        related_name='vehicles',
        help_text="Which category does this vehicle belong to?"
    )
    name = models.CharField(max_length=200, help_text="Vehicle name/title")
    description = models.TextField(help_text="Describe the vehicle, its features, etc.")
    passenger_capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="How many passengers can this vehicle hold?"
    )

    # Pricing
    show_pricing = models.BooleanField(
        default=False,
        help_text="Check to show price, uncheck to show 'Request Quote'"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Price per hour/day (optional)"
    )
    price_unit = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., 'per hour', 'per day', 'starting at'"
    )

    # Display settings
    featured_image = models.ImageField(
        upload_to='fleet/featured/',
        help_text="Main photo shown on fleet page"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this vehicle from the website"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order within category (lower numbers appear first)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__order', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class VehicleImage(models.Model):
    """Gallery images for each vehicle"""
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        help_text="Which vehicle does this image belong to?"
    )
    image = models.ImageField(upload_to='fleet/gallery/')
    caption = models.CharField(max_length=200, blank=True, help_text="Optional image description")
    order = models.IntegerField(default=0, help_text="Display order in gallery")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.vehicle.name} - Image {self.order}"


class Booking(models.Model):
    """Model for customer bookings"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    DURATION_CHOICES = [
        ('1', '1 Hour'),
        ('2', '2 Hours'),
        ('3', '3 Hours'),
        ('4', '4 Hours'),
        ('6', '6 Hours'),
        ('8', '8 Hours'),
        ('full-day', 'Full Day (12 Hours)'),
        ('custom', 'Custom Duration'),
    ]

    # Contact Information
    customer_name = models.CharField(max_length=100, blank=True)
    customer_email = models.EmailField(blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)

    # Trip Details
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    date = models.DateField()
    pickup_time = models.TimeField()
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)

    # Vehicle Selection
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )

    # Pricing
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmation_code = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['confirmation_code']),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.customer_name or self.phone} - {self.date}"

    def save(self, *args, **kwargs):
        # Generate confirmation code if not exists
        if not self.confirmation_code:
            import random
            import string
            self.confirmation_code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=10
            ))
        super().save(*args, **kwargs)


# models.py


