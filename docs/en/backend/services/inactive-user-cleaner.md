# `services/inactive_user_cleaner.py` - Inactive User Cleaner Service

This document describes the `backend/app/services/inactive_user_cleaner.py` file, which contains the business logic for periodically cleaning up unactivated user accounts.

## Function Description
*   **Periodic Cleanup**: Automatically deletes user accounts that have not been activated within a specified period.
*   **Data Maintenance**: Helps manage database size, improve system security, and clean up invalid user data.

## Logic Implementation
1.  **`remove_expired_unactivated_users()`**:
    *   Retrieves the `EMAIL_ACTIVATE_TOKEN_EXPIRE_HOURS` configuration from `backend.app.core.config` to determine the retention period for unactivated accounts.
    *   Calculates the cutoff date for accounts that need to be deleted.
    *   Connects to the database.
    *   Finds and deletes all users in the `users` table where `is_active` is `False` and `created_at` is earlier than the cutoff date.
    *   Logs the cleanup operation.

## Path
`/backend/app/services/inactive_user_cleaner.py`