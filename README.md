# Job Bot

A human-in-the-loop job application copilot that helps find, apply, and track jobs.

## Features

- **Job Ingestion**: Fetch jobs from multiple ATS sources (Greenhouse, Lever, Ashby)
- **Smart Filtering**: Filter jobs based on your preferences and criteria
- **Priority Scoring**: Rank jobs by fit, company priority, freshness, and more
- **Application Assistance**: Guided browser autofill for job applications
- **Tracker Integration**: Sync with Google Sheets for comprehensive tracking
- **Outreach Support**: Generate personalized outreach drafts
- **Follow-up Management**: Automated follow-up task creation

## Philosophy

This system is designed to reduce repetitive work while preserving human control. Every meaningful step requires user approval - no automatic submissions or messaging without explicit consent.

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js (for Playwright browsers)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/job-bot.git
cd job-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Initialize the database:
```bash
python -m app.db.init_db
```

## Configuration

Key environment variables:

- `DATABASE_URL`: SQLite database path (default: `sqlite:///./data/database/job_bot.db`)
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
- `GOOGLE_SHEETS_CREDENTIALS_PATH`: Path to Google Sheets credentials JSON
- `ANTHROPIC_API_KEY`: Optional API key for LLM features
- `DEBUG`: Enable debug mode (default: `False`)

See `.env.example` for all available configuration options.

## Usage

### Start the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Manual Scripts

Fetch jobs manually:
```bash
python scripts/fetch_jobs.py
```

Sync tracker:
```bash
python scripts/sync_tracker.py
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
ruff check app/
```

### Type Checking

```bash
mypy app/
```

## Project Structure

```
job-bot/
├── app/                    # Application code
│   ├── api/               # FastAPI endpoints
│   ├── core/              # Core application logic
│   ├── services/          # Business logic services
│   ├── models/            # Data models
│   ├── schemas/           # Pydantic schemas
│   └── db/                # Database layer
├── data/                  # Data storage
├── scripts/               # Utility scripts
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Architecture

The system follows a modular architecture with clear separation of concerns:

- **API Layer**: FastAPI endpoints for HTTP requests
- **Services Layer**: Business logic and integrations
- **Models Layer**: Data models and validation
- **Database Layer**: Data persistence and migrations

## Security & Privacy

- Personal data stored securely in local database
- No automatic submissions without user approval
- Environment-based configuration
- Secure credential management

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.