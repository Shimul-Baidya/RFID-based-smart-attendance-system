===========================
Authentication API Contract
===========================

Feature Owner
=============

Shimul Baidya

Source Requirements
===================

- SRS Section 3.1: User Authentication
- SRS Section 3.1.1: Password Management
- SRS Section 3.1.3: Token-based Access Control

User Story
==========

As a registered user, I want to log in securely with my credentials so that I can receive an access token to access protected system features.

Confirmed Auth Interface
========================

The following interface has been implemented for authentication:

- User model: ``app/models/user.py``
- User primary key: ``User.id``
- Username field: ``User.username``
- Password hashing: Handled via ``pwdlib`` using argon2
- JWT Generation: Handled via ``PyJWT``

Authentication Validation Rules
===============================

The authentication service shall validate the login in this order:

1. Validate that the request contains a username and password.
2. Look up the user associated with the provided username.
3. If the user does not exist, perform a dummy hash verification to mitigate timing attacks and return an error.
4. Verify the provided password against the stored password hash.
5. If the password does not match, return an error.
6. Generate a JSON Web Token (JWT) containing the username as the subject.
7. Return the token.

Proposed Endpoints
==================

POST /token
-----------

Handles user login and token generation.

**Proposed Request:**

.. code-block:: http

    POST /token
    Content-Type: application/x-www-form-urlencoded

    username=testuser&password=securepassword

**Successful Response:**

HTTP status: ``200 OK``

.. code-block:: json

    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }

**Rejection Response (Invalid Credentials):**

HTTP status: ``401 Unauthorized``

.. code-block:: json

    {
      "detail": "Incorrect username or password"
    }

GET /users/me
-------------

Retrieves the currently authenticated user's profile.

**Successful Response:**

HTTP status: ``200 OK``

.. code-block:: json

    {
      "username": "testuser",
      "email": "testuser@example.com",
      "role": "student",
      "id": 1,
      "status": "active",
      "email_verified_at": null,
      "last_login_at": null,
      "created_at": "2026-08-25T21:30:00+06:00",
      "updated_at": "2026-08-25T21:30:00+06:00"
    }

Initial Required Tests
======================

- Successful login returns a valid JWT.
- Login with an incorrect password is rejected with a 401.
- Login with an unknown username is rejected with a 401.
- Accessing a protected route with a valid token succeeds.
- Accessing a protected route without a token is rejected with a 401.

Open Questions for Scrum Meeting
================================

1. How long should the access token expire (currently defaults to 30 minutes)?
2. Do we need to implement refresh tokens for this project?
3. Should we log failed login attempts to the audit logs?

Document Status
===============

This is a proposed Sprint 1 contract for Authentication. Token expiration times and refresh token requirements must be confirmed during the Scrum meeting.

