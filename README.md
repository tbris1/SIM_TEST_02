# Medical On-Call Simulation Platform

A web-based simulation platform for training medical students in managing multiple patients during on-call shifts.

## Features

- **Time-Based Mechanics**: Simulated clock where actions consume time (3-4 hours sim time in ~60 minutes)
- **AI-Driven Interactions**: GPT-4 powered nurse conversations for realistic triage
- **Simulated EHR**: Progressive information revelation based on user actions
- **Patient State Machine**: Rule-based clinical trajectories (stable → deteriorating → critical)
- **Timeline & Feedback**: Automated session recording with AI-generated feedback

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: React + TypeScript
- **AI**: OpenAI GPT-4
- **Storage**: JSON files

## Project Structure

```
medical-oncall-sim/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── data/            # Scenarios and session data
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API documentation available at: http://localhost:8000/docs

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## Development Status

Currently in Phase 1: Core Simulation Engine development.

See [implementation plan](/.claude/plans/snug-launching-bird.md) for details.

## License

TBD
