# CustDev Marketplace Bot

Telegram marketplace / Customer Development platform with customer and worker roles, task creation, applications, balance, payout, arbitration, ratings, Excel reports and YooMoney integration.

## Features

- customer / worker registration
- task creation with categories and budgets
- worker applications and customer selection
- balance and reserved balance flow
- payout request and arbitration flow
- ratings and Excel reports

## Tech Stack

pyTelegramBotAPI, SQLite, pandas, openpyxl, YooMoney

## Project Structure

- `.env.example`
- `.gitignore`
- `base.py`
- `config.py`
- `content`
- `create_task.py`
- `excel`
- `excel.py`
- `files`
- `help.py`
- `keyboard.py`
- `main.py`
- `pay.py`
- `README.md`
- `requirements.txt`
- `reset-demo.ps1`
- `run.ps1`
- `scripts`
- `setup.ps1`
- `survey.py`
- `test.py`

## Quick Start

### Windows

1. Run `./setup.ps1`.
2. Fill `.env` with a fresh Telegram test bot token and any required service credentials.
3. Keep `DEMO_MODE=1` for portfolio screenshots.
4. Run `./run.ps1`.

## Environment Variables

- `DEMO_MODE`
- `TELEGRAM_BOT_TOKEN`
- `ADMIN_IDS`
- `ADMIN_CHAT_ID`
- `ARBITRATION_CHAT_URL`
- `YOOMONEY_TOKEN`
- `YOOMONEY_RECEIVER`

## Demo Mode

Demo mode disables real external side effects. Payment checks are treated as successful where payment flow exists, and production channel/admin sends are skipped or require a fresh configured target.

## Security / Privacy

Production databases, logs, lock files, generated Excel exports, old Git history and hardcoded credentials were removed. Use only fresh credentials created for a demo bot.

## Project Status

needs credentials for real services.

## Historical Context

This is an older portfolio project. The public version keeps the original business logic and structure as much as possible; changes are limited to safety, local launch, demo mode and compatibility.
