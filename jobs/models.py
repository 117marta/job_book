from django.db import models

from jobs.consts import JobKinds, JobStatuses
from trades.models import Trade
from users.models import User


class Job(models.Model):
    principal = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs_principal")
    contractor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs_contractor")
    kind = models.CharField(max_length=16, choices=JobKinds.choices)
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE)
    description = models.TextField(max_length=1024)
    km_from = models.DecimalField(max_digits=7, decimal_places=3, default=0)
    km_to = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True)
    deadline = models.DateField()
    comments = models.TextField(max_length=512, blank=True)
    status = models.CharField(
        max_length=32, choices=JobStatuses.choices, default=JobStatuses.WAITING
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.trade}] {self.kind}: {self.description}"

    @property
    def is_waiting(self):
        return self.status == JobStatuses.WAITING

    @property
    def is_accepted(self):
        return self.status == JobStatuses.ACCEPTED

    @property
    def is_refused(self):
        return self.status == JobStatuses.REFUSED

    @property
    def is_making_documents(self):
        return self.status == JobStatuses.MAKING_DOCUMENTS

    @property
    def is_ready_to_stake_out(self):
        return self.status == JobStatuses.READY_TO_STAKE_OUT

    @property
    def is_ongoing(self):
        return self.status == JobStatuses.ONGOING

    @property
    def is_finished(self):
        return self.status == JobStatuses.FINISHED

    @property
    def is_closed(self):
        return self.status == JobStatuses.CLOSED
