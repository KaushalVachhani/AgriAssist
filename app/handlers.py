import os
import platform
import subprocess
from uuid import uuid4
from typing import Optional, Tuple, Any
from gtts import gTTS
from groq import Groq
from elevenlabs.client import ElevenLabs
import elevenlabs
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def validate_and_handle(text, img, audio, model):
    # If all inputs are empty
    if not (text or img or audio):
        return "❌ Please provide at least one input (text, image, or audio).", None
    # Otherwise forward to your handler
    return handle_multimodal_query(text, img, audio, model=model)

def handle_multimodal_query(
    text_input: str,
    image_input: Any,
    audio_input: Optional[str] = None,
    model: Optional[Any] = None
) -> Tuple[str, Optional[str]]:
    """
    Process a farming-related query using text, image, and/or audio input.
    Returns the AI's text response and the path to the generated audio file.
    """
    logger.info("Received inputs: text=%s, image=%s, audio=%s", text_input, bool(image_input), bool(audio_input))
    question_id = str(uuid4())
    try:
        if audio_input:
            logger.info("Audio file received at: %s", audio_input)
            stt_model = "whisper-large-v3"
            transcribed_text = transcribe_with_groq(stt_model, audio_input, os.getenv("GROQ_API_KEY"))
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
        output_dir = "generated_speech_responses"
        
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, f"speech_response_{question_id}.mp3")
        text_to_speech_with_gtts(input_text=ai_text_response, output_filepath=output_filepath)
        logger.info("Generated speech saved to: %s", output_filepath)
        
        return ai_text_response, output_filepath
    
    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return f"An error occurred: {e}", None

def text_to_speech_with_gtts(input_text: str, output_filepath: str) -> None:
    """Convert text to speech in Hindi and save as MP3."""
    language = "hi"
    audioobj = gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)

def transcribe_with_groq(stt_model: str, audio_filepath: str, GROQ_API_KEY: str) -> str:
    """Transcribe audio to text using Groq's API."""
    client = Groq(api_key=GROQ_API_KEY)
    with open(audio_filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=stt_model,
            file=audio_file,
            language="en"
        )
    logger.info("Transcription: %s", transcription)
    return transcription.text

def text_to_speech_with_elevenlabs(input_text: str, output_filepath: str) -> None:
    """Convert text to speech using ElevenLabs and save as MP3."""
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    audio = client.text_to_speech.convert(
        text=input_text,
        voice_id="aGb0TwKthRLQTPThYRqI",
        output_format="mp3_44100_128",
        model_id="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)
    os_name = platform.system()
    try:
        if os_name == "Darwin":
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        logger.error("An error occurred while trying to play the audio: %s", e)
