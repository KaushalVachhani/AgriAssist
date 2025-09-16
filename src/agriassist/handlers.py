import os
from uuid import uuid4
from typing import Optional, Tuple, Any
from gtts import gTTS
from groq import Groq
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    logger.info("validate_and_handle called with text=%s, img=%s, audio=%s", bool(text), bool(img), bool(audio))
    try:
        # If all inputs are empty
        if not (text or img or audio):
            logger.warning("No input provided by user.")
            return "❌ Please provide at least one input (text, image, or audio).", None
        # If audio, transcribe first for guardrail check
        transcript = None
        if audio:
            try:
                stt_model = "whisper-large-v3"
                transcript = transcribe_with_groq(stt_model, audio, os.getenv("GROQ_API_KEY") or "")
            except Exception as e:
                logger.error("Audio transcription failed: %s", e, exc_info=True)
                return "❌ Could not transcribe audio. Please try again or upload a clearer recording.", None
        # Check if any input is farming-related using LLM as judge
        check_text = text or ""
        if transcript:
            check_text += f"\n{transcript}"
        if not is_farming_related_llm(check_text, model):
            logger.info("Input rejected by LLM guardrail. Input: %s", check_text)
            return "❌ Not supported: Please ask only farming-related questions. | कृपया केवल खेती से संबंधित प्रश्न पूछें", None
        # Otherwise forward to your handler
        return handle_multimodal_query(text, img, audio, model=model)
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
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, "generated_speech_responses")        
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, f"speech_response_{question_id}.mp3")
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
