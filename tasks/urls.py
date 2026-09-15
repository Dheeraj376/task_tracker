from django.urls import path

from .views import (
    task_tracker_dashboard,
    create_task,
    edit_task,
    delete_task,
)
from .api import task_detail, task_list


urlpatterns = [
    path(
        "api/tasks/",
        task_list,
        name="api_task_list",
    ),

    path(
        "api/tasks/<int:task_id>/",
        task_detail,
        name="api_task_detail",
    ),

    path(
        "",
        task_tracker_dashboard,
        name="dashboard"
    ),

    path(
        "task/create/",
        create_task,
        name="create_task"
    ),

    path(
        "task/edit/<int:task_id>/",
        edit_task,
        name="edit_task"
    ),

    path(
        "task/delete/<int:task_id>/",
        delete_task,
        name="delete_task"
    ),
]