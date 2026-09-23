# Task Tracker

## Windows installation

### Prerequisites

Install the following software:

- Python 3.10 or newer
- Git
- MySQL Server 8.0 or newer if you are using MySQL instead of SQLite

### 1. Open the project

Open PowerShell and move to the project directory:

```powershell
cd C:\Users\Dheeraj\Desktop\demoproject\task_tracker
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, allow locally created scripts for
your Windows user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For MySQL support, install the MySQL Python driver as well:

```powershell
pip install mysqlclient
```

### 4. Apply database migrations

For the default local SQLite database:

```powershell
python manage.py migrate
```

For MySQL, complete the [MySQL configuration](#mysql-configuration) first and
then run the same migration command.

### 5. Check the project

```powershell
python manage.py check
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Open the application at <http://127.0.0.1:8000/>.

To create a Django administrator account:

```powershell
python manage.py createsuperuser
```

The custom staff dashboard is available at
<http://127.0.0.1:8000/admin-dashboard/login/>.

## MySQL configuration

The project uses SQLite by default. To use MySQL, create a database and user,
install the MySQL driver, and configure the database through environment
variables.

### 1. Create the MySQL database

Open MySQL Command Line Client, MySQL Workbench, or a terminal connected to
your MySQL server and run:

```sql
CREATE DATABASE task_tracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER 'task_tracker_user'@'localhost'
    IDENTIFIED BY 'replace-with-a-strong-password';

GRANT ALL PRIVILEGES ON task_tracker.*
    TO 'task_tracker_user'@'localhost';

FLUSH PRIVILEGES;
```

Use a strong password and do not commit it to Git.

### 2. Install the MySQL driver on Windows

Activate the project's virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
pip install mysqlclient
```

If `mysqlclient` cannot be built on your machine, install the current
Microsoft C++ Build Tools and retry. The required workload is **Desktop
development with C++**.

### 3. Set database environment variables

The Django settings read these variables:

```powershell
$env:DB_ENGINE = "django.db.backends.mysql"
$env:DB_NAME = "task_tracker"
$env:DB_USER = "task_tracker_user"
$env:DB_PASSWORD = "replace-with-a-strong-password"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
```

These variables apply only to the current PowerShell window. Set them again
after opening a new terminal.

To set them persistently for the current Windows user, use:

```powershell
[Environment]::SetEnvironmentVariable("DB_ENGINE", "django.db.backends.mysql", "User")
[Environment]::SetEnvironmentVariable("DB_NAME", "task_tracker", "User")
[Environment]::SetEnvironmentVariable("DB_USER", "task_tracker_user", "User")
[Environment]::SetEnvironmentVariable("DB_PASSWORD", "replace-with-a-strong-password", "User")
[Environment]::SetEnvironmentVariable("DB_HOST", "127.0.0.1", "User")
[Environment]::SetEnvironmentVariable("DB_PORT", "3306", "User")
```

Restart PowerShell after setting persistent variables.

### 4. Verify the MySQL connection

From the project root, with the virtual environment activated:

```powershell
python manage.py check
python manage.py migrate
```

If both commands complete successfully, Django can connect to the configured
MySQL database and has created the required tables.

### Configuration notes

- `DB_ENGINE` must be exactly `django.db.backends.mysql`.
- Use `127.0.0.1` rather than `localhost` if your local MySQL setup has
  socket or name-resolution issues.
- Confirm that the MySQL service is running before starting Django.
- Do not commit passwords, secret keys, or `.env` files.
- The local SQLite file `db.sqlite3` is ignored by Git and is not used when
  `DB_ENGINE` is set to MySQL.
