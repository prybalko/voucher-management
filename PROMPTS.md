# Prompts Used to Build This Project

1. **Initial requirement**
   ```
   # Senior Python Backend Developer - Test Assignment

   ## Overview
   Build a simple REST API for voucher management using FastAPI and SQLAlchemy.

   ## The Task
   Create a basic CRUD API for managing discount vouchers. Keep it simple - this is not meant to be a huge API.
   No authentication or authorization is required for this assignment.

   ## Technical Stack
   - FastAPI
   - SQLAlchemy
   - Pydantic v2
   - Python 3.11+

   ## Voucher Data
   A voucher should track:
   - Unique code
   - Discount percentage
   - Expiration date
   - Active status
   - Timestamps

   ## Expected Functionality
   - Create vouchers (with auto-generated codes)
   - List vouchers (with pagination)
   - Retrieve voucher by code
   - Update vouchers
   - Deactivate/delete vouchers

   ## Deliverables
   Working API with brief setup instructions.

   ## What We Value
   - Clean, maintainable code
   - Type safety
   - Pragmatic solutions - keep it simple
   ```

2. `add tests`

3. `use ruff linter`

4. `can there be race conditions with db?`

5. `use PostgreSQL with pessimistic locking`

6. `Add db level Validators on discount_percent`

7. `remove Retry logic`

8. `use postgres for tests`

9. `avoid "docker exec -it vouchers-db psql -U postgres -c "CREATE DATABASE vouchers_test;". is there a way to create it from code?`

10. `run tests`

11. `add docker-compose file`

12. `add github action that runs tests on every commit to master`

13. `save all my promts to a md file`

14. `add api tests`

15. `run tests`

16. `for list\get apis return only active and non-expired vouchers. When deleting, do not delete the record, set active to False. Add tests`
