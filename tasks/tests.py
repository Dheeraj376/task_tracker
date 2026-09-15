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
