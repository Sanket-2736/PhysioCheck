# PhysioCheck Backend

A comprehensive physiotherapy monitoring system that uses computer vision and pose estimation to track patient exercises in real-time. Built with FastAPI, MediaPipe, and MySQL.

## Overview

PhysioCheck enables physicians to create custom exercise protocols and monitor patient rehabilitation sessions through AI-powered pose tracking. The system provides real-time feedback, quality scoring, and detailed analytics for physiotherapy sessions.

## Key Features

- **Real-time Pose Tracking**: Uses MediaPipe for accurate body pose estimation
- **Exercise Creation**: Physicians can define custom exercises with specific rules
- **Live Session Monitoring**: Real-time tracking of patient exercise sessions
- **Quality Assessment**: Automated scoring based on form, alignment, and completion
- **Role-based Access**: Separate interfaces for physicians, patients, and administrators
- **Rehabilitation Plans**: Structured therapy programs with progress tracking
- **Analytics Dashboard**: Performance metrics and progress visualization
- **Advanced Rep Analysis**: Automatic detection of exercise phases (start, peak, end)
- **Stability Assessment**: Movement quality analysis with jitter detection
- **Subscription Management**: Patient-physician relationship management
- **Pose Template System**: Reference pose capture and comparison
- **Interactive Testing**: HTML-based testing interfaces for pose tracking
- **Modular Architecture**: Separated pose tracking modules for enhanced maintainability

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Computer Vision**: MediaPipe, OpenCV
- **Authentication**: JWT tokens
- **File Storage**: Cloudinary
- **Email**: SMTP integration

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── .env                   # Environment configuration
├── pose_tracking_patient.py    # Legacy patient tracking (moved to pose/)
├── pose_tracking_physician.py  # Legacy physician tracking (moved to pose/)
├── test.py                # Testing utilities
├── database/
│   ├── connection.py      # Database connection setup
│   └── models.py          # SQLAlchemy models
├── pose/                  # Enhanced pose tracking modules
│   ├── main.py           # Standalone pose tracking server
│   ├── pose_tracking_patient.py    # Patient session tracking
│   ├── pose_tracking_physician.py  # Physician pose capture
│   ├── rep_analysis.py   # Repetition detection algorithms
│   └── stability_analysis.py      # Movement stability assessment
├── routers/
│   ├── auth_router.py     # Authentication endpoints
│   ├── exercises_router.py # Exercise management
│   ├── sessions_router.py  # Session tracking
│   ├── rehab_router.py    # Rehabilitation plans
│   ├── rehab_plan_router.py # Detailed rehab plan management
│   ├── profile_router.py  # User profiles
│   ├── admin_router.py    # Admin functions
│   ├── physician_router.py # Physician-specific endpoints
│   └── subscription_router.py # Patient-physician subscriptions
├── services/              # Business logic layer
│   ├── auth_service.py    # Authentication logic
│   ├── exercises_service.py # Exercise management
│   ├── sessions_service.py # Session handling
│   ├── rehab_service.py   # Rehabilitation plans
│   ├── rehab_plan_service.py # Advanced rehab planning
│   ├── profile_service.py # User profile management
│   ├── admin_service.py   # Admin operations
│   ├── subscription_service.py # Subscription management
│   ├── pose_template_service.py # Pose template handling
│   ├── exercise_rule_service.py # Exercise rule generation
│   └── rep_capture_service.py   # Rep analysis and capture
├── schemas/               # Pydantic models
│   ├── auth_schemas.py    # Authentication schemas
│   ├── exercise_schemas.py # Exercise-related schemas
│   ├── profile_schemas.py # Profile schemas
│   ├── subscription_schema.py # Subscription schemas
│   ├── pose_template_schema.py # Pose template schemas
│   └── rep_capture_schema.py   # Rep capture schemas
├── utils/                 # Utility functions
│   ├── security.py       # Security utilities
│   ├── cloudinary.py     # File upload handling
│   └── email_utils.py    # Email functionality
└── tests/                # Testing and demo files
    ├── test.html         # Frontend pose tracking demo
    ├── test2.html        # Additional test interface
    └── test_capture.html # Pose capture testing
```

## Installation

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Webcam for pose tracking

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy aiomysql mediapipe opencv-python cloudinary python-multipart python-jose bcrypt statistics
```

**Alternative: Install from requirements.txt (if available)**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file with:
```env
# Database
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/physiocheck

# Cloudinary (for file uploads)
CLOUDINARY_CLOUD=your_cloud_name
CLOUDINARY_KEY=your_api_key
CLOUDINARY_SECRET=your_api_secret

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM="PhysioCheck <your_email@gmail.com>"
```

4. **Set up the database**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE physiocheck;
```

5. **Run the application**

**Main Application:**
```bash
python -m uvicorn main:app --reload
```

**Standalone Pose Tracking Server:**
```bash
cd pose
python -m uvicorn main:app --reload --port 8001
```

The main API will be available at `http://localhost:8000`
The pose tracking server will be available at `http://localhost:8001`

6. **Test the system**

Open the testing interfaces in your browser:
- `backend/tests/test.html` - Interactive pose tracking demo
- `backend/tests/test_capture.html` - Pose capture testing

Or visit the API documentation at `http://localhost:8000/docs`

## API Documentation

### Authentication Endpoints

- `POST /auth/register` - Patient registration
- `POST /auth/register-physician` - Physician registration
- `POST /auth/login` - User login
- `POST /auth/login-admin` - Admin login
- `GET /auth/me` - Get current user info
- `GET /auth/physician/status` - Check physician verification status

### Exercise Management

- `POST /exercises/` - Create new exercise (physician only)
- `GET /exercises` - List all exercises
- `GET /exercise/{exercise_id}` - Get exercise details
- `POST /exercises/{exercise_id}/capture-pose` - Capture reference poses
- `POST /exercises/{exercise_id}/capture-keypoints` - Capture pose keypoints
- `POST /exercises/{exercise_id}/generate-angle-ranges` - Generate angle rules
- `POST /exercises/{exercise_id}/generate-timing-stability` - Generate timing rules
- `POST /exercises/{exercise_id}/generate-alignment-rules` - Generate alignment rules

### Session Tracking

- `POST /start-session` - Start patient exercise session
- `GET /session/{session_id}` - Get session status and progress
- `GET /video-feed` - Live camera stream

### Physician Management

- `GET /physician/patients` - Get physician's assigned patients

### Subscription Management

- `POST /subscription/subscribe` - Subscribe patient to physician

### Pose Analysis

- **Rep Detection**: Automatic identification of exercise repetitions
- **Phase Analysis**: Detection of start, peak, and end phases
- **Stability Metrics**: Assessment of movement consistency and control
- **Template Matching**: Comparison against reference poses

### Core Functionality

#### Exercise Session Flow

1. **Exercise Creation** (Physician)
   - Define exercise parameters and target body parts
   - Capture reference poses using pose tracking
   - Set alignment rules and angle thresholds

2. **Session Execution** (Patient)
   - Start session with specific exercise and target reps
   - Real-time pose tracking and validation
   - Live feedback on form and alignment
   - Automatic rep counting and quality scoring

3. **Results Analysis**
   - Detailed session summary with quality metrics
   - Error analysis and improvement suggestions
   - Progress tracking over time

#### Pose Tracking Features

- **Critical Joint Validation**: Ensures required body parts are visible
- **Angle Measurement**: Calculates joint angles for form assessment
- **Alignment Rules**: Checks body symmetry and positioning
- **Smoothing**: Reduces noise in pose detection with EMA filtering
- **Phase Detection**: Identifies exercise phases (up/down/mid)
- **Rep Analysis**: Automatic detection of repetition start, peak, and end points
- **Stability Assessment**: Measures movement consistency and jitter
- **Template System**: Reference pose capture and comparison
- **Multi-pose Support**: Handles various exercise types and movements

## Database Schema

### Core Tables

- **users**: User accounts with role-based access
- **patients**: Patient-specific information and profiles
- **physicians**: Physician credentials and specializations
- **exercises**: Exercise definitions and metadata
- **exercise_presets**: Exercise configuration and rules
- **pose_templates**: Reference poses for exercises (start, peak, end, reference)
- **exercise_rules**: Joint angle ranges, timing, and stability rules
- **exercise_logic**: Rep counting and phase detection logic
- **sessions**: Individual exercise sessions
- **session_progress**: Real-time session events
- **session_results**: Final session summaries
- **rehab_plans**: Structured rehabilitation programs
- **rehab_plan_exercises**: Exercise assignments within plans
- **performance_metrics**: Detailed analytics and metrics
- **common_errors**: Error pattern tracking
- **ai_rule_suggestions**: AI-generated exercise improvements

## Usage Examples

### Starting a Patient Session

```python
# POST /start-session
{
    "exercise_id": 1,
    "patient_id": 123,
    "target_reps": 10,
    "max_duration": 300
}
```

### Session Progress Monitoring

```python
# GET /session/{session_id}
{
    "session": {
        "id": "uuid-string",
        "status": "ACTIVE",
        "targetReps": 10,
        "startedAt": "2024-01-01T10:00:00"
    },
    "progress": {
        "event": "progress",
        "repCount": 5,
        "measuredAngles": {...}
    },
    "final": null
}
```

## Development

### Running Tests

```bash
python test.py
```

### Adding New Exercises

1. Create exercise definition in database
2. Capture reference poses using pose template system
3. Generate angle ranges and timing rules automatically
4. Implement pose tracking logic in `pose/pose_tracking_patient.py`
5. Define validation rules and alignment checks
6. Test with HTML testing interfaces in `tests/` directory

### Testing Interfaces

The project includes interactive HTML testing interfaces:

- **test.html**: Complete pose tracking demo with real-time feedback
- **test2.html**: Alternative testing interface
- **test_capture.html**: Pose capture and template testing

These can be opened directly in a browser for testing pose tracking functionality.

### Rep Analysis System

The enhanced rep analysis system provides:

- **Phase Detection**: Automatic identification of exercise phases
- **Stability Metrics**: Movement quality assessment
- **Template Matching**: Comparison against reference poses
- **Quality Scoring**: Comprehensive exercise performance evaluation

### Error Handling

The application includes comprehensive error handling:
- Global exception handlers for unhandled errors
- Validation error responses
- HTTP exception handling
- Database connection error recovery

## Deployment

### Production Setup

1. **Environment Configuration**
   - Set production database credentials
   - Configure secure JWT secrets
   - Set up production SMTP settings

2. **Database Migration**
   - Run database schema creation
   - Seed initial data (roles, admin users)

3. **Server Deployment**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

### Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`