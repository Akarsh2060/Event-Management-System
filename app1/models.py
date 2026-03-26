from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
    
class tbl_register(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    uname = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tbl_register"

    def __str__(self):
        return self.uname

class tbl_booking(models.Model):
    plan = models.ForeignKey('Plan', on_delete=models.PROTECT, null=True, blank=True)
    event_name = models.CharField(max_length=100)
    hotel_name = models.CharField(max_length=100, default="Unknown Hotel")
    location = models.CharField(max_length=100, null=True, blank=True)
    people_count = models.IntegerField(default=1)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

    # workflow
    status = models.CharField(max_length=50)  # Requested / Approved / Rejected

    # payment-related (NEW)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20,
        default="PENDING"  # PENDING / PARTIAL / PAID
    )

    reject_reason = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "tbl_booking"

        
class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.PositiveIntegerField(help_text="Base event price")
    food_per_head = models.PositiveIntegerField(
        help_text="Food cost per person",
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)  # 👈 REQUIRED

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    
class PlanFeature(models.Model):
    plan = models.ForeignKey(
        Plan,
        related_name='features',
        on_delete=models.CASCADE
    )
    feature = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.plan.name} - {self.feature}"
          
       
class tbl_payment(models.Model):
    booking = models.ForeignKey(tbl_booking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=15)

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(
        max_length=10,
        choices=[
            ('ADVANCE', 'Advance'),
            ('BALANCE', 'Balance')
        ]
    )

    status = models.CharField(max_length=20, default="SUCCESS")
    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tbl_payment"


class tbl_customizePlan(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )

    price = models.PositiveIntegerField(
        help_text="Addon price"
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    # Which plan tier this addon exclusively belongs to (e.g. Diamond).
    # Addons tagged to a plan are shown as upgrades for lower-tier plan users.
    plan = models.ForeignKey(
        'Plan',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='exclusive_addons',
        help_text="The plan tier this addon exclusively belongs to (e.g. Diamond)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} (₹{self.price})"
    




