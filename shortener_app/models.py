
from django.db import models
import string
import random

def generate_short_code():
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(6))
        if not URL.objects.filter(short_code=short_code).exists():
            return short_code

class URL(models.Model):
    url_title = models.CharField(max_length=600 , blank=True , null=True)
    long_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=6, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk and not self.short_code:
            self.short_code = generate_short_code()
        super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.short_code} -> {self.long_url}"
        
    
class SiteConfiguration(models.Model):
        ads_enabled_globally = models.BooleanField(default=True) # Global toggle for ads
    
        class Meta:
            verbose_name = "Site Configuration"
            verbose_name_plural = "Site Configuration" # To show "Site Configuration" in admin, not "Site Configurations"
    
        def save(self, *args, **kwargs):
            # Ensure that there's always only one instance of this model.
            # This prevents accidental creation of multiple global config objects.
            if self.pk is None and SiteConfiguration.objects.exists():
                # If an instance already exists and this is a new one, update the existing one
                existing_config = SiteConfiguration.objects.first()
                existing_config.ads_enabled_globally = self.ads_enabled_globally
                super(SiteConfiguration, existing_config).save(*args, **kwargs)
            else:
                super().save(*args, **kwargs)
    
        def __str__(self):
            return "Global Site Configuration"

class AdUnit(models.Model):
    AD_LOCATIONS = [
        ('waiting_top', 'Waiting Page - Top (Ad 1)'),
        ('waiting_bottom', 'Waiting Page - Bottom (Ad 2)'),
        # Add more locations as your site grows
        # ('homepage_sidebar', 'Homepage - Sidebar'),
        # ('after_form', 'Shorten Page - After Form'),
    ]

    name = models.CharField(max_length=100, help_text="A descriptive name for this ad unit (e.g., 'Google AdSense 300x250 - Waiting Top')")
    ad_code = models.TextField(help_text="Paste the full HTML/JavaScript ad code here (e.g., AdSense, PropellerAds).")
    location = models.CharField(
        max_length=50,
        choices=AD_LOCATIONS,
        default='waiting_top',
        help_text="Where this ad unit should be displayed on the site."
    )
    is_active = models.BooleanField(default=True, help_text="Check to enable this ad unit.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ad Unit"
        verbose_name_plural = "Ad Units"
        ordering = ['location', '-created_at'] # Order by location, then by newest first

    def __str__(self):
        return f"{self.name} ({self.get_location_display()})" # get_location_display() gives the human-readable choice