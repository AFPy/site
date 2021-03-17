from datetime import datetime
from typing import Optional

from flask_admin.contrib.peewee import ModelView
from flask_login import current_user
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import TextField

from afpy.models import BaseModel
from afpy.models.AdminUser import AdminUser


class JobPost(BaseModel):
    title = TextField(null=False, help_text="Title of the job post", verbose_name="Title")
    summary = TextField(null=True, help_text="Summary of the job post", verbose_name="Summary")
    content = TextField(null=False, help_text="Content of the job post", verbose_name="Content")
    dt_submitted = DateTimeField(
        null=False,
        default=datetime.now,
        help_text="When was the job post submitted",
        verbose_name="Datetime Submitted",
        index=True,
    )
    dt_updated = DateTimeField(
        null=False, default=datetime.now, help_text="When was the job post updated", verbose_name="Datetime Updated"
    )
    dt_published = DateTimeField(
        null=True, help_text="When was the job post published", verbose_name="Datetime Published"
    )
    state = CharField(
        null=False,
        default="waiting",
        choices=[("waiting", "waiting"), ("published", "published"), ("rejected", "rejected")],
        help_text="Current state of the job post",
        verbose_name="State",
    )
    approved_by = ForeignKeyField(
        AdminUser,
        null=True,
        default=None,
        backref="adminuser",
        help_text="Who approved the job post",
        verbose_name="Approved by",
    )

    company = CharField(null=False, help_text="Company that posted the job", verbose_name="Company")
    phone = CharField(null=True, help_text="Phone number to contact", verbose_name="Phone Number")
    location = CharField(null=False, help_text="Where is the job located", verbose_name="Job Location")
    email = CharField(null=True, help_text="Email to contact", verbose_name="Email Address")
    contact_info = CharField(null=False, help_text="Person to contact", verbose_name="Contact info")
    image_path = CharField(null=True, help_text="Image for the job post", verbose_name="Image Path in filesystem")

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        company: str,
        location: str,
        contact_info: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        summary: Optional[str] = None,
        dt_submitted: Optional[datetime] = None,
        dt_updated: Optional[datetime] = None,
        dt_published: Optional[datetime] = None,
        state: str = "waiting",
        approved_by: Optional[AdminUser] = None,
        image_path: Optional[str] = None,
    ):
        if not dt_submitted:
            dt_submitted = datetime.now()
        if not dt_updated:
            dt_updated = datetime.now()

        if not email and not phone:
            raise ValueError("One of email or phone must be provided")

        new_job = super().create(
            title=title,
            content=content,
            company=company,
            location=location,
            contact_info=contact_info,
            email=email,
            phone=phone,
            summary=summary,
            dt_submitted=dt_submitted,
            dt_updated=dt_updated,
            dt_published=dt_published,
            state=state,
            approved_by=approved_by,
            image_path=image_path,
        )
        new_job.save()
        return new_job


class JobPost_Admin(ModelView):
    model_class = JobPost

    def is_accessible(self):
        return current_user.is_authenticated


if not JobPost.table_exists():
    JobPost.create_table()
