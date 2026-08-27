# Changes made for public release

- Removed hardcoded credentials and moved configuration to environment variables.
- Removed production SQLite databases, logs, lock files, caches and generated/user Excel files.
- Added per-project `.env.example`, `.gitignore`, requirements and Windows setup/run/reset scripts.
- Added demo database initializer with synthetic records only.
- Fixed file paths to resolve relative to the project directory.
- Added minimal demo mode safeguards for payments, production channels and admin side effects where applicable.
- Added `if __name__ == '__main__'` guards where needed for syntax/import checks.

Core business logic was intentionally left unchanged.
