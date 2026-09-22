
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import Task_Database


def login_page(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html", {"form": form})


def admin_login_page(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(request, "Invalid admin username or password.")

    return render(request, "admin_login.html")


@login_required(login_url="admin_login")
def admin_dashboard(request):
    if not request.user.is_staff:
        return render(request, "admin_access_denied.html", status=403)

    context = {
        "users": User.objects.order_by("username"),
        "tasks": Task_Database.objects.order_by("-task_created_at"),
        "user_count": User.objects.count(),
        "task_count": Task_Database.objects.count(),
    }
    return render(request, "admin_dashboard.html", context)


def sign_up(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password_confirmation = request.POST.get("password2", "")

        if not username or not email or not password:
            messages.error(request, "Username, email, and password are required.")
        elif password != password_confirmation:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "That username is already in use.")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            return redirect("login")

    return render(request, "registration/signup.html")


signup = sign_up


@login_required
def profile(request):
    user = request.user

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            user.first_name = request.POST.get("first_name", "").strip()
            user.last_name = request.POST.get("last_name", "").strip()
            user.email = request.POST.get("email", "").strip()
            user.save(update_fields=["first_name", "last_name", "email"])
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")

        if action == "change_password":
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("profile")
        else:
            password_form = PasswordChangeForm(user)
    else:
        password_form = PasswordChangeForm(user)

    return render(
        request,
        "registration/profile.html",
        {"password_form": password_form},
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def task_tracker_dashboard(request):

    # Get all tasks
    tasks = Task_Database.objects.filter(created_by=request.user.username)

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    status = request.GET.get("status", "ALL")

    if status != "ALL":
        tasks = tasks.filter(
            task_status=status
        )

    # --------------------------------------------------------
    # PRIORITY FILTER
    # --------------------------------------------------------

    priority = request.GET.get("priority", "ALL")

    if priority != "ALL":
        tasks = tasks.filter(
            task_priority=priority
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    sort = request.GET.get("sort", "asc")

    if sort == "desc":
        tasks = tasks.order_by(
            "-task_due_date"
        )
    else:
        tasks = tasks.order_by(
            "task_due_date"
        )

    # --------------------------------------------------------
    # COUNTS
    # --------------------------------------------------------

    total_tasks = Task_Database.objects.filter(
        created_by=request.user.username
    ).count()

    todo_count = Task_Database.objects.filter(
        created_by=request.user.username,
        task_status=Task_Database.Status.TO_DO
    ).count()

    in_progress_count = Task_Database.objects.filter(
        created_by=request.user.username,
        task_status=Task_Database.Status.IN_PROGRESS
    ).count()

    done_count = Task_Database.objects.filter(
        created_by=request.user.username,
        task_status=Task_Database.Status.DONE
    ).count()

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        "tasks": tasks,

        "total_tasks": total_tasks,
        "todo_count": todo_count,
        "in_progress_count": in_progress_count,
        "done_count": done_count,

        "current_status": status,
        "current_priority": priority,
        "current_sort": sort,
    }

    return render(
        request,
        "task_tracker_dashboard.html",
        context
    )


# ============================================================
# CREATE TASK
# ============================================================

@login_required
def create_task(request):

    if request.method == "POST":

        task = Task_Database(
            created_by=request.user.username,
            task_name=request.POST.get(
                "task_name",
                ""
            ).strip(),

            task_description=request.POST.get(
                "task_description",
                ""
            ).strip(),

            task_assignee=request.POST.get(
                "task_assignee",
                ""
            ).strip(),

            task_priority=request.POST.get(
                "task_priority",
                ""
            ).strip(),

            # Do NOT send status here.
            # Model default will set TO_DO.

            task_due_date=request.POST.get(
                "task_due_date",
                ""
            )
        )

        try:

            task.full_clean()
            task.save()

            messages.success(
                request,
                "Task created successfully."
            )

        except ValidationError as error:

            print("Create Task Error:", error)

            messages.error(
                request,
                "Please enter valid task details."
            )

    return redirect("dashboard")


# ============================================================
# EDIT TASK
# ============================================================

@login_required
def edit_task(request, task_id):

    task = get_object_or_404(
        Task_Database,
        id=task_id,
    )

    if request.method == "POST":

        task.task_name = request.POST.get(
            "task_name",
            ""
        ).strip()

        task.task_description = request.POST.get(
            "task_description",
            ""
        ).strip()

        task.task_assignee = request.POST.get(
            "task_assignee",
            ""
        ).strip()

        task.task_priority = request.POST.get(
            "task_priority",
            ""
        ).strip()

        task.task_status = request.POST.get(
            "task_status",
            Task_Database.Status.TO_DO
        ).strip()

        task.task_due_date = request.POST.get(
            "task_due_date",
            ""
        )

        try:

            task.full_clean()
            task.save()

            messages.success(
                request,
                "Task updated successfully."
            )

        except ValidationError as error:

            print("Edit Task Error:", error)

            messages.error(
                request,
                "Please enter valid task details."
            )

    return redirect("dashboard")


# ============================================================
# DELETE TASK
# ============================================================

@login_required
def delete_task(request, task_id):

    task = get_object_or_404(
        Task_Database,
        id=task_id,
    )

    if request.method == "POST":

        task.delete()

        messages.success(
            request,
            "Task deleted successfully."
        )

    return redirect("dashboard")

