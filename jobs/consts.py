from django.db import models


class JobKinds(models.TextChoices):
    STAKING = "staking", "staking out"
    INVENTORY = "inventory", "as-built inventory"
    OTHER = "other", "other"


class JobStatuses(models.TextChoices):
    WAITING = "waiting", "waiting"
    ACCEPTED = "accepted", "accepted"
    REFUSED = "refused", "refused"
    MAKING_DOCUMENTS = "making_documents", "making documents"
    READY_TO_STAKE_OUT = "ready_to_stake_out", "ready to stake out"
    ONGOING = "ongoing", "ongoing"
    FINISHED = "finished", "finished"
    CLOSED = "closed", "closed"


JOBS_PER_PAGE = 10

KM_HELP_TEXT = "Use , or . as a separator"
JOB_CREATE_SUCCESS_MESSAGE = "The job has been created!"
