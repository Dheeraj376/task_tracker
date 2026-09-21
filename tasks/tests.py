from datetime import date, timedelta

from django.test import TestCase

from .models import Task_Database


class TaskApiTests(TestCase):
    def valid_payload(self, **overrides):
        payload = {
            "task_name": "Write API tests",
            "task_description": "Cover the task endpoints",
            "task_assignee": "Dheeraj",
            "task_priority": "HIGH",
            "task_due_date": (date.today() + timedelta(days=1)).isoformat(),
        }
        payload.update(overrides)
        return payload

    def test_create_and_list_tasks(self):
        response = self.client.post(
            "/api/tasks/",
            self.valid_payload(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["task_status"], "TO_DO")

        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["tasks"]), 1)

    def test_update_and_delete_task(self):
        task = Task_Database.objects.create(
            **self.valid_payload(task_name="Existing task")
        )

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"task_status": "DONE"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task_status"], "DONE")

        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task_Database.objects.filter(id=task.id).exists())

    def test_invalid_task_returns_validation_errors(self):
        response = self.client.post(
            "/api/tasks/",
            self.valid_payload(
                task_due_date=(date.today() - timedelta(days=1)).isoformat()
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("task_due_date", response.json()["errors"])

    def test_list_supports_search_and_pagination(self):
        Task_Database.objects.create(
            **self.valid_payload(task_name="Prepare report")
        )
        Task_Database.objects.create(
            **self.valid_payload(task_name="Review report")
        )

        response = self.client.get("/api/tasks/?q=prepare&page=1&limit=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["tasks"]), 1)
        self.assertEqual(response.json()["tasks"][0]["task_name"], "Prepare report")
        self.assertEqual(response.json()["pagination"]["total"], 1)

    def test_invalid_list_parameters_return_helpful_errors(self):
        response = self.client.get("/api/tasks/?status=INVALID")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid status filter.")

        response = self.client.get("/api/tasks/?limit=101")

        self.assertEqual(response.status_code, 400)
        self.assertIn("limit must be between", response.json()["detail"])

    def test_malformed_json_is_rejected(self):
        response = self.client.post(
            "/api/tasks/",
            "{not-json}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Request body must contain valid JSON.",
        )


class TaskDashboardTests(TestCase):
    def test_dashboard_is_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task Tracker")
