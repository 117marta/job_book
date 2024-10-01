from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from trades.models import Trade
from users.managers import UserManager


CONTRACT_DIRECTOR = "contract_director"
CONTRACT_MANAGER = "contract_manager"
CLERK_OF_THE_WORKS = "clerk_of_the_works"
SITE_MANAGER = "site_manager"
SITE_ENGINEER = "site_engineer"
SUBCONTRACTOR = "subcontractor"
SURVEYOR = "surveyor"

ROLES = (
    (CONTRACT_DIRECTOR, "Contract director"),
    (CONTRACT_MANAGER, "Contract manager"),
    (CLERK_OF_THE_WORKS, "Clerk of the works"),
    (SITE_MANAGER, "Site manager"),
    (SITE_ENGINEER, "Site engineer"),
    (SUBCONTRACTOR, "Subcontractor"),
    (SURVEYOR, "Surveyor"),
)

GENERAL_CONTRACTOR = (
    CONTRACT_DIRECTOR,
    CONTRACT_MANAGER,
    CLERK_OF_THE_WORKS,
    SITE_MANAGER,
    SITE_ENGINEER,
)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('first name'), max_length=32, blank=True)
    last_name = models.CharField(_('last name'), max_length=64, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    role = models.CharField(_("staff role"), max_length=32, choices=ROLES)
    phone = models.CharField(_("phone"), max_length=16)
    trade = models.ManyToManyField(to=Trade, related_name="users")
    birth_date = models.DateField(_("date of birth"), blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an e-mail to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
