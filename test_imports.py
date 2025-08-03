import requests
import openai
import time
import json
import os

try:
    from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig
    from azure.cognitiveservices.speech.audio import AudioOutputConfig
    print("Azure Cognitive Services Speech SDK imported successfully!")
except ImportError as e:
    print(f"Error importing Azure Cognitive Services Speech SDK: {e}")
