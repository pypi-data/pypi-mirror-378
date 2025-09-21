import gradio as gr


def mimo_audio_ui():

    from .run_mimo_audio import MultiModalSpeechInterface

    speech_interface = MultiModalSpeechInterface()

    speech_interface.create_interface()


def extension__tts_generation_webui():
    mimo_audio_ui()

    return {
        "package_name": "tts_webui_extension.mimo_audio",
        "name": "Mimo audio",
        "requirements": "git+https://github.com/rsxdalv/tts_webui_extension.mimo_audio@main",
        "description": "A template extension for TTS Generation WebUI",
        "extension_type": "interface",
        "extension_class": "tools",
        "author": "Xiaomi MiMo",
        "extension_author": "rsxdalv",
        "license": "MIT",
        "website": "https://github.com/XiaomiMiMo/MiMo-Audio",
        "extension_website": "https://github.com/rsxdalv/tts_webui_extension.mimo_audio",
        "extension_platform_version": "0.0.1",
    }


if __name__ == "__main__":
    if "demo" in locals():
        locals()["demo"].close()
    with gr.Blocks() as demo:
        with gr.Tab("Mimo audio", id="mimo_audio"):
            mimo_audio_ui()

    demo.launch(
        server_port=7772,  # Change this port if needed
    )
