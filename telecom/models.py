from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator

from core.validators import (
    validate_comma_separated_prefix_list_string,
    validate_semicolon_seperated_email_string,
)

from .storage import UUIDFileSystemStorage

uuid_file_system_storage = UUIDFileSystemStorage()


class File(models.Model):
    file = models.FileField(
        storage=uuid_file_system_storage,
        upload_to="telecom",
    )


class Isp(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=63)
    cname = models.CharField(verbose_name=_("Chinese Name"), max_length=63)
    customer_no = models.CharField(
        verbose_name=_("Customer No."), max_length=150, blank=True
    )
    upstream_as = models.CharField(verbose_name=_("Upstream AS"), max_length=63)
    primary_contact = models.CharField(verbose_name=_("Primary contact"), max_length=63)
    to = models.EmailField(
        verbose_name=_("To"),
        validators=[EmailValidator(message=_("Please enter a valid email address."))],
    )
    cc = models.TextField(
        verbose_name=_("CC"),
        blank=True,
        validators=[
            validate_semicolon_seperated_email_string,
        ],
    )
    bcc = models.TextField(
        verbose_name=_("BCC"),
        blank=True,
        validators=[
            validate_semicolon_seperated_email_string,
        ],
    )
    upstream_session_ip = models.TextField(
        verbose_name=_("Upstream Session IP"),
        blank=True,
        validators=[
            validate_comma_separated_prefix_list_string,
        ],
    )
    chief_session_ip = models.TextField(
        verbose_name=_("Chief Session IP"),
        blank=True,
        validators=[
            validate_comma_separated_prefix_list_string,
        ],
    )
    telephone = models.CharField(verbose_name=_("Telephone"), max_length=63, blank=True)
    cellphone = models.CharField(verbose_name=_("Cellphone"), max_length=63, blank=True)
    subject = models.TextField(verbose_name=_("Subject"), blank=True)
    content = models.TextField(verbose_name=_("Content"), blank=True)
    remark = models.TextField(verbose_name=_("Remark"), blank=True)
    eng_mail_type = models.BooleanField(verbose_name=_("English format"), default=False)
    created_by = models.ForeignKey(
        verbose_name=_("Created by"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("ISP")
        verbose_name_plural = _("ISPs")

    def __str__(self):
        return f"{self.name} ({self.cname})"

    def get_review_url(self):
        return reverse("telecom:isp_review", kwargs={"pk": self.pk})

    def get_create_url(self):
        return reverse("telecom:isp_create")

    def get_update_url(self):
        return reverse("telecom:isp_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("telecom:isp_delete", kwargs={"pk": self.pk})


class IspGroup(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=63)
    isps = models.ManyToManyField(verbose_name=_("ISPs"), to="telecom.Isp")
    remark = models.TextField(verbose_name=_("Remark"), blank=True)
    created_by = models.ForeignKey(
        verbose_name=_("Created by"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("ISP group")
        verbose_name_plural = _("ISP groups")

    def __str__(self):
        return self.name

    def get_create_url(self):
        return reverse("telecom:ispgroup_create")

    def get_update_url(self):
        return reverse("telecom:ispgroup_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("telecom:ispgroup_delete", kwargs={"pk": self.pk})


class PrefixListUpdateTask(models.Model):
    update_type = models.CharField(
        verbose_name=_("Update type"),
        max_length=63,
        choices=(
            ("add prefix-list", _("Add prefix-list")),
            ("delete prefix-list", _("Delete prefix-list")),
        ),
    )
    isps = models.ManyToManyField(verbose_name=_("ISPs"), to="telecom.Isp", blank=True)
    isp_groups = models.ManyToManyField(
        verbose_name=_("ISP groups"), to="telecom.IspGroup", blank=True
    )
    origin_as = models.CharField(verbose_name=_("Origin AS"), max_length=63)
    as_path = models.CharField(verbose_name=_("AS path"), max_length=63)
    ipv4_prefix_list = models.TextField(
        verbose_name=_("IPv4-Prefix-list"),
        validators=[
            validate_comma_separated_prefix_list_string,
        ],
    )
    ipv6_prefix_list = models.TextField(
        verbose_name=_("IPv6-Prefix-list"),
        validators=[
            validate_comma_separated_prefix_list_string,
        ],
    )
    subject_warning = models.CharField(
        verbose_name=_("Subject warning"), max_length=63, blank=True
    )
    related_ticket = models.CharField(
        verbose_name=_("Related ticket"), max_length=63, blank=True
    )
    roa = models.ManyToManyField(verbose_name=_("roa"), to="telecom.File", blank=True, related_name="roa_tasks")
    loa = models.ManyToManyField(verbose_name=_("loa"), to="telecom.File", blank=True, related_name="loa_tasks")
    loa_remark = models.TextField(verbose_name=_("Loa Remark"), blank=True)
    remark = models.TextField(verbose_name=_("Remark"), blank=True)
    meil_sended_time = models.CharField(
        verbose_name=_("Mail sended time"), max_length=63, blank=True
    )
    created_by = models.ForeignKey(
        verbose_name=_("Created by"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Prefix-list update task")
        verbose_name_plural = _("Prefix-list update tasks")

    def get_create_url(self):
        return reverse("telecom:prefixlistupdatetask_create")

    def get_update_url(self):
        return reverse("telecom:prefixlistupdatetask_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("telecom:prefixlistupdatetask_delete", kwargs={"pk": self.pk})

    def get_clone_url(self):
        return reverse("telecom:prefixlistupdatetask_clone", kwargs={"pk": self.pk})

    def preview_mail_content_url(self):
        return reverse(
            "telecom:prefixlistupdatetask_previewmailcontent", kwargs={"pk": self.pk}
        )

    def send_task_mail_url(self):
        return reverse(
            "telecom:prefixlistupdatetask_sendtaskmail", kwargs={"pk": self.pk}
        )
