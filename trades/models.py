from django.db import models
from django.utils.text import slugify

ABBREVIATION_BRIDGE = "BR"
ABBREVIATION_CONSTRUCTION = "CN"
ABBREVIATION_CONTACT_SYSTEM = "CS"
ABBREVIATION_DRAINAGE = "DR"
ABBREVIATION_OTHER = "OT"
ABBREVIATION_POWER_ENGINEERING = "PE"
ABBREVIATION_RAILWAY = "RL"
ABBREVIATION_RAILWAY_TRAFFIC = "RT"
ABBREVIATION_ROAD = "RD"
ABBREVIATION_TELECOMMUNICATION = "TL"


class Trade(models.Model):
    name = models.CharField(max_length=32)
    abbreviation = models.CharField(max_length=2, unique=True, default=ABBREVIATION_OTHER)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
