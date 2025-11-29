# Task-Forge Backend

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Django-~4.x-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django Version">
  <img src="https://img.shields.io/badge/Django%20REST%20Framework-brightgreen?style=for-the-badge&logo=django&logoColor=white" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
</p>

## Project Overview

Task-Forge is the powerful backend API for a task management system. It's built with **Django** and **Django REST Framework** to provide a robust and scalable platform for managing projects and tasks. This API handles user authentication, project and task management, comments, and media uploads. It's fully containerized using Docker and PostgreSQL, making it easy to set up and deploy.

## Features ✨

* **Authentication**: Full user lifecycle management including registration, login, logout, password reset, and email verification.
* **Custom User Model**: Uses a custom user model with email as the username, supporting additional fields like job title and profile pictures.
* **Project Management**: Create projects with unique keys, assign industries, and manage team members.
* **Task Board**: A comprehensive task board with customizable statuses (**To Do**, **In Progress**, **Core Review**, **Done**), priorities, types, and due dates. Supports drag-and-drop reordering for seamless workflow management.
* **Comments**: Add and manage comments on individual tasks.
* **Permissions**: Granular permissions system where project owners and admins control member roles and access.
* **File Uploads**: Supports media uploads for user profile pictures.
* **CORS**: Configured to support Cross-Origin Resource Sharing for a frontend client.
* **Dockerized**: The entire application and its dependencies are containerized for consistent and isolated development and deployment environments.

---

## Technology Stack 🚀

The project is built using a modern, scalable tech stack.

* **Backend**: Python, Django, Django REST Framework, `dj-rest-auth`, `django-allauth`
* **Database**: PostgreSQL
* **Containerization**: Docker, Docker Compose
* **Email**: Gmail SMTP (for verification emails and password resets)

---

## Getting Started 🛠️

### Prerequisites

* **Docker** and **Docker Compose** installed.
* A **Gmail account** for sending emails with an app password configured.

### Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd task-forge/backend
    ```

2.  **Create a `media` directory**: This is where all file uploads will be stored.
    ```bash
    mkdir media
    ```

3.  **Configure environment variables**: Copy the example `.env` file and update the values with your own credentials and secret key.
    ```bash
    cp .env.example .env
    ```
    * `SECRET_KEY`: Generate a secure secret key.
    * `EMAIL_HOST_USER` & `EMAIL_HOST_PASSWORD`: Your Gmail address and the app password you created.
    * Update PostgreSQL credentials if necessary.

4.  **Build and start the containers**: This command will build the Docker images and start the backend and PostgreSQL containers.
    ```bash
    docker-compose up --build
    ```

5.  **Apply database migrations**:
    ```bash
    docker-compose exec backend python manage.py migrate
    ```

6.  **Create a superuser**: This is required to access the Django admin panel.
    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

---

## Usage Guide 🧭

* **API Root**: The main API is accessible at `http://localhost:8000/api/`.
* **Admin Panel**: The Django admin panel is at `http://localhost:8000/admin/`.

### Key Endpoints

* **Authentication**:
    * `POST /api/authentication/signup/` - Register a new user.
    * `POST /api/authentication/login/` - Authenticate a user.
    * `POST /api/authentication/logout/` - Log out.
    * `POST /api/authentication/password/reset/` - Trigger a password reset email.
* **User**:
    * `GET/PATCH /api/user/current/` - Retrieve or update the current user's profile.
* **Projects**:
    * `GET/POST /api/project/` - List or create new projects.
    * `GET/PUT/DELETE /api/project/<project_id>/` - Retrieve, update, or delete a specific project.
    * `GET/POST /api/project/<project_id>/users/` - View or add members to a project.
* **Tasks**:
    * `GET/POST /api/project/<project_id>/tasks/` - List or create new tasks within a project.
    * `GET/PUT/DELETE /api/project/<project_id>/tasks/<task_id>/` - Retrieve, update, or delete a specific task.
    * `GET/PATCH /api/project/<project_id>/tasks/board/` - Retrieve the task board or move a task on the board.
* **Comments**:
    * `GET/POST /api/project/<project_id>/tasks/<task_id>/comments/` - List or create comments on a task.
    * `GET/PUT/DELETE /api/project/<project_id>/tasks/<task_id>/comments/<comment_id>/` - Retrieve, update, or delete a specific comment.

---

## Development Notes 🗒️

* To stop the containers, use `docker-compose down`.
* For production, make sure to set `DEBUG=False` and use a more secure email backend.
* To run tests, use the command: `docker-compose exec backend python manage.py test`.

---

## License 📜

This project does not have a specified license. All rights belong to the repository owner.

---

## Support 🤝

If you encounter any issues or have questions, please feel free to open an issue on this GitHub repository.
