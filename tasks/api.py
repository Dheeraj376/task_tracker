import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Task_Database


EDITABLE_FIELDS = (
    "task_name",
    "task_description",
    "task_assignee",
    "task_priority",
    "task_status",
    "task_due_date",
)


def serialize_task(task):
    return {
        "id": task.id,
        "task_name": task.task_name,
        "task_description": task.task_description,
        "task_assignee": task.task_assignee,
        "task_priority": task.task_priority,
        "task_status": task.task_status,
        "task_due_date": task.task_due_date.isoformat(),
        "task_created_at": task.task_created_at.isoformat(),
    }


def _validation_errors(error):
    if hasattr(error, "message_dict"):
        return error.message_dict
    return {"detail": error.messages}


def _request_payload(request):
    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None, JsonResponse(
            {"detail": "Request body must contain valid JSON."},
            status=400,
        )

    if not isinstance(payload, dict):
        return None, JsonResponse(
            {"detail": "Request body must be a JSON object."},
            status=400,
        )
    return payload, None


def _apply_payload(task, payload, require_all=False):
    unknown_fields = sorted(set(payload) - set(EDITABLE_FIELDS))
    if unknown_fields:
        return JsonResponse(
            {"detail": "Unknown fields.", "fields": unknown_fields},
            status=400,
        )

    required_fields = {"task_name", "task_assignee", "task_priority", "task_due_date"}
    if require_all:
        missing_fields = sorted(required_fields - set(payload))
        if missing_fields:
            return JsonResponse(
                {"detail": "Missing required fields.", "fields": missing_fields},
                status=400,
            )

    for field in EDITABLE_FIELDS:
        if field in payload:
            value = payload[field]
            if isinstance(value, str):
                value = value.strip()
            setattr(task, field, value)
    return None


@csrf_exempt
def task_list(request):
    if request.method == "GET":
        tasks = Task_Database.objects.all()
        status = request.GET.get("status")
        priority = request.GET.get("priority")
        sort = request.GET.get("sort", "asc")

        if status:
            tasks = tasks.filter(task_status=status)
        if priority:
            tasks = tasks.filter(task_priority=priority)
        if sort == "desc":
            tasks = tasks.order_by("-task_due_date", "-id")
        else:
            tasks = tasks.order_by("task_due_date", "id")

        return JsonResponse({"tasks": [serialize_task(task) for task in tasks]})

    if request.method != "POST":
        return JsonResponse(
            {"detail": "Method not allowed."},
            status=405,
            headers={"Allow": "GET, POST"},
        )

    payload, error_response = _request_payload(request)
    if error_response:
        return error_response

    task = Task_Database()
    error_response = _apply_payload(task, payload, require_all=True)
    if error_response:
        return error_response

    try:
        task.full_clean()
        task.save()
    except ValidationError as error:
        return JsonResponse({"errors": _validation_errors(error)}, status=400)

    return JsonResponse(serialize_task(task), status=201)


@csrf_exempt
def task_detail(request, task_id):
    try:
        task = Task_Database.objects.get(id=task_id)
    except Task_Database.DoesNotExist:
        return JsonResponse({"detail": "Task not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(serialize_task(task))

    if request.method == "DELETE":
        task.delete()
        return HttpResponse(status=204)

    if request.method not in {"PUT", "PATCH"}:
        return JsonResponse(
            {"detail": "Method not allowed."},
            status=405,
            headers={"Allow": "GET, PUT, PATCH, DELETE"},
        )

    payload, error_response = _request_payload(request)
    if error_response:
        return error_response

    error_response = _apply_payload(
        task,
        payload,
        require_all=request.method == "PUT",
    )
    if error_response:
        return error_response

    try:
        task.full_clean()
        task.save()
    except ValidationError as error:
        return JsonResponse({"errors": _validation_errors(error)}, status=400)

    return JsonResponse(serialize_task(task))
