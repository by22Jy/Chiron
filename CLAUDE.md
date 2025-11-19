<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# YOLO-LLM - Gesture Control AI Platform

## Project Overview
YOLO-LLM is an AI-powered gesture control platform that combines computer vision, machine learning, and web technologies to enable gesture-based control of applications. The system can detect objects, poses, emotions, and hand gestures, then map these to various system actions.

## Architecture
The project consists of 4 main components:
1. **Backend** (Spring Boot, port 8080): API orchestrator and configuration management
2. **AI Service** (FastAPI, port 8000): Computer vision services (YOLO, pose detection, emotion recognition)
3. **Agent** (Python): Local gesture detection and system control
4. **Frontend** (Vue.js, port 5173): Web interface for interaction

## Development Setup

### Prerequisites
- Python 3.8+ with pip
- Java 17+ with Maven
- Node.js 18+ with npm
- MySQL database
- Webcam for gesture detection

### Environment Setup

#### Backend Setup
```bash
cd backend
mvn spring-boot:run
# Set environment variables:
# KIMI_API_KEY or QWEN_API_KEY
```

#### AI Service Setup
```bash
cd ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### Agent Setup
```bash
cd agent
pip install -r requirements.txt
# Test gesture detection:
python main.py --realtime
# View available actions:
python main.py --actions
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Configuration
- Agent settings: `agent/config.yaml`
- Backend settings: `backend/src/main/resources/application.yml`
- Frontend development server: `http://localhost:5173`

## Key Features
### Gesture Recognition
- 8 hand gestures: POINT_UP, THUMBS_UP, VICTORY, OK_SIGN, etc.
- MediaPipe-based real-time detection
- Configurable detection intervals and confidence thresholds

### Action Execution
- 7 action types: hotkey, mouse, click, scroll, text, window, system
- Cross-platform support with pyautogui
- Extensible action framework

### AI Capabilities
- Object detection with YOLOv8
- Pose estimation and person tracking
- Emotion recognition with DeepFace
- Real-time WebSocket streaming

## Development Workflow
1. Start Backend (port 8080)
2. Start AI Service (port 8000)
3. Start Agent (optional, for local testing)
4. Start Frontend (port 5173)
5. Access web interface at `http://localhost:5173`

## API Endpoints
### Backend (port 8080)
- `/api/config` - Get gesture mappings
- `/api/audit/log` - Log gesture executions
- `/api/event` - Send events

### AI Service (port 8000)
- `/detect/file` - Object detection from file
- `/analyze/file` - Comprehensive analysis (detection + pose + gesture + emotion)
- `/ws/analyze` - WebSocket streaming for real-time analysis

## Testing
- Use `--realtime` mode for live gesture testing
- Use `--watch` mode for interactive testing
- Use `--gesture <code>` for single gesture execution
- Access web interface for integration testing

## Troubleshooting
- Camera access issues: Check camera permissions and camera_id in config
- Model loading: Ensure YOLO models are downloaded properly
- Backend connection: Verify backend is running at configured URL
- CORS issues: Check FastAPI CORS configuration