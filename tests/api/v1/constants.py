API_V1_PREFIX = "/api/v1"

# Auth
LOGIN_URL = f"{API_V1_PREFIX}/auth/login"
LOGOUT_URL = f"{API_V1_PREFIX}/auth/logout"
REGISTER_URL = f"{API_V1_PREFIX}/auth/register"
REFRESH_URL = f"{API_V1_PREFIX}/auth/refresh"
CHANGE_PASSWORD_URL = f"{API_V1_PREFIX}/auth/change-password"

# Users & Profiles
PROFILES_URL = f"{API_V1_PREFIX}/users/me"

# Resources
WORKSPACES_URL = f"{API_V1_PREFIX}/workspaces"
PROJECTS_URL = f"{API_V1_PREFIX}/projects"
TASKS_URL = f"{API_V1_PREFIX}/tasks"
LABELS_URL = f"{API_V1_PREFIX}/labels"
COMMENTS_URL = f"{API_V1_PREFIX}/comments"
