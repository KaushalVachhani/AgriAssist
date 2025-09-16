# AgriAssist

Farm AI Assistant | खेत सहायक AI

## Overview
AgriAssist is an AI-powered assistant for farmers, providing advice via text, image, and audio queries. It uses FastAPI for the backend and a custom HTML/CSS/JS frontend.

## Features
- Multimodal input: text, image, audio
- Hindi language support
- LLM-based guardrails for farming-related queries
- Audio response generation

## Project Structure
```
frontend/        # Static frontend (HTML, CSS, JS)
src/             # Backend code and generated audio
  agriassist/    # Main backend package
  generated_speech_responses/ # Audio output
requirements.txt # Python dependencies
Dockerfile       # Container setup
.env.example     # Environment variable template
```

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy .env.example to .env and add your API keys.
3. Run the backend:
   ```bash
   python src/app.py
   ```
4. Open [http://localhost:7860](http://localhost:7860) in your browser.

## Docker
1. Build:
   ```bash
   docker build -t agriassist .
   ```
2. Run:
   ```bash
   docker run -p 7860:7860 --env GROQ_API_KEY=your_key --env GOOGLE_API_KEY=your_key agriassist
   ```

## Contributing
- Fork the repo and submit PRs
- Add tests in the /tests directory

## License
MIT