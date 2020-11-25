from datetime import datetime

import flask_admin as admin
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin import expose
from flask_admin import helpers
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from peewee import DoesNotExist
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from afpy.forms.auth import ChangePasswordForm
from afpy.forms.auth import LoginForm
from afpy.forms.auth import RegistrationForm
from afpy.models.AdminUser import AdminUser
from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry


# Create customized index view class that handles login & registration
class AdminIndexView(admin.AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(AdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            try:
                user = AdminUser.get(AdminUser.email == form.email_or_username.data)
            except DoesNotExist:
                user = AdminUser.get(AdminUser.username == form.email_or_username.data)
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(AdminIndexView, self).index()

    @expose("/register/", methods=("GET", "POST"))
    def register_view(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            AdminUser.create(
                email=form.email.data,
                username=form.username.data,
                password=generate_password_hash(form.password.data),
                dt_added=datetime.now(),
            ).save()
            return redirect(url_for(".index"))
        return self.render("admin/create_user.html", form=form)

    @expose("/change_password", methods=("GET", "POST"))
    def change_password_view(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = ChangePasswordForm(request.form)
        if helpers.validate_form_on_submit(form):
            if not check_password_hash(current_user.password, form.old_password.data):
                flash("Incorrect old password.")
                return self.render("admin/change_password.html", form=form)
            if not form.new_password == form.new_password_confirmation:
                flash("Passwords don't match.")
                return self.render("admin/change_password.html", form=form)
            current_user.password = generate_password_hash(form.new_password.data)
            return redirect(url_for(".index"))
        return self.render("admin/change_password.html", form=form)

    @expose("/moderate/<type>", methods=["GET"])
    def moderate_view(self, type):
        if not current_user.is_authenticated:
            return redirect(url_for(".index"))
        if type == "jobs":
            jobs = JobPost.select().where(JobPost.state == "waiting").order_by(JobPost.dt_submitted.desc())
            return self.render("admin/moderate_view.html", items=jobs, type=type)
        elif type == "news":
            news = NewsEntry.select().where(NewsEntry.state == "waiting").order_by(NewsEntry.dt_submitted.desc())
            return self.render("admin/moderate_view.html", items=news, type=type)
        else:
            flash("Wrong type")
            return redirect(url_for(".index"))

    @expose("/preview/<type>/<id>", methods=["GET"])
    def preview_item(self, type, id):
        if not current_user.is_authenticated:
            return redirect(url_for(".index"))
        if type == "job":
            job = JobPost.get_by_id(id)
            return self.render("pages/job.html", job=job, preview=True)
        elif type == "news":
            news = NewsEntry.get_by_id(id)
            return self.render("pages/post.html", post=news, preview=True)
        else:
            flash("Wrong type")
            return redirect(url_for(".index"))

    @expose("/moderate/action/<id>/<type>/<action>", methods=["GET"])
    def moderate_action(self, id, type, action):
        if not current_user.is_authenticated:
            return redirect(url_for(".index"))
        if type == "job":
            item = JobPost.get_by_id(id)
        elif type == "news":
            item = NewsEntry.get_by_id(id)
        else:
            flash("Wrong type")
            return redirect(url_for(".index"))
        if action == "approve":
            item.state = "published"
            item.approved_by = current_user.id
            item.dt_published = datetime.now()
            item.save()
        elif action == "reject":
            item.state = "rejected"
            item.approved_by = current_user.id
            item.save()
        else:
            flash("Wrong action type")
            return redirect(url_for(".index"))
        return redirect(url_for(".moderate_view", type=type))

    @expose("/logout/")
    def logout_view(self):
        logout_user()
        return redirect(url_for(".index"))
