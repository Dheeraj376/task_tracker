import json

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Task_Database


EDITABLE_FIELDS = frozenset(
    (
        "task_name",
        "task_description",
        "task_assignee",
        "task_priority",
        "task_status",
        "task_due_date",
    )
)
REQUIRED_FIELDS = frozenset(
    ("task_name", "task_assignee", "task_priority", "task_due_date")
)
MAX_PAGE_SIZE = 100


def _creator_name(request):
    if request.user.is_authenticated:
        return request.user.username
    return "Anonymous"


def serialize_task(task):
    return {
        "id": task.id,
        "created_by": task.created_by,
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


def _error_response(detail, status=400, headers=None, **extra):
    return JsonResponse({"detail": detail, **extra}, status=status, headers=headers)


def _request_payload(request):
    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None, _error_response("Request body must contain valid JSON.")

    if not isinstance(payload, dict):
        return None, _error_response("Request body must be a JSON object.")
    return payload, None


def _apply_payload(task, payload, require_all=False):
    unknown_fields = sorted(set(payload) - EDITABLE_FIELDS)
    if unknown_fields:
        return _error_response(
            "Unknown fields.",
            fields=unknown_fields,
        )

    if require_all:
        missing_fields = sorted(REQUIRED_FIELDS - set(payload))
        if missing_fields:
            return _error_response(
                "Missing required fields.",
                fields=missing_fields,
            )

    for field in EDITABLE_FIELDS:
        if field in payload:
            value = payload[field]
            if isinstance(value, str):
                value = value.strip()
            setattr(task, field, value)
    return None


def _page_parameters(request):
    page_value = request.GET.get("page")
    limit_value = request.GET.get("limit")
    if page_value is None and limit_value is None:
        return None, None, None

    try:
        page = int(page_value or 1)
        limit = int(limit_value or 20)
    except ValueError:
        return None, None, _error_response("page and limit must be integers.")

    if page < 1 or limit < 1 or limit > MAX_PAGE_SIZE:
        return None, None, _error_response(
            f"page must be positive and limit must be between 1 and {MAX_PAGE_SIZE}."
        )
    return page, limit, None


def _list_response(tasks, request):
    page, limit, error_response = _page_parameters(request)
    if error_response:
        return error_response

    if page is None:
        return JsonResponse({"tasks": [serialize_task(task) for task in tasks]})

    total = tasks.count()
    start = (page - 1) * limit
    page_tasks = tasks[start:start + limit]
    return JsonResponse(
        {
            "tasks": [serialize_task(task) for task in page_tasks],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
        }
    )


@csrf_exempt
@login_required
def task_list(request):
    if request.method == "GET":
        tasks = Task_Database.objects.filter(created_by=_creator_name(request))
        status = request.GET.get("status")
        priority = request.GET.get("priority")
        sort = request.GET.get("sort", "asc")
        search = request.GET.get("q", "").strip()

        if status:
            if status not in Task_Database.Status.values:
                return _error_response("Invalid status filter.")
            tasks = tasks.filter(task_status=status)
        if priority:
            if priority not in Task_Database.Priority.values:
                return _error_response("Invalid priority filter.")
            tasks = tasks.filter(task_priority=priority)
        if search:
            tasks = tasks.filter(
                Q(task_name__icontains=search)
                | Q(task_description__icontains=search)
                | Q(task_assignee__icontains=search)
            )
        if sort not in {"asc", "desc"}:
            return _error_response("sort must be either 'asc' or 'desc'.")
        if sort == "desc":
            tasks = tasks.order_by("-task_due_date", "-id")
        else:
            tasks = tasks.order_by("task_due_date", "id")

        return _list_response(tasks, request)

    if request.method != "POST":
        return _error_response(
            "Method not allowed.",
            status=405,
            headers={"Allow": "GET, POST"},
        )

    payload, error_response = _request_payload(request)
    if error_response:
        return error_response

    task = Task_Database(
        created_by=(request.user.username if request.user.is_authenticated else "Anonymous")
    )
    error_response = _apply_payload(task, payload, require_all=True)
    if error_response:
        return error_response

    try:
        task.full_clean()
        task.save()
    except ValidationError as error:
        return _error_response(
            "Validation failed.",
            errors=_validation_errors(error),
        )

    return JsonResponse(serialize_task(task), status=201)


@csrf_exempt
@login_required
def task_detail(request, task_id):
    try:
        task = Task_Database.objects.get(
            id=task_id,
            created_by=_creator_name(request),
        )
    except Task_Database.DoesNotExist:
        return JsonResponse({"detail": "Task not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(serialize_task(task))

    if request.method == "DELETE":
        task.delete()
        return HttpResponse(status=204)

    if request.method not in {"PUT", "PATCH"}:
        return _error_response(
            "Method not allowed.",
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
        return _error_response(
            "Validation failed.",
            errors=_validation_errors(error),
        )

    return JsonResponse(serialize_task(task))
