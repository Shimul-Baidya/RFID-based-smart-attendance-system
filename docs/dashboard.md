# Role-Based Dashboard Access

## 1. Feature Purpose

The Role-Based Dashboard Access feature provides users with a dashboard response based on their assigned role.

The current implementation supports four roles:

- Admin
- Teacher
- Staff
- Student

> Note: Authentication is not integrated yet. For the current development version, the user name and role are provided manually through query parameters. These will be replaced with the shared authentication dependency once it is finalized.

---

## 2. User Story

As an authenticated user, I want to access a dashboard based on my role so that I can see the actions and information relevant to my responsibilities.

---

## 3. Dashboard Endpoint

### GET `/dashboard/`

Returns a role-specific dashboard response.

### Request Example

```text
GET /dashboard/?user_name=Arpita&user_role=admin