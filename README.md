# Task Tracker

A web-based Task Tracker application developed using **Python and Django**, with **MySQL** as the database and **HTML, CSS, and JavaScript** for the frontend. The application allows users to create, view, update, and manage tasks through a simple and user-friendly interface.

## Technologies Used

* **Python** – Backend programming and application logic
* **Django** – Web framework for developing the backend
* **MySQL** – Database for storing task information
* **HTML** – Web page structure
* **CSS** – User interface styling and layout
* **JavaScript** – Client-side interactions
* **Git & GitHub** – Version control and project management

## Key Features

* Create and add new tasks
* View and manage existing tasks
* Update task details
* Delete tasks
* Task status management using radio buttons
* Store task information in MySQL
* Django-based backend with database integration
* Simple and responsive user interface

## REST API

The task collection is available as JSON at `/api/tasks/`.

* `GET /api/tasks/` - list tasks. Optional `status`, `priority`, and `sort=desc` query parameters are supported.
* `POST /api/tasks/` - create a task.
* `GET /api/tasks/<id>/` - retrieve a task.
* `PUT /api/tasks/<id>/` - replace a task.
* `PATCH /api/tasks/<id>/` - partially update a task.
* `DELETE /api/tasks/<id>/` - delete a task.

Create and update requests must send a JSON object with `task_name`, `task_assignee`,
`task_priority`, and `task_due_date`. `task_description` and `task_status` are optional.

## Project Purpose

The purpose of this project is to provide a simple and efficient way to organize and manage daily tasks while demonstrating practical knowledge of **Python, Django, database management, frontend development, and Git/GitHub**.