# Telegram Channel Info Bot

A lightweight Telegram bot that retrieves channel information
using the official Telegram Bot API.

## Features

- /start
- /help
- /info @channel
- /stats
- Channel title
- Channel username
- Channel ID
- Channel type
- Subscriber count when available
- Description
- Public channel link
- SQLite lookup statistics
- Lightweight Python backend
- No AI
- No external database

## Requirements

Python 3.10+

## Installation

Install dependencies:

pip install -r requirements.txt

## Configure token

Set the BOT_TOKEN environment variable.

Linux/macOS:

export BOT_TOKEN="YOUR_BOT_TOKEN"

Windows PowerShell:

$env:BOT_TOKEN="YOUR_BOT_TOKEN"

## Run

python bot.py

## Telegram commands

/start

/help

/info @telegram

/stats

## Security

Never publish your Telegram bot token on GitHub.

Use an environment variable or hosting-platform secret.

## Database

SQLite is automatically created as:

channel_bot.db

The database stores basic lookup statistics.

## Deployment

Use the following start command:

python bot.py

Set:

BOT_TOKEN = your Telegram bot token
