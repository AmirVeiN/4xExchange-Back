from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from user.models import ChangePasswordEmailConfirmation, EmailCode


@shared_task
def delete_email_code(pk, code):

    instance1 = PeriodicTask.objects.filter(name__startswith=f"Delete_EmailCode_{code}")
    for task in instance1:
        task.delete()

    instance2 = ChangePasswordEmailConfirmation.objects.filter(code=code)
    for task in instance2:
        task.delete()


@shared_task
def delete_email_code_verification(pk, code):

    instance1 = PeriodicTask.objects.filter(
        name__startswith=f"Delete_UserEmailCode_{code}"
    )
    for task in instance1:
        task.delete()

    instance2 = EmailCode.objects.filter(code=code)
    for task in instance2:
        task.delete()
