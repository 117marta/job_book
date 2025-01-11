from django.db import models


# TextChoices
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
    DATA_PASSED = "data_passed", "data passed"
    ONGOING = "ongoing", "ongoing"
    FINISHED = "finished", "finished"
    CLOSED = "closed", "closed"


# Constants
JOBS_PER_PAGE = 10


# Forms
KM_HELP_TEXT = "Use , or . as a separator"
DEADLINE_FORM_ERROR = "A date from the past was given"


# Views
JOB_CREATE_SUCCESS_MESSAGE = "The job has been created!"
JOB_SAVE_SUCCESS_MESSAGE = "The job has been saved!"
JOB_ROLE_CONTRACTOR = "contractor"
JOB_ROLE_PRINCIPAL = "principal"


# E-mails
EMAIL_JOB_CREATE_SUBJECT = "A new job has been just created and assigned to you"
EMAIL_JOB_CREATE_CONTENT = "A new job has been just created by {} in the {} trade. Check the details and accept or reject this job."
EMAIL_JOB_CHANGE_STATUS_SUBJECT = "The job number {} has changed status"
EMAIL_JOB_CHANGE_STATUS_CONTENT = "The job number {job_pk} has changed status to <strong>{status}</strong>. Check the details here <a href={url}>[CLICK]</a>"
EMAIL_JOB_CHANGE_CONTRACTOR_SUBJECT = "The job number {} has been assigned to you"
EMAIL_JOB_CHANGE_CONTRACTOR_CONTENT = "The job number {job_pk} in the {trade} trade has been assigned to you. Check the details here <a href={url}>[CLICK]</a>"
EMAIL_JOB_UPCOMING_DEADLINE_SUBJECT = "Tomorrow is the deadline for the job number {}."
EMAIL_JOB_UPCOMING_DEADLINE_CONTENT = (
    "Tomorrow is the deadline for the job number {}. Remember to finish your work."
)
EMAIL_JOB_OVERDUE_DEADLINE_SUBJECT = "Your job number {} has not been completed."
EMAIL_JOB_OVERDUE_DEADLINE_CONTENT = "The deadline for the job number {} has passed and it not has been completed. Contact the Contractor to arrange the details."
EMAIL_JOB_MONTHLY_STATUS_SUBJECT = "Jobs Monthly Status"
EMAIL_JOB_MONTHLY_STATUS_CONTENT = "Monthly statistics for the year <strong>{year}</strong>, month <strong>{month}</strong> are in the attachment"
