
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Task_Database


# ============================================================
# DASHBOARD
# ============================================================

def task_tracker_dashboard(request):

    # Get all tasks
    tasks = Task_Database.objects.all()

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

    total_tasks = Task_Database.objects.count()

    todo_count = Task_Database.objects.filter(
        task_status=Task_Database.Status.TO_DO
    ).count()

    in_progress_count = Task_Database.objects.filter(
        task_status=Task_Database.Status.IN_PROGRESS
    ).count()

    done_count = Task_Database.objects.filter(
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

def create_task(request):

    if request.method == "POST":

        task = Task_Database(
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

def edit_task(request, task_id):

    task = get_object_or_404(
        Task_Database,
        id=task_id
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

def delete_task(request, task_id):

    task = get_object_or_404(
        Task_Database,
        id=task_id
    )

    if request.method == "POST":

        task.delete()

        messages.success(
            request,
            "Task deleted successfully."
        )

    return redirect("dashboard")

