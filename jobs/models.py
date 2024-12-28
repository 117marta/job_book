import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from jobs.consts import JobKinds, JobStatuses
from trades.models import Trade
from users.models import User

JOBS_CONCLUDED_STATUSES = [JobStatuses.CLOSED, JobStatuses.FINISHED, JobStatuses.REFUSED]


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

    @property
    def get_job_files(self):
        return JobFile.objects.filter(content_type__model="job", object_id=self.pk)

    @property
    def has_attachments(self):
        return self.get_job_files.exists()


def job_file_directory(instance, filename):
    get_path = getattr(instance, "get_path")
    return get_path(filename)


class FileBase(models.Model):
    file = models.FileField(upload_to=job_file_directory, max_length=1024, blank=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default="")
    object_id = models.PositiveIntegerField(default=None, null=True)
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    file_name = ""
    last_download = models.DateTimeField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "file_name"):
            raise NotImplementedError(
                "Subclasses of FileBase must provide a `file_name` attribute!"
            )

    def get_path(self, name):
        raise NotImplementedError("Subclasses of FileBase must provide a `get_path` method!")

    class Meta:
        abstract = True


class JobFile(FileBase):
    file_name = "jobfiles"

    def get_path(self, name):
        path = os.path.join(self.file_name, f"job_{self.object_id:06d}")
        return os.path.join(path, name)
