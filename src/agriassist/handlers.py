import os
import tempfile
import aiofiles
from pathlib import Path
from uuid import uuid4
from typing import Optional, Tuple, Any
from gtts import gTTS
from groq import Groq
import logging
from .config import settings

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles secure file operations."""
    
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}
    
    @classmethod
    def validate_file_extension(cls, filename: str, file_type: str) -> bool:
        """Validate file extension based on type."""
        if not filename:
            return False
            
        ext = Path(filename).suffix.lower()
        
        if file_type == "image":
            return ext in cls.ALLOWED_IMAGE_EXTENSIONS
        elif file_type == "audio":
            return ext in cls.ALLOWED_AUDIO_EXTENSIONS
        
        return False
    
    @classmethod
    def get_safe_filename(cls, filename: str) -> str:
        """Generate a safe filename."""
        ext = Path(filename).suffix.lower()
        safe_name = f"{uuid4()}{ext}"
        return safe_name
    
    @classmethod
    def cleanup_temp_file(cls, filepath: str) -> None:
        """Safely remove temporary file."""
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Cleaned up temporary file: {filepath}")
        except OSError as e:
            logger.warning(f"Failed to cleanup file {filepath}: {e}")

class InputValidator:
    """Validates user inputs."""
    
    @staticmethod
    def validate_text_input(text: Optional[str]) -> bool:
        """Validate text input."""
        if not text:
            return False
        
        # Basic validation - can be extended
        if len(text.strip()) > 5000:  # Max 5000 characters
            return False
        
        return True
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size."""
        return file_size <= settings.max_file_size

def is_farming_related_llm(text: str, model) -> bool:
    """
    Use the LLM to judge if the input is farming-related. Returns True if yes, else False.
    """
    if not text:
        return False
    judge_prompt = [
        "You are a strict classifier. Only answer with 'YES' or 'NO'. ",
        "Is the following input related to farming, agriculture, crops, soil, plants, livestock, or rural agricultural issues? ",
        "If yes, answer 'YES'. If not, answer 'NO'. Do not explain.\n\nInput: ",
        text.strip()
    ]
    try:
        response = model.generate_content(judge_prompt)
        answer = response.text.strip().upper()
        return answer == 'YES'
    except Exception:
        return False

def validate_and_handle(text, img, audio, model):
    """Enhanced validation and handling with security checks."""
    logger.info("validate_and_handle called with text=%s, img=%s, audio=%s", bool(text), bool(img), bool(audio))
    
    try:
        # Validate inputs
        if not (text or img or audio):
            logger.warning("No input provided by user.")
            return "❌ Please provide at least one input (text, image, or audio).", None
        
        # Validate text input if provided
        if text and not InputValidator.validate_text_input(text):
            logger.warning("Invalid text input provided")
            return "❌ Text input is too long or invalid. Please keep it under 5000 characters.", None
        
        # If audio, validate and transcribe first for guardrail check
        transcript = None
        if audio:
            try:
                # Validate audio file
                if not FileHandler.validate_file_extension(audio, "audio"):
                    return "❌ Invalid audio format. Please upload MP3, WAV, M4A, OGG, FLAC, or AAC files.", None
                
                transcript = transcribe_with_groq(
                    settings.whisper_model_name, 
                    audio, 
                    settings.groq_api_key
                )
            except Exception as e:
                logger.error("Audio transcription failed: %s", e, exc_info=True)
                return "❌ Could not transcribe audio. Please try again or upload a clearer recording.", None
        
        # Validate image if provided
        if img and not FileHandler.validate_file_extension(img, "image"):
            return "❌ Invalid image format. Please upload JPG, PNG, GIF, BMP, or WebP files.", None
        
        # Check if any input is farming-related using LLM as judge
        check_text = text or ""
        if transcript:
            check_text += f"\n{transcript}"
        
        if check_text and not is_farming_related_llm(check_text, model):
            logger.info("Input rejected by LLM guardrail")
            return "❌ Not supported: Please ask only farming-related questions. | कृपया केवल खेती से संबंधित प्रश्न पूछें", None
        
        # Forward to handler with cleanup
        result = handle_multimodal_query(text, img, audio, model=model)
        
        # Cleanup temporary files
        if audio:
            FileHandler.cleanup_temp_file(audio)
        if img:
            FileHandler.cleanup_temp_file(img)
        
        return result
        
    except Exception as e:
        logger.error("Unexpected error in validate_and_handle: %s", e, exc_info=True)
        return "❌ An unexpected error occurred. Please try again later.", None

def handle_multimodal_query(
    text_input: str,
    image_input: Any,
    audio_input: Optional[str] = None,
    model: Optional[Any] = None
) -> Tuple[str, Optional[str]]:
    logger.info("handle_multimodal_query called with text_input=%s, image_input=%s, audio_input=%s", bool(text_input), bool(image_input), bool(audio_input))
    question_id = str(uuid4())
    try:
        if audio_input:
            logger.info("Audio file received at: %s", audio_input)
            stt_model = "whisper-large-v3"
            transcribed_text = transcribe_with_groq(stt_model, audio_input, os.getenv("GROQ_API_KEY") or "")
            text_input = f"{text_input}\nTranscribed audio: {transcribed_text}"
        
        prompt_parts = [
            "You are an AI assistant specialized in farming advice. "
            "Read the farmer's question carefully and give a clear, practical answer. "
            "Respond only in Hindi. "
            "Keep the answer short, limited to 2–3 key points. "
            "Do not add any introduction or summary, and avoid symbols like *.",
            f"\n\nFarmer's Question: {text_input}"
        ]
        
        if image_input:
            prompt_parts.append(image_input)
        
        logger.info("Sending request to Gemini model...")
        response = model.generate_content(prompt_parts)
        ai_text_response = response.text
        logger.info("AI Response generated: %s", ai_text_response)
        
        # Use the same directory that FastAPI serves from
        from pathlib import Path
        output_dir = Path(__file__).parent / "generated_speech_responses"
        output_dir.mkdir(exist_ok=True)
        output_filepath = str(output_dir / f"speech_response_{question_id}.mp3")
        try:
            text_to_speech_with_gtts(input_text=ai_text_response, output_filepath=output_filepath)
            logger.info("Generated speech saved to: %s", output_filepath)
        except Exception as e:
            logger.error("Text-to-speech failed: %s", e, exc_info=True)
            return ai_text_response + "\n\n⚠️ Audio response could not be generated.", None
        return ai_text_response, output_filepath
    except Exception as e:
        logger.error("Error in handle_multimodal_query: %s", e, exc_info=True)
        return f"An error occurred while processing your request. Please try again later.", None

def text_to_speech_with_gtts(input_text: str, output_filepath: str) -> None:
    """Convert text to speech in Hindi and save as MP3."""
    language = "hi"
    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)

def transcribe_with_groq(stt_model: str, audio_filepath: str, api_key: str) -> str:
    """Transcribe audio to text using Groq's API."""
    try:
        if not os.path.exists(audio_filepath):
            raise FileNotFoundError(f"Audio file not found: {audio_filepath}")
        
        client = Groq(api_key=api_key)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        logger.info("Successfully transcribed audio")
        return transcription.text
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise
