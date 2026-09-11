from django.urls import path

from .views import (
    task_tracker_dashboard,
    create_task,
    edit_task,
    delete_task,
)


urlpatterns = [

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