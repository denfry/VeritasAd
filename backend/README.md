# VeritasAd Backend

Neural network-based advertising integration detection system backend built with FastAPI.

## Features

- **Video Analysis Pipeline**: Multi-modal analysis combining visual, audio, and text
- **Logo Detection**: CLIP-based brand logo detection in video frames
- **Audio Transcription**: Whisper-based audio-to-text conversion
- **Keyword Detection**: Advertising keyword identification in transcripts
- **Disclosure Detection**: Rule-based and LLM-based advertising disclosure marker detection
- **PDF Report Generation**: Comprehensive analysis reports
- **RESTful API**: FastAPI-based REST API with automatic documentation
- **Database Storage**: SQLite/PostgreSQL support for analysis results
- **Rate Limiting**: API key-based usage tracking

## Architecture

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── analyze.py   # Video analysis endpoints
│   │   ├── upload.py    # File upload endpoints
│   │   ├── report.py    # Report generation/retrieval
│   │   └── health.py    # Health check
│   ├── core/            # Core configuration
│   │   ├── config.py    # Settings and configuration
│   │   └── dependencies.py  # Dependency injection
│   ├── models/          # Database models
│   │   └── database.py  # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   │   ├── analysis.py
│   │   ├── user.py
│   │   └── video.py
│   ├── services/        # Business logic
│   │   ├── video_processor.py     # Main video processing
│   │   ├── audio_analyzer.py      # Audio analysis with Whisper
│   │   ├── disclosure_detector.py # Disclosure detection
│   │   └── report_generator.py    # PDF generation
│   └── main.py          # Application entry point
├── tests/               # Unit and integration tests
├── requirements.txt     # Python dependencies
└── Dockerfile          # Docker configuration
```

## Installation

### Prerequisites

- Python 3.11+
- FFmpeg (for video/audio processing)
- CUDA-capable GPU (optional, for faster processing)

### Setup

1. **Clone the repository**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**:
```bash
# Database is initialized automatically on first run
```

## Configuration

Edit `.env` file:

```env
# Project Settings
PROJECT_NAME=VeritasAD
DEBUG=False

# ML Models
USE_LLM=False              # Enable LLM-based disclosure detection
WHISPER_MODEL=tiny         # Whisper model size
CLIP_MODEL=openai/clip-vit-base-patch32

# Database
DATABASE_URL=sqlite:///./veritasad.db

# Rate Limits
FREE_LIMIT=5
PRO_LIMIT=100
```

## Running

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
docker build -t veritasad-backend .
docker run -p 8000:8000 veritasad-backend
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Video Analysis

**POST** `/api/v1/analyze/check`
- Analyze video for advertising content
- Accepts file upload or URL
- Returns analysis results with scores

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/check" \
  -H "X-API-Key: test-key-123" \
  -F "url=https://youtube.com/watch?v=..."
```

**Response**:
```json
{
  "video_id": "20240315_123456_abc123",
  "status": "completed",
  "has_advertising": true,
  "confidence_score": 0.78,
  "visual_score": 0.65,
  "audio_score": 0.82,
  "text_score": 0.82,
  "disclosure_score": 0.90,
  "detected_brands": [
    {
      "name": "Winline",
      "confidence": 0.85,
      "timestamps": [12.5, 45.2, 78.9]
    }
  ],
  "detected_keywords": ["промокод", "скидка", "winline"],
  "transcript": "...",
  "processing_time": 45.2
}
```

### Reports

**GET** `/api/v1/report/{video_id}`
- Download PDF report
- Returns PDF file

### Health Check

**GET** `/health`
- Check API status

## ML Models

### CLIP (Visual Analysis)
- Model: `openai/clip-vit-base-patch32`
- Purpose: Logo and brand detection in video frames
- Sampling: Every 2 seconds, max 30 frames

### Whisper (Audio Analysis)
- Model: `tiny` (configurable: tiny, base, small, medium, large)
- Purpose: Audio transcription
- Language: Russian

### LLM (Optional - Disclosure Detection)
- Model: Llama 3.1 8B + LoRA adapter
- Purpose: Advanced disclosure marker detection
- Requires: GPU with 16GB+ VRAM

## Performance

### Processing Times (approximate)

| Video Length | CPU | GPU |
|--------------|-----|-----|
| 30 seconds   | 20s | 8s  |
| 2 minutes    | 45s | 15s |
| 5 minutes    | 120s| 35s |

### Optimization Tips

1. Use GPU for faster processing
2. Adjust Whisper model size (tiny → large)
3. Reduce frame sampling rate
4. Enable LLM only when needed

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_video_processor.py
```

## Troubleshooting

### FFmpeg not found
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### CUDA/GPU issues
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU-only mode
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Memory errors
- Reduce Whisper model size in `.env`
- Decrease frame sampling rate
- Process shorter videos

## Development

### Adding new analysis features

1. Create new analyzer in `app/services/`
2. Integrate into `VideoProcessor.process()`
3. Update schemas in `app/schemas/`
4. Add tests

### Database migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## License

MIT License - see LICENSE file

## Support

- GitHub Issues: [github.com/denfry/VeritasAd/issues](https://github.com/denfry/VeritasAd/issues)
- Email: dabinayo@pm.me
- Telegram: [@kfcbossalbino](https://t.me/kfcbossalbino)
