import gradio as gr
from app.handlers import validate_and_handle
from app.config import load_env_and_models

model = load_env_and_models()

def launch_app() -> None:
    """
    Launch the Gradio web application for the Farm AI Assistant.
    """
    theme = gr.themes.Ocean()
    with gr.Blocks(theme=theme, title="Farm AI Assistant | खेत सहायक AI") as demo:
        gr.Markdown(
            """
            <div style="text-align: center;">
                <h1 style="font-size: 3em; color: #4CAF50;">🌾 Farm AI Assistant | खेत सहायक AI</h1>
                <p style="font-size: 1.2em; color: #7f8c8d; margin-top: -10px;">Your Personal Farming Companion | आपका व्यक्तिगत कृषि साथी</p>
            </div>
            """
        )
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("#### 📥 Input Your Query | अपनी समस्या बताएं")
                text_box = gr.Textbox(
                    label="Describe your farming issue: | अपनी कृषि समस्या का वर्णन करें:",
                    placeholder="e.g., 'My tomato plant leaves are turning yellow.' | उदाहरण: 'मेरे टमाटर के पौधों की पत्तियां पीली हो रही हैं।'",
                    interactive=True
                )
                image_box = gr.Image(
                    type="pil",
                    label="Upload an image of the plant (optional): | पौधे की तस्वीर अपलोड करें (वैकल्पिक):",
                    interactive=True
                )
                audio_box = gr.Audio(
                    label="Record your question (optional): | अपना प्रश्न रिकॉर्ड करें (वैकल्पिक):",
                    sources=["microphone"],
                    interactive=True,
                    type="filepath"
                )
                submit_btn = gr.Button("Get My Solution | समाधान प्राप्त करें", variant="primary")
            with gr.Column(scale=1):
                gr.Markdown("#### 💬 AI Response | AI प्रतिक्रिया")
                text_output = gr.Textbox(
                    label="AI Response (Text): | AI प्रतिक्रिया (पाठ):",
                    placeholder="The AI's response will appear here... | AI की प्रतिक्रिया यहां दिखाई देगी...",
                    interactive=False
                )
                audio_output = gr.Audio(
                    label="AI Response (Audio): | AI प्रतिक्रिया (ऑडियो):",
                    interactive=False,
                    type="filepath"
                )
        submit_btn.click(
            fn=lambda text, img, audio: validate_and_handle(text, img, audio, model=model),
            inputs=[text_box, image_box, audio_box],
            outputs=[text_output, audio_output]
        )
        gr.Markdown(
            """
            ---
            <p align="center">Powered by AI for a greener future. | बेहतर भविष्य के लिए AI द्वारा संचालित।</p>
            """
        )
    demo.launch()

if __name__ == "__main__":
    launch_app()
