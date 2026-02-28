from django.db import models
from django.conf import settings
from django.core import validators

def get_currencies():
    return {i: i for i in settings.CURRENCIES}

def get_timezones():
    return {i: i for i in settings.TIMEZONES}

# Create your models here.

class Platform(models.Model):
    TYPE_OF_PLATFORM = [
        ("telegram", "Telegram"),
        ("youtube", "YouTube"),
        ("facebook", "Facebook"),
        ("website", "Website"),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_OF_PLATFORM)
    description = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=get_currencies(), default="USD")
    timezone = models.CharField(max_length=50, choices=get_timezones(), default="Europe/Sofia")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
class Client(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    vat_number = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["email", "is_active"]),
        ]

    def __str__(self):
        return self.name or self.email

class PriceList(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default="Europe/Sofia")
    default_slot_duration = models.PositiveSmallIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["platform", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.platform})"

# PromoCode model based on Laravel validation structure
class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percent", "Percent"),
        ("fixed", "Fixed"),
    ]
    APPLIES_TO_CHOICES = [
        ("global", "Global"),
        ("platform", "Platform"),
        ("price_list", "Price List"),
    ]

    code = models.CharField(max_length=64, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_client = models.PositiveIntegerField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applies_to = models.CharField(max_length=10, choices=APPLIES_TO_CHOICES)
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)
    price_list = models.ForeignKey(PriceList, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    is_stackable = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class Slot(models.Model):
    SLOT_STATUS = models.TextChoices("available","reserved","booked","cancelled")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    pricelist = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    price = models.FloatField()
    status = models.CharField(choices=SLOT_STATUS, max_length=10, default="available")
    capacity = models.IntegerField(default=1)
    used_capacity = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["platform", "starts_at", "status"]),
        ]

    def __str__(self):
        return f"Slot {self.id} - {self.platform} - {self.starts_at}"
        
class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, null=True, blank=True, on_delete=models.SET_NULL)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    promo_code = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.status}"

class PromoRedemption(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["promo_code", "client"]),
        ]

    def __str__(self):
        return f"{self.promo_code} redeemed by {self.client}"

class PriceListRule(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    weekday = models.IntegerField(
        null=True,
        blank=True,
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(7)],
    )
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    slot_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(
        validators=[validators.MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["price_list", "weekday", "is_active"]),
        ]

    def __str__(self):
        return f"Rule {self.price_list} {self.weekday} {self.starts_at}-{self.ends_at}"

class PriceOverride(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE)
    for_date = models.DateField()
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    slot_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("price_list", "for_date", "starts_at", "ends_at")

    def __str__(self):
        return f"Override {self.for_date} {self.starts_at}-{self.ends_at}"

