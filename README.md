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

- **Python 3.8+** (3.9+ recommended)
- **MySQL 8.0+** or compatible database
- **Webcam** for pose tracking functionality
- **Git** for version control
- **Node.js** (optional, for frontend development)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create virtual environment (recommended)**
```bash
python -m venv physiocheck-env
source physiocheck-env/bin/activate  # On Windows: physiocheck-env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy aiomysql mediapipe opencv-python cloudinary python-multipart python-jose bcrypt
```

**Alternative: Install from requirements.txt (if available)**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the `backend/` directory with:
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

5. **Set up the database**
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE physiocheck;
EXIT;
```

6. **Initialize database tables**
The application will automatically create tables on startup, or you can run:
```bash
python -c "from database.connection import engine, Base; import asyncio; asyncio.run(engine.begin().run_sync(Base.metadata.create_all))"
```

7. **Run the application**

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

8. **Test the system**

**API Documentation & Landing Page:**
- Visit `http://localhost:8000/` for the main landing page with all documentation links
- Visit `http://localhost:8000/docs` for interactive Swagger UI documentation
- Visit `http://localhost:8000/redoc` for alternative ReDoc documentation
- Visit `http://localhost:8000/health` for API health check
- Visit `http://localhost:8000/api-info` for detailed API information

**Interactive Testing:**
Open the testing interfaces in your browser:
- `backend/tests/test.html` - Interactive pose tracking demo
- `backend/tests/test_capture.html` - Pose capture testing
- `backend/tests/test2.html` - Additional testing interface

**Quick Health Check:**
```bash
# Test API health
curl http://localhost:8000/health

# List available exercises
curl http://localhost:8000/exercises

# Get API information
curl http://localhost:8000/api-info
```

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

```json
POST /start-session
{
    "exercise_id": 1,
    "patient_id": 123,
    "target_reps": 10,
    "max_duration": 300
}

Response:
{
    "sessionId": "uuid-string"
}
```

### Session Progress Monitoring

```json
GET /session/{session_id}
{
    "session": {
        "id": "uuid-string",
        "status": "ACTIVE",
        "targetReps": 10,
        "maxDuration": 300,
        "startedAt": "2024-01-01T10:00:00",
        "endedAt": null
    },
    "progress": {
        "event": "progress",
        "repCount": 5,
        "status": "ACTIVE",
        "measuredAngles": {
            "left_shoulder": 85.2,
            "right_shoulder": 87.1
        }
    },
    "final": null
}
```

### Creating an Exercise

```json
POST /exercises/
{
    "name": "Shoulder Raise",
    "category": "Upper Body",
    "difficulty": "beginner",
    "target_body_parts": ["shoulders", "arms"],
    "description": "Raise both arms to shoulder level"
}
```

### User Authentication

```json
POST /auth/login
{
    "email": "patient@example.com",
    "password": "secure_password"
}

Response:
{
    "success": true,
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
        "id": 123,
        "email": "patient@example.com",
        "role": "patient",
        "full_name": "John Doe"
    }
}
```

## Development

### Running Tests

```bash
# Run basic tests
python test.py

# Test pose tracking functionality
python pose/pose_tracking_patient.py

# Test physician pose capture
python pose/pose_tracking_physician.py
```

### Development Workflow

1. **Start development server with auto-reload:**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Monitor logs:**
```bash
tail -f logs/app.log  # if logging is configured
```

3. **Database migrations:**
```bash
# After model changes, restart the application to auto-create tables
python -m uvicorn main:app --reload
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

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Install system dependencies for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  physiocheck-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+aiomysql://root:password@db:3306/physiocheck
    depends_on:
      - db
    volumes:
      - /dev/video0:/dev/video0  # For webcam access
    
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: physiocheck
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## Troubleshooting

### Common Issues

**Camera Access Issues:**
```bash
# Check camera permissions
ls /dev/video*
# Ensure camera is not being used by another application
```

**Database Connection Issues:**
```bash
# Test MySQL connection
mysql -h localhost -u root -p physiocheck
# Check if database exists
SHOW DATABASES;
```

**MediaPipe Installation Issues:**
```bash
# For M1 Macs
pip install mediapipe-silicon

# For older systems
pip install mediapipe==0.8.11
```

**Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**
   ```bash
   python test.py
   # Test with HTML interfaces
   ```
5. **Submit a pull request**
   - Provide clear description of changes
   - Include screenshots for UI changes
   - Reference any related issues

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

## License

This project is licensed under the MIT License.

## Performance Optimization

### For Production

1. **Database Optimization:**
   - Use connection pooling
   - Add database indexes for frequently queried fields
   - Consider read replicas for analytics

2. **Pose Tracking Optimization:**
   - Adjust MediaPipe model complexity based on hardware
   - Use frame skipping for lower-end devices
   - Implement pose caching for reference templates

3. **API Performance:**
   - Enable response compression
   - Use Redis for session caching
   - Implement rate limiting

## Security Considerations

- **Authentication:** JWT tokens with proper expiration
- **Data Protection:** Encrypt sensitive patient data
- **API Security:** Input validation and sanitization
- **File Uploads:** Validate and scan uploaded files
- **Database:** Use parameterized queries to prevent SQL injection

## Monitoring and Logging

```python
# Add to main.py for basic logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log important events
logger.info("Session started for patient {patient_id}")
logger.error("Pose tracking failed: {error}")
```

## Support

For technical support or questions:

- **Documentation:** Check the API documentation at `/docs`
- **Issues:** Create an issue in the repository with:
  - Clear description of the problem
  - Steps to reproduce
  - System information (OS, Python version, etc.)
  - Error logs if applicable
- **Community:** Join our community discussions
- **Professional Support:** Contact the development team for enterprise support

## Roadmap

### Upcoming Features

- [ ] Mobile app integration
- [ ] Advanced AI exercise recommendations
- [ ] Multi-language support
- [ ] Telehealth video consultations
- [ ] Wearable device integration
- [ ] Advanced analytics dashboard
- [ ] Exercise library expansion

### Version History

- **v1.0.0** - Initial release with basic pose tracking
- **v1.1.0** - Added rep analysis and stability assessment
- **v1.2.0** - Enhanced template system and testing interfaces
- **Current** - Modular architecture and subscription management