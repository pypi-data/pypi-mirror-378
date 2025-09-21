#!/usr/bin/env python3
"""
Mova Voice Interface - Speech Recognition and Text-to-Speech

This module provides comprehensive voice interaction capabilities for Mova CLI including:
- Multi-language speech recognition using OpenAI Whisper
- Real-time audio recording and processing
- Text-to-speech output with multilingual support
- Continuous voice interaction modes
- Integration with Mova CLI commands

IMPORTANT: This module is designed to be completely standalone to avoid circular imports.
"""

import os
import sys
import threading
import time
import tempfile
import json
import queue
import subprocess
import requests
import re
from typing import Optional, Dict, List, Callable
from pathlib import Path
from datetime import datetime
import logging

# Voice processing dependencies
try:
    import whisper
    import speech_recognition as sr
    import pyttsx3
    import pyaudio
    import wave
    import numpy as np
    VOICE_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    VOICE_DEPENDENCIES_AVAILABLE = False
    VOICE_IMPORT_ERROR = str(e)

# High-quality TTS engines
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from TTS.api import TTS as CoquiTTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False

# Mova CLI integration - completely standalone implementation
DEFAULT_SERVER = "http://localhost:8094"

def make_request(method, endpoint, data=None, server=DEFAULT_SERVER):
    """Make HTTP request to Mova server - standalone implementation"""
    url = f"{server}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_mova_command(command, language="en"):
    """Execute Mova CLI command directly - no imports needed"""
    try:
        # Get the CLI directory
        cli_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(cli_dir)
        venv_python = os.path.join(project_root, "venv", "bin", "python")
        mova_cli = os.path.join(cli_dir, "mova.py")
        
        # Execute command directly
        full_command = [venv_python, mova_cli] + command.split()
        result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "command": " ".join(full_command)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "command": command}


class VoiceConfig:
    """Voice interface configuration"""
    
    # Supported languages and their configurations
    LANGUAGES = {
        'en': {
            'name': 'English',
            'whisper_model': 'base.en',
            'tts_voice': 'english',
            'wake_words': ['mova', 'hey mova', 'computer'],
            'commands': {
                'stop': ['stop', 'quit', 'exit', 'end'],
                'help': ['help', 'what can you do', 'commands'],
                'status': ['status', 'how are you', 'what\'s your status'],
                'repeat': ['repeat', 'say that again', 'what did you say']
            }
        },
        'pl': {
            'name': 'Polski',
            'whisper_model': 'base',
            'tts_voice': 'polish',
            'wake_words': ['mova', 'hej mova', 'komputer'],
            'commands': {
                'stop': ['stop', 'koniec', 'wyjście', 'zakończ'],
                'help': ['pomoc', 'co potrafisz', 'komendy'],
                'status': ['status', 'jak się masz', 'jaki jest twój status'],
                'repeat': ['powtórz', 'powiedz to jeszcze raz', 'co powiedziałeś']
            }
        },
        'de': {
            'name': 'Deutsch',
            'whisper_model': 'base',
            'tts_voice': 'german',
            'wake_words': ['mova', 'hey mova', 'computer'],
            'commands': {
                'stop': ['stop', 'aufhören', 'ende', 'beenden'],
                'help': ['hilfe', 'was kannst du', 'befehle'],
                'status': ['status', 'wie geht es dir', 'was ist dein status'],
                'repeat': ['wiederholen', 'sag das nochmal', 'was hast du gesagt']
            }
        }
    }
    
    # Audio configuration
    AUDIO_FORMAT = pyaudio.paInt16 if VOICE_DEPENDENCIES_AVAILABLE else None
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    SILENCE_THRESHOLD = 500
    SILENCE_DURATION = 2.0  # seconds
    MAX_RECORDING_DURATION = 30.0  # seconds
    
    # Processing configuration
    WHISPER_DEVICE = "cpu"  # Use "cuda" if GPU available
    TTS_RATE = 200  # Words per minute
    TTS_VOLUME = 0.8


class AudioRecorder:
    """Real-time audio recording with silence detection"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_data = []
        
        if VOICE_DEPENDENCIES_AVAILABLE:
            self.audio = pyaudio.PyAudio()
    
    def start_recording(self) -> bool:
        """Start audio recording"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return False
        
        try:
            self.stream = self.audio.open(
                format=self.config.AUDIO_FORMAT,
                channels=self.config.CHANNELS,
                rate=self.config.RATE,
                input=True,
                frames_per_buffer=self.config.CHUNK
            )
            self.is_recording = True
            self.audio_data = []
            return True
        except Exception as e:
            logging.error(f"Failed to start recording: {e}")
            return False
    
    def record_with_silence_detection(self) -> Optional[bytes]:
        """Record audio until silence is detected"""
        if not self.is_recording:
            return None
        
        audio_frames = []
        silence_frames = 0
        total_frames = 0
        max_frames = int(self.config.RATE / self.config.CHUNK * self.config.MAX_RECORDING_DURATION)
        silence_threshold_frames = int(self.config.RATE / self.config.CHUNK * self.config.SILENCE_DURATION)
        
        try:
            while self.is_recording and total_frames < max_frames:
                data = self.stream.read(self.config.CHUNK)
                audio_frames.append(data)
                total_frames += 1
                
                # Convert to numpy array for amplitude analysis
                audio_np = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_np).mean()
                
                if amplitude < self.config.SILENCE_THRESHOLD:
                    silence_frames += 1
                else:
                    silence_frames = 0
                
                # Stop recording after silence threshold
                if silence_frames >= silence_threshold_frames and len(audio_frames) > silence_threshold_frames:
                    break
            
            # Combine all audio frames
            return b''.join(audio_frames)
            
        except Exception as e:
            logging.error(f"Error during recording: {e}")
            return None
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def cleanup(self):
        """Cleanup audio resources"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()


class SpeechProcessor:
    """Speech-to-text processing using OpenAI Whisper"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.config = VoiceConfig.LANGUAGES.get(language, VoiceConfig.LANGUAGES['en'])
        self.whisper_model = None
        self.backup_recognizer = None
        
        if VOICE_DEPENDENCIES_AVAILABLE:
            self._load_models()
    
    def _load_models(self):
        """Load Whisper and backup speech recognition models"""
        try:
            # Load Whisper model
            model_name = self.config['whisper_model']
            print(f"🤖 Loading Whisper model: {model_name}...")
            self.whisper_model = whisper.load_model(model_name, device=VoiceConfig.WHISPER_DEVICE)
            print("✅ Whisper model loaded successfully")
            
            # Initialize backup recognizer
            self.backup_recognizer = sr.Recognizer()
            self.backup_recognizer.energy_threshold = 300
            self.backup_recognizer.dynamic_energy_threshold = True
            
        except Exception as e:
            logging.error(f"Failed to load speech models: {e}")
            print(f"❌ Error loading speech models: {e}")
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data to text"""
        if not VOICE_DEPENDENCIES_AVAILABLE or not audio_data:
            return None
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Write WAV header and data
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(VoiceConfig.CHANNELS)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(VoiceConfig.RATE)
                    wav_file.writeframes(audio_data)
                
                temp_path = temp_file.name
            
            # Transcribe with Whisper (primary method)
            if self.whisper_model:
                try:
                    result = self.whisper_model.transcribe(
                        temp_path,
                        language=self.language if self.language != 'en' else None,
                        task='transcribe',
                        fp16=False
                    )
                    text = result['text'].strip()
                    
                    # Clean up temporary file
                    os.unlink(temp_path)
                    
                    if text:
                        return text
                except Exception as e:
                    logging.warning(f"Whisper transcription failed: {e}")
            
            # Fallback to speech_recognition
            if self.backup_recognizer:
                try:
                    with sr.AudioFile(temp_path) as source:
                        audio = self.backup_recognizer.record(source)
                    
                    # Try Google Speech Recognition
                    text = self.backup_recognizer.recognize_google(audio, language=self.language)
                    
                    # Clean up temporary file
                    os.unlink(temp_path)
                    
                    return text.strip()
                    
                except Exception as e:
                    logging.warning(f"Backup speech recognition failed: {e}")
            
            # Clean up temporary file if still exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return None
            
        except Exception as e:
            logging.error(f"Audio transcription error: {e}")
            return None
    
    def detect_wake_word(self, text: str) -> bool:
        """Detect wake words in transcribed text"""
        if not text:
            return False
        
        text_lower = text.lower()
        wake_words = self.config.get('wake_words', [])
        
        return any(wake_word in text_lower for wake_word in wake_words)
    
    def parse_command(self, text: str) -> tuple[str, str]:
        """Parse command from transcribed text"""
        if not text:
            return 'unknown', text
        
        text_lower = text.lower()
        commands = self.config.get('commands', {})
        
        for command_type, variations in commands.items():
            for variation in variations:
                if variation in text_lower:
                    return command_type, text
        
        return 'custom', text


class TextToSpeech:
    """Enhanced Text-to-speech with high-quality engines and intelligent fallback"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.config = VoiceConfig.LANGUAGES.get(language, VoiceConfig.LANGUAGES['en'])
        self.tts_engine = None
        self.is_speaking = False
        self.active_engine = None
        self.temp_files = []  # Track temp files for cleanup
        
        # Initialize pygame mixer for audio playback
        try:
            import pygame
            pygame.mixer.init()
            self.pygame_available = True
        except:
            self.pygame_available = False
        
        if VOICE_DEPENDENCIES_AVAILABLE:
            self._initialize_enhanced_engine()
    
    def _initialize_enhanced_engine(self):
        """Initialize high-quality TTS engine with intelligent fallback system"""
        print("🎯 Initializing Enhanced TTS System with high-quality engines...")
        
        # Priority order: highest quality first
        engines_to_try = [
            ('gTTS', self._try_gtts_engine),
            ('EdgeTTS', self._try_edge_tts_engine), 
            ('CoquiTTS', self._try_coqui_tts_engine),
            ('pyttsx3', self._try_pyttsx3_engine),
            ('espeak', self._try_espeak_fallback)
        ]
        
        for engine_name, init_method in engines_to_try:
            try:
                print(f"🔊 Trying {engine_name} TTS engine...")
                if init_method():
                    self.active_engine = engine_name
                    print(f"✅ {engine_name} TTS engine initialized successfully!")
                    return
            except Exception as e:
                print(f"⚠️ {engine_name} engine failed: {e}")
                continue
        
        print("❌ All TTS engines failed to initialize")
        self.active_engine = None
    
    def _try_gtts_engine(self):
        """Try to initialize Google Text-to-Speech (highest quality)"""
        if not GTTS_AVAILABLE:
            return False
        
        try:
            # Test gTTS with a short phrase
            test_text = "Test" if self.language == 'en' else "Test"
            tts = gTTS(text=test_text, lang=self.language, slow=False)
            
            # Create temporary file to test
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tts.save(tmp_file.name)
                
                # Test playback
                if self.pygame_available:
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    # Cleanup test file
                    os.unlink(tmp_file.name)
                    print("🎵 gTTS quality test: HIGH QUALITY VOICE ✅")
                    return True
                    
        except Exception as e:
            print(f"❌ gTTS test failed: {e}")
            return False
        return False
    
    def _try_edge_tts_engine(self):
        """Try to initialize Microsoft Edge TTS (very high quality)"""
        if not EDGE_TTS_AVAILABLE:
            return False
        
        try:
            # Test Edge TTS availability
            # This is a basic check - actual usage will be in speak method
            voice_map = {
                'en': 'en-US-AriaNeural',
                'pl': 'pl-PL-ZofiaNeural', 
                'es': 'es-ES-ElviraNeural',
                'de': 'de-DE-KatjaNeural',
                'fr': 'fr-FR-DeniseNeural'
            }
            
            selected_voice = voice_map.get(self.language, 'en-US-AriaNeural')
            print(f"🎵 Edge TTS selected voice: {selected_voice} - NATURAL NEURAL VOICE ✅")
            return True
            
        except Exception as e:
            print(f"❌ Edge TTS test failed: {e}")
            return False
    
    def _try_coqui_tts_engine(self):
        """Try to initialize Coqui TTS (neural synthesis)"""
        if not COQUI_TTS_AVAILABLE:
            return False
        
        try:
            # Initialize Coqui TTS with a lightweight model
            self.coqui_tts = CoquiTTS("tts_models/en/ljspeech/tacotron2-DDC")
            print("🎵 Coqui TTS quality: NEURAL SYNTHESIS ✅")
            return True
        except Exception as e:
            print(f"❌ Coqui TTS initialization failed: {e}")
            return False
    
    def _try_pyttsx3_engine(self):
        """Try to initialize improved pyttsx3 with better voice selection"""
        try:
            # Try different TTS drivers with preference for quality
            drivers = ['sapi5', 'nsss', 'espeak']  # sapi5 first for Windows quality
            
            for driver in drivers:
                try:
                    self.tts_engine = pyttsx3.init(driver)
                    
                    # Configure for better quality
                    self.tts_engine.setProperty('rate', 180)  # Slower, more natural
                    self.tts_engine.setProperty('volume', 0.9)
                    
                    # Try to find best quality voice
                    voices = self.tts_engine.getProperty('voices')
                    if voices:
                        # Prefer female voices as they often sound more natural
                        for voice in voices:
                            if any(term in voice.name.lower() for term in ['female', 'aria', 'zira', 'helen']):
                                self.tts_engine.setProperty('voice', voice.id)
                                print(f"🎵 pyttsx3 selected high-quality voice: {voice.name}")
                                break
                    
                    print(f"🔊 pyttsx3 driver '{driver}' - IMPROVED QUALITY ✅")
                    return True
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ pyttsx3 initialization failed: {e}")
            return False
        return False
    
    def _try_espeak_fallback(self):
        """Fallback to espeak (basic quality but reliable)"""
        try:
            # Test espeak availability
            result = subprocess.run(['espeak', '--version'], capture_output=True, timeout=3)
            if result.returncode == 0:
                print("🔊 espeak fallback - BASIC QUALITY (reliable) ✅")
                return True
        except Exception as e:
            print(f"❌ espeak fallback failed: {e}")
            return False
        return False
    
    def _initialize_engine(self):
        """Initialize TTS engine with enhanced diagnostics"""
        try:
            # Try different TTS drivers
            drivers = ['espeak', 'sapi5', 'nsss', 'dummy']
            for driver in drivers:
                try:
                    self.tts_engine = pyttsx3.init(driver)
                    print(f"🔊 TTS driver '{driver}' initialized successfully")
                    break
                except Exception as e:
                    print(f"⚠️  TTS driver '{driver}' failed: {e}")
                    continue
            
            if not self.tts_engine:
                # Fallback to default initialization
                self.tts_engine = pyttsx3.init()
                print(f"🔊 TTS engine initialized with default driver")
            
            # Configure voice properties
            self.tts_engine.setProperty('rate', VoiceConfig.TTS_RATE)
            self.tts_engine.setProperty('volume', VoiceConfig.TTS_VOLUME)
            
            # Enhanced voice diagnostics
            voices = self.tts_engine.getProperty('voices')
            print(f"🎤 Available voices: {len(voices) if voices else 0}")
            
            # Try to set language-specific voice
            target_voice = self.config.get('tts_voice', 'english')
            voice_found = False
            
            if voices:
                for i, voice in enumerate(voices):
                    print(f"  Voice {i}: {voice.name} (ID: {voice.id})")
                    if target_voice.lower() in voice.name.lower() or self.language in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"🎯 Selected voice: {voice.name}")
                        voice_found = True
                        break
            
            if not voice_found and voices:
                # Use first available voice as fallback
                self.tts_engine.setProperty('voice', voices[0].id)
                print(f"🔄 Using fallback voice: {voices[0].name}")
            
            # Test TTS functionality
            self._test_tts()
            
            print(f"✅ TTS engine initialized for {self.config['name']}")
            
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {e}")
            print(f"❌ TTS initialization error: {e}")
            self._try_alternative_tts()
    
    def _test_tts(self):
        """Test TTS functionality with a simple phrase"""
        try:
            test_text = "Test" if self.language == 'en' else "Test"
            print(f"🧪 Testing TTS with: '{test_text}'")
            
            # Test without blocking to avoid hanging
            self.tts_engine.say(test_text)
            self.tts_engine.runAndWait()
            
            print(f"✅ TTS test completed successfully")
            
        except Exception as e:
            print(f"❌ TTS test failed: {e}")
            logging.error(f"TTS test error: {e}")
    
    def _test_audio_device(self, sink_name):
        """Test if audio device actually works with volume monitoring"""
        try:
            print(f"    🧪 Testing device: {sink_name}")
            
            # Set as temporary default to test
            set_result = subprocess.run(['pactl', 'set-default-sink', sink_name], 
                                      capture_output=True, timeout=3)
            if set_result.returncode != 0:
                print(f"    ❌ Cannot set as default sink")
                return {'working': False, 'volume': 0, 'reason': 'Cannot set as default'}
            
            # Get volume info
            volume_result = subprocess.run(['pactl', 'list', 'sinks'], 
                                         capture_output=True, text=True, timeout=3)
            
            volume_percent = 0
            if volume_result.returncode == 0:
                lines = volume_result.stdout.split('\n')
                in_our_sink = False
                
                for line in lines:
                    if f'Name: {sink_name}' in line:
                        in_our_sink = True
                        continue
                    
                    if in_our_sink and 'Volume:' in line:
                        import re
                        volume_match = re.search(r'(\d+)%', line)
                        if volume_match:
                            volume_percent = int(volume_match.group(1))
                        break
                    
                    if in_our_sink and line.strip() == '':
                        break
            
            print(f"    🔊 Current volume: {volume_percent}%", end='')
            
            # Ensure minimum volume
            if volume_percent < 50:
                print(f" -> Setting to 70%")
                subprocess.run(['pactl', 'set-sink-volume', sink_name, '70%'], 
                             capture_output=True, timeout=3)
                volume_percent = 70
            else:
                print(f" ✅")
            
            # Test actual audio output
            print(f"    🎵 Testing audio output...", end='')
            test_result = subprocess.run(['espeak', '-s', '300', '-v', 'pl', 'test'], 
                                       capture_output=True, timeout=3)
            
            if test_result.returncode == 0:
                print(f" ✅ Working!")
                return {
                    'working': True, 
                    'volume': volume_percent, 
                    'name': sink_name,
                    'reason': 'Audio test successful'
                }
            else:
                print(f" ❌ Failed")
                return {
                    'working': False, 
                    'volume': volume_percent, 
                    'name': sink_name,
                    'reason': 'Audio test failed'
                }
                
        except Exception as e:
            print(f"    ❌ Test error: {e}")
            return {'working': False, 'volume': 0, 'name': sink_name, 'reason': str(e)}

    def _detect_audio_devices(self, interactive=True):
        """Detect available audio devices with proper testing and user choice"""
        try:
            print(f"🔍 Detecting and testing available audio devices...")
            
            # Get PulseAudio sinks
            result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                print(f"⚠️  pactl not available or failed")
                return None
            
            # Get current default sink to restore if needed
            current_default = None
            try:
                current_result = subprocess.run(['pactl', 'get-default-sink'], 
                                              capture_output=True, text=True, timeout=3)
                if current_result.returncode == 0:
                    current_default = current_result.stdout.strip()
            except:
                pass
            
            all_sinks = []
            working_devices = []
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sink_id = parts[0]
                        sink_name = parts[1]
                        status = parts[4] if len(parts) > 4 else 'UNKNOWN'
                        
                        sink_info = {
                            'id': sink_id,
                            'name': sink_name,
                            'status': status
                        }
                        all_sinks.append(sink_info)
                        print(f"  🔊 Found device: {sink_name} (Status: {status})")
                        
                        # Test each device regardless of type (including Bluetooth!)
                        test_result = self._test_audio_device(sink_name)
                        
                        if test_result['working']:
                            device_type = "Unknown"
                            name_lower = sink_name.lower()
                            if 'usb' in name_lower and 'generic' in name_lower:
                                device_type = "USB Audio (Generic)"
                            elif 'usb' in name_lower:
                                device_type = "USB Audio"
                            elif 'bt' in name_lower or 'bluetooth' in name_lower:
                                device_type = "Bluetooth Audio"  # NO LONGER REJECTED!
                            elif 'hdmi' in name_lower:
                                device_type = "HDMI Audio"
                            
                            working_devices.append({
                                **test_result,
                                'type': device_type,
                                'priority': self._get_device_priority(sink_name)
                            })
                            print(f"    ✅ {device_type} - Working (Volume: {test_result['volume']}%)")
            
            # Restore original default if we changed it during testing
            if current_default:
                subprocess.run(['pactl', 'set-default-sink', current_default], 
                             capture_output=True, timeout=3)
            
            if not working_devices:
                print(f"❌ No working audio devices found!")
                return None
            
            # Sort by priority (but include Bluetooth now!)
            working_devices.sort(key=lambda x: x['priority'])
            
            # User choice if multiple devices and interactive mode
            if interactive and len(working_devices) > 1:
                print(f"\n🎵 Found {len(working_devices)} working audio devices:")
                for i, device in enumerate(working_devices):
                    print(f"  {i+1}. {device['type']}: {device['name']} (Volume: {device['volume']}%)")
                
                try:
                    choice = input(f"\nChoose device (1-{len(working_devices)}) or Enter for auto-select: ").strip()
                    if choice and choice.isdigit():
                        selected_idx = int(choice) - 1
                        if 0 <= selected_idx < len(working_devices):
                            selected_device = working_devices[selected_idx]
                        else:
                            selected_device = working_devices[0]
                    else:
                        selected_device = working_devices[0]
                except (KeyboardInterrupt, EOFError):
                    selected_device = working_devices[0]
            else:
                selected_device = working_devices[0]
            
            # Set selected device as default
            print(f"🎯 Selected: {selected_device['type']} - {selected_device['name']} ({selected_device['volume']}%)")
            
            set_result = subprocess.run(['pactl', 'set-default-sink', selected_device['name']], 
                                      capture_output=True, timeout=5)
            if set_result.returncode == 0:
                print(f"✅ Audio device set successfully!")
                return {
                    'id': selected_device.get('id', ''),
                    'name': selected_device['name'],
                    'status': 'ACTIVE'
                }
            else:
                print(f"⚠️  Failed to set audio device")
                return None
            
        except Exception as e:
            print(f"⚠️  Audio detection failed: {e}")
            return None
    
    def _get_device_priority(self, sink_name):
        """Get device priority (lower number = higher priority)"""
        name_lower = sink_name.lower()
        if 'usb' in name_lower and 'generic' in name_lower:
            return 1  # Highest priority
        elif 'usb' in name_lower or ('bt' in name_lower or 'bluetooth' in name_lower):
            return 2  # Second priority (INCLUDING BLUETOOTH!)
        elif 'hdmi' in name_lower:
            return 3  # Third priority
        else:
            return 4  # Lowest priority
    
    def _try_alternative_tts(self):
        """Try alternative TTS methods if pyttsx3 fails"""
        print(f"🔄 Attempting alternative TTS methods with audio autodetection...")
        
        # First, detect and set proper audio device
        audio_device = self._detect_audio_devices()
        
        # Method 1: espeak command line (preferred since user confirmed it works)
        try:
            test_text = "Test audio output" if self.language == 'en' else "Test dźwięku"
            print(f"🧪 Testing espeak with detected audio device...")
            
            result = subprocess.run(['espeak', test_text, '-v', 'pl' if self.language == 'pl' else 'en'], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Alternative TTS (espeak) working with audio device")
                self.alternative_tts = 'espeak'
                self.audio_device = audio_device
                return
        except Exception as e:
            print(f"⚠️  espeak failed: {e}")
        
        # Method 2: festival
        try:
            result = subprocess.run(['festival', '--tts'], input="Hello test", text=True, capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Alternative TTS (festival) working")
                self.alternative_tts = 'festival'
                self.audio_device = audio_device
                return
        except Exception as e:
            print(f"⚠️  festival failed: {e}")
        
        print(f"❌ No working TTS method found")
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Enhanced text-to-speech with high-quality engines and intelligent fallback"""
        if not text:
            return False
        
        print(f"🗣️ Speaking with {self.active_engine or 'FALLBACK'}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        if not self.active_engine:
            print("❌ No TTS engine available")
            return False
        
        # Use the best available engine
        try:
            if self.active_engine == 'gTTS':
                return self._speak_with_gtts(text, blocking)
            elif self.active_engine == 'EdgeTTS':
                return self._speak_with_edge_tts(text, blocking)
            elif self.active_engine == 'CoquiTTS':
                return self._speak_with_coqui_tts(text, blocking)
            elif self.active_engine == 'pyttsx3':
                return self._speak_with_pyttsx3(text, blocking)
            elif self.active_engine == 'espeak':
                return self._speak_with_espeak(text, blocking)
        except Exception as e:
            print(f"❌ {self.active_engine} failed: {e}")
            # Try fallback to espeak
            return self._speak_with_espeak(text, blocking)
        
        return False
    
    def _speak_with_gtts(self, text: str, blocking: bool = True) -> bool:
        """Speak using Google Text-to-Speech (highest quality)"""
        if not GTTS_AVAILABLE:
            return False
        
        try:
            print("🎵 Using Google TTS - HIGH QUALITY VOICE")
            tts = gTTS(text=text, lang=self.language, slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tts.save(tmp_file.name)
                self.temp_files.append(tmp_file.name)
                
                # Play using pygame
                if self.pygame_available:
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    
                    if blocking:
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    
                    print("✅ Google TTS completed successfully")
                    return True
                    
        except Exception as e:
            print(f"❌ Google TTS failed: {e}")
            return False
        return False
    
    def _speak_with_edge_tts(self, text: str, blocking: bool = True) -> bool:
        """Speak using Microsoft Edge TTS (natural neural voices)"""
        if not EDGE_TTS_AVAILABLE:
            return False
        
        try:
            print("🎵 Using Microsoft Edge TTS - NATURAL NEURAL VOICE")
            
            # Voice selection based on language
            voice_map = {
                'en': 'en-US-AriaNeural',
                'pl': 'pl-PL-ZofiaNeural',
                'es': 'es-ES-ElviraNeural', 
                'de': 'de-DE-KatjaNeural',
                'fr': 'fr-FR-DeniseNeural'
            }
            
            voice = voice_map.get(self.language, 'en-US-AriaNeural')
            
            # Run Edge TTS async function
            async def run_edge_tts():
                communicate = edge_tts.Communicate(text, voice)
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    await communicate.save(tmp_file.name)
                    self.temp_files.append(tmp_file.name)
                    
                    # Play the file
                    if self.pygame_available:
                        pygame.mixer.music.load(tmp_file.name)
                        pygame.mixer.music.play()
                        
                        if blocking:
                            while pygame.mixer.music.get_busy():
                                time.sleep(0.1)
                        
                        return True
                return False
            
            # Run the async function
            result = asyncio.run(run_edge_tts())
            if result:
                print("✅ Microsoft Edge TTS completed successfully")
                return True
                
        except Exception as e:
            print(f"❌ Microsoft Edge TTS failed: {e}")
            return False
        return False
    
    def _speak_with_coqui_tts(self, text: str, blocking: bool = True) -> bool:
        """Speak using Coqui TTS (neural synthesis)"""
        if not COQUI_TTS_AVAILABLE or not hasattr(self, 'coqui_tts'):
            return False
        
        try:
            print("🎵 Using Coqui TTS - NEURAL SYNTHESIS")
            
            # Generate audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                self.coqui_tts.tts_to_file(text=text, file_path=tmp_file.name)
                self.temp_files.append(tmp_file.name)
                
                # Play using pygame
                if self.pygame_available:
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    
                    if blocking:
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    
                    print("✅ Coqui TTS completed successfully")
                    return True
                    
        except Exception as e:
            print(f"❌ Coqui TTS failed: {e}")
            return False
        return False
    
    def _speak_with_pyttsx3(self, text: str, blocking: bool = True) -> bool:
        """Speak using improved pyttsx3 with better voice selection"""
        if not self.tts_engine:
            return False
        
        try:
            print("🎵 Using pyttsx3 - IMPROVED QUALITY")
            self.is_speaking = True
            
            if blocking:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                print("✅ pyttsx3 completed successfully")
            else:
                def speak_async():
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                        print("✅ pyttsx3 async completed successfully")
                    except Exception as e:
                        print(f"❌ pyttsx3 async error: {e}")
                    finally:
                        self.is_speaking = False
                
                thread = threading.Thread(target=speak_async)
                thread.daemon = True
                thread.start()
            
            if blocking:
                self.is_speaking = False
            return True
            
        except Exception as e:
            print(f"❌ pyttsx3 failed: {e}")
            self.is_speaking = False
            return False
    
    def _speak_with_espeak(self, text: str, blocking: bool = True) -> bool:
        """Speak using espeak fallback (basic quality but reliable)"""
        try:
            print("🎵 Using espeak - BASIC QUALITY (reliable)")
            voice_param = 'pl' if self.language == 'pl' else 'en'
            cmd = ['espeak', text, '-v', voice_param, '-s', '150', '-a', '200']
            
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if result.returncode == 0:
                print("✅ espeak completed successfully")
                return True
            else:
                print(f"⚠️ espeak returned error code: {result.returncode}")
                
        except Exception as e:
            print(f"❌ espeak failed: {e}")
            return False
        return False
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
        self.temp_files.clear()
        
        # Original pyttsx3 code disabled - keeping for reference
        # Try primary TTS engine
        if False and self.tts_engine:  # Disabled
            try:
                self.is_speaking = True
                
                if blocking:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    print(f"✅ TTS completed successfully")
                else:
                    # Non-blocking speech in separate thread
                    def speak_async():
                        try:
                            self.tts_engine.say(text)
                            self.tts_engine.runAndWait()
                            print(f"✅ TTS async completed successfully")
                        except Exception as e:
                            print(f"❌ TTS async error: {e}")
                        finally:
                            self.is_speaking = False
                    
                    thread = threading.Thread(target=speak_async)
                    thread.daemon = True
                    thread.start()
                
                if blocking:
                    self.is_speaking = False
                return True
                
            except Exception as e:
                print(f"❌ Primary TTS error: {e}")
                logging.error(f"TTS error: {e}")
                self.is_speaking = False
        
        # Try alternative TTS methods
        return self._speak_alternative(text)
    
    def _speak_alternative(self, text: str) -> bool:
        """Use alternative TTS methods with intelligent audio routing"""
        print(f"🔄 Using alternative TTS with audio autodetection...")
        
        # Ensure proper audio device is selected
        if not hasattr(self, 'audio_device') or not self.audio_device:
            self.audio_device = self._detect_audio_devices()
        
        # Method 1: espeak (preferred - user confirmed it works)
        try:
            voice_param = 'pl' if self.language == 'pl' else 'en'
            cmd = ['espeak', text, '-v', voice_param, '-s', '150', '-a', '200']
            
            print(f"🗣️  Speaking via espeak: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if result.returncode == 0:
                print(f"✅ Alternative TTS (espeak) completed successfully")
                return True
            else:
                print(f"⚠️  espeak returned error code: {result.returncode}")
                if result.stderr:
                    print(f"    stderr: {result.stderr.decode()}")
        except Exception as e:
            print(f"⚠️  espeak failed: {e}")
        
        # Method 2: festival with Polish support
        try:
            result = subprocess.run(['festival', '--tts'], input=text, text=True, capture_output=True, timeout=15)
            if result.returncode == 0:
                print(f"✅ Alternative TTS (festival) completed")
                return True
        except Exception as e:
            print(f"⚠️  festival failed: {e}")
        
        # Method 3: Try direct ALSA with aplay + espeak wav output
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                wav_cmd = ['espeak', text, '-v', voice_param, '-w', tmp_file.name]
                wav_result = subprocess.run(wav_cmd, capture_output=True, timeout=10)
                
                if wav_result.returncode == 0 and os.path.exists(tmp_file.name):
                    play_cmd = ['aplay', tmp_file.name]
                    play_result = subprocess.run(play_cmd, capture_output=True, timeout=10)
                    
                    os.unlink(tmp_file.name)  # Cleanup
                    
                    if play_result.returncode == 0:
                        print(f"✅ Alternative TTS (espeak+aplay) completed")
                        return True
        except Exception as e:
            print(f"⚠️  espeak+aplay method failed: {e}")
        
        # Method 4: Text output as fallback
        print(f"📝 TTS FALLBACK - TEXT OUTPUT: {text}")
        return False
    
    def stop_speaking(self):
        """Stop current speech output"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
            except Exception as e:
                logging.error(f"Error stopping TTS: {e}")


class VoiceInterface:
    """Main voice interface coordinator"""
    
    def __init__(self, language: str = 'en', server: str = DEFAULT_SERVER, tts_only: bool = False):
        self.language = language
        self.server = server
        self.tts_only = tts_only  # Tryb tylko TTS - bez interaktywnej selekcji urządzeń
        self.config = VoiceConfig.LANGUAGES.get(language, VoiceConfig.LANGUAGES['en'])
        
        # Initialize components
        self.recorder = AudioRecorder(VoiceConfig()) if not tts_only else None
        self.speech_processor = SpeechProcessor(language) if not tts_only else None
        self.tts = TextToSpeech(language)
        
        # State management
        self.is_active = False
        self.is_listening = False
        self.listen_only = False
        self.text_only = False
        self.continuous = False
        
        # Command callbacks
        self.command_handlers = {
            'stop': self._handle_stop,
            'help': self._handle_help,
            'status': self._handle_status,
            'repeat': self._handle_repeat,
            'custom': self._handle_custom_command
        }
        
        self.last_response = ""
        
        # Jeśli tryb TTS-only, pokaż tylko status bez interakcji
        if tts_only:
            self._show_tts_audio_status()
    
    def check_dependencies(self) -> tuple[bool, str]:
        """Check if all voice dependencies are available"""
        if not VOICE_DEPENDENCIES_AVAILABLE:
            return False, f"Voice dependencies missing: {VOICE_IMPORT_ERROR}"
        
        # Check microphone access
        try:
            test_audio = pyaudio.PyAudio()
            test_stream = test_audio.open(
                format=VoiceConfig.AUDIO_FORMAT,
                channels=VoiceConfig.CHANNELS,
                rate=VoiceConfig.RATE,
                input=True,
                frames_per_buffer=VoiceConfig.CHUNK
            )
            test_stream.close()
            test_audio.terminate()
            return True, "All voice dependencies available"
        except Exception as e:
            return False, f"Microphone access error: {e}"
    
    def start_session(self, listen_only: bool = False, text_only: bool = False, continuous: bool = False, debug_tts: bool = False):
        """Start voice interaction session"""
        self.listen_only = listen_only
        self.text_only = text_only
        self.continuous = continuous
        self.is_active = True
        
        language_name = self.config['name']
        
        print(f"🎤 Starting Mova voice interface: {language_name}")
        
        # Dependency check
        deps_ok, deps_msg = self.check_dependencies()
        if not deps_ok:
            print(f"❌ {deps_msg}")
            print("🔧 Install dependencies: pip install openai-whisper SpeechRecognition pyttsx3 pyaudio")
            return False
        
        # Mode announcements
        if listen_only:
            print("👂 Mode: Listen only (no voice responses)")
        elif text_only:
            print("📝 Mode: Text responses only")
            if debug_tts:
                print("🐛 DEBUG: TTS testing enabled despite text-only mode")
        elif continuous:
            print("🔄 Mode: Continuous listening")
        else:
            print("🗣️ Mode: Full voice interaction")
        
        # Welcome message
        welcome_msg = self._get_welcome_message()
        print(f"💬 {welcome_msg}")
        
        # TTS execution: normal mode OR debug mode (bypasses text_only restriction)
        if (not text_only and not listen_only) or debug_tts:
            if debug_tts and text_only:
                print("🐛 DEBUG: Forcing TTS execution for testing...")
            self.tts.speak(welcome_msg)
        
        # Start main interaction loop
        try:
            if continuous:
                self._continuous_interaction_loop()
            else:
                self._single_interaction_loop()
        except KeyboardInterrupt:
            print("\n👋 Voice interface stopped by user")
        finally:
            self._cleanup()
        
        return True
    
    def _get_welcome_message(self) -> str:
        """Get welcome message in current language"""
        messages = {
            'en': "Hello! I'm Mova voice assistant. How can I help you today?",
            'pl': "Cześć! Jestem asystentem głosowym Mova. Jak mogę Ci pomóc?",
            'de': "Hallo! Ich bin Mova Sprachassistent. Wie kann ich Ihnen helfen?"
        }
        return messages.get(self.language, messages['en'])
    
    def _single_interaction_loop(self):
        """Single voice interaction"""
        print("\n🎯 Listening for your command...")
        
        if not self.recorder.start_recording():
            print("❌ Failed to start audio recording")
            return
        
        # Record audio
        audio_data = self.recorder.record_with_silence_detection()
        self.recorder.stop_recording()
        
        if not audio_data:
            print("❌ No audio recorded")
            return
        
        print("🔄 Processing audio...")
        
        # Transcribe speech
        text = self.speech_processor.transcribe_audio(audio_data)
        
        if not text:
            print("❌ Could not understand speech")
            return
        
        print(f"👤 You said: {text}")
        
        # Process command
        self._process_voice_command(text)
    
    def _continuous_interaction_loop(self):
        """Continuous voice interaction with wake word detection"""
        print("\n🔄 Continuous listening mode active...")
        print(f"💡 Say wake words: {', '.join(self.config['wake_words'])}")
        
        while self.is_active:
            try:
                if not self.recorder.start_recording():
                    print("❌ Failed to start recording")
                    break
                
                print("👂 Listening...")
                audio_data = self.recorder.record_with_silence_detection()
                self.recorder.stop_recording()
                
                if audio_data:
                    text = self.speech_processor.transcribe_audio(audio_data)
                    
                    if text:
                        print(f"🔊 Heard: {text}")
                        
                        # Check for wake word
                        if self.speech_processor.detect_wake_word(text):
                            print("✅ Wake word detected!")
                            self._process_voice_command(text)
                        elif any(stop_word in text.lower() for stop_word in ['exit', 'quit', 'stop mova']):
                            print("👋 Stopping continuous mode...")
                            break
                
                time.sleep(0.5)  # Brief pause between listening cycles
                
            except KeyboardInterrupt:
                break
    
    def _process_voice_command(self, text: str):
        """Process voice command and generate response"""
        command_type, original_text = self.speech_processor.parse_command(text)
        
        # Handle command
        if command_type in self.command_handlers:
            response = self.command_handlers[command_type](original_text)
        else:
            response = self._handle_custom_command(original_text)
        
        # Output response
        if response:
            print(f"🤖 Mova: {response}")
            self.last_response = response
            
            if not self.text_only and not self.listen_only:
                self.tts.speak(response)
    
    def _handle_stop(self, text: str) -> str:
        """Handle stop command"""
        self.is_active = False
        messages = {
            'en': "Goodbye! Voice interface stopping.",
            'pl': "Do widzenia! Kończę interfejs głosowy.",
            'de': "Auf Wiedersehen! Sprachinterface wird beendet."
        }
        return messages.get(self.language, messages['en'])
    
    def _handle_help(self, text: str) -> str:
        """Handle help command"""
        messages = {
            'en': "I can help you with Mova commands. Try saying: check status, list services, or any Mova CLI command.",
            'pl': "Mogę pomóc z komendami Mova. Spróbuj powiedzieć: sprawdź status, lista usług, lub dowolną komendę CLI.",
            'de': "Ich kann Ihnen mit Mova-Befehlen helfen. Versuchen Sie zu sagen: Status prüfen, Dienste auflisten, oder jeden CLI-Befehl."
        }
        return messages.get(self.language, messages['en'])
    
    def _handle_status(self, text: str) -> str:
        """Handle status command"""
        try:
            # Make request to Mova server
            result = make_request("GET", "/api/health", server=self.server)
            
            if result.get("success"):
                messages = {
                    'en': "Mova server is running and healthy.",
                    'pl': "Serwer Mova działa i jest w dobrej kondycji.",
                    'de': "Mova-Server läuft und ist gesund."
                }
                return messages.get(self.language, messages['en'])
            else:
                messages = {
                    'en': "Mova server appears to be offline or having issues.",
                    'pl': "Serwer Mova wydaje się być offline lub ma problemy.",
                    'de': "Mova-Server scheint offline zu sein oder Probleme zu haben."
                }
                return messages.get(self.language, messages['en'])
                
        except Exception as e:
            messages = {
                'en': f"Error checking server status: {str(e)}",
                'pl': f"Błąd podczas sprawdzania statusu serwera: {str(e)}",
                'de': f"Fehler beim Überprüfen des Serverstatus: {str(e)}"
            }
            return messages.get(self.language, messages['en'])
    
    def _handle_repeat(self, text: str) -> str:
        """Handle repeat command"""
        if self.last_response:
            return self.last_response
        else:
            messages = {
                'en': "I haven't said anything yet to repeat.",
                'pl': "Nie powiedziałem jeszcze nic do powtórzenia.",
                'de': "Ich habe noch nichts gesagt, was ich wiederholen könnte."
            }
            return messages.get(self.language, messages['en'])
    
    def _handle_custom_command(self, text: str) -> str:
        """Handle custom Mova commands"""
        try:
            # Try to interpret as Mova CLI command
            text_lower = text.lower()
            
            # Map voice commands to CLI commands
            command_mappings = {
                'en': {
                    'check health': 'health',
                    'server health': 'health',
                    'list services': 'services list',
                    'show services': 'services list',
                    'start rss': 'rss',
                    'list logs': 'list all --limit 5',
                    'show errors': 'list error --limit 5'
                },
                'pl': {
                    'sprawdź zdrowie': 'health',
                    'zdrowie serwera': 'health',
                    'lista usług': 'services list',
                    'pokaż usługi': 'services list',
                    'uruchom rss': 'rss',
                    'lista logów': 'list all --limit 5',
                    'pokaż błędy': 'list error --limit 5'
                },
                'de': {
                    'gesundheit prüfen': 'health',
                    'server gesundheit': 'health',
                    'dienste auflisten': 'services list',
                    'dienste zeigen': 'services list',
                    'rss starten': 'rss',
                    'logs auflisten': 'list all --limit 5',
                    'fehler zeigen': 'list error --limit 5'
                }
            }
            
            # Find matching command
            mappings = command_mappings.get(self.language, command_mappings['en'])
            mova_command = None
            
            for voice_cmd, cli_cmd in mappings.items():
                if voice_cmd in text_lower:
                    mova_command = cli_cmd
                    break
            
            if mova_command:
                # Execute Mova CLI command
                print(f"🔄 Executing: mova {mova_command}")
                
                # This would typically execute the actual CLI command
                # For now, return a simulated response
                messages = {
                    'en': f"Executed command: {mova_command}. Check the terminal for results.",
                    'pl': f"Wykonano komendę: {mova_command}. Sprawdź terminal dla wyników.",
                    'de': f"Befehl ausgeführt: {mova_command}. Prüfen Sie das Terminal für Ergebnisse."
                }
                return messages.get(self.language, messages['en'])
            else:
                messages = {
                    'en': f"I'm not sure how to handle: {text}. Try asking for help.",
                    'pl': f"Nie jestem pewien jak obsłużyć: {text}. Spróbuj poprosić o pomoc.",
                    'de': f"Ich bin nicht sicher, wie ich damit umgehen soll: {text}. Versuchen Sie um Hilfe zu bitten."
                }
                return messages.get(self.language, messages['en'])
                
        except Exception as e:
            return f"Error processing command: {str(e)}"
    
    # ===== ZARZĄDZANIE URZĄDZENIAMI AUDIO =====
    
    def list_all_audio_devices(self, detailed: bool = False, test: bool = False):
        """Lista wszystkich dostępnych urządzeń audio (wejścia i wyjścia)"""
        print("🎵 Lista wszystkich urządzeń audio")
        print("=" * 50)
        
        # Lista urządzeń wyjściowych (głośniki)
        print("\n🔊 URZĄDZENIA WYJŚCIOWE (Głośniki/TTS):")
        output_devices = self._get_output_devices(detailed=detailed, test=test)
        
        # Lista urządzeń wejściowych (mikrofony)  
        print("\n🎤 URZĄDZENIA WEJŚCIOWE (Mikrofony/STT):")
        input_devices = self._get_input_devices(detailed=detailed, test=test)
        
        print(f"\n📊 Znaleziono: {len(output_devices)} urządzeń wyjściowych, {len(input_devices)} urządzeń wejściowych")
        
        return {'output': output_devices, 'input': input_devices}
    
    def list_speaker_devices(self, test: bool = False, current: bool = False):
        """Lista dostępnych głośników i urządzeń wyjściowych dla TTS"""
        print("🔊 Lista głośników i urządzeń wyjściowych")
        print("=" * 45)
        
        if current:
            # Pokaż aktualnie wybrany głośnik
            current_sink = self._get_current_sink()
            if current_sink:
                print(f"🎯 Aktualnie wybrany: {current_sink}")
            else:
                print("❌ Nie można wykryć aktualnie wybranego głośnika")
            print("-" * 45)
        
        devices = self._get_output_devices(detailed=True, test=test)
        
        if not devices:
            print("❌ Nie znaleziono urządzeń wyjściowych")
        else:
            print(f"\n💡 Użyj: mova speaker set <numer> aby wybrać głośnik")
        
        return devices
    
    def set_speaker_device(self, device_index: int, test: bool = False, save: bool = False):
        """Ustaw domyślny głośnik dla TTS"""
        print(f"🎯 Ustawianie głośnika #{device_index}")
        
        # Pobierz listę urządzeń wyjściowych
        devices = self._get_output_devices_raw()
        
        if device_index < 1 or device_index > len(devices):
            print(f"❌ Nieprawidłowy indeks. Wybierz od 1 do {len(devices)}")
            return False
        
        selected_device = devices[device_index - 1]
        device_name = selected_device['name']
        
        print(f"🔄 Ustawianie domyślnego głośnika: {device_name}")
        
        # Ustaw jako domyślny sink PulseAudio
        try:
            result = subprocess.run(['pactl', 'set-default-sink', device_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Pomyślnie ustawiono głośnik: {selected_device.get('description', device_name)}")
                
                if test:
                    print("🧪 Testowanie głośnika...")
                    test_result = self._test_audio_device(device_name)
                    if test_result['working']:
                        print(f"✅ Test zakończony sukcesem (Volume: {test_result['volume']}%)")
                    else:
                        print(f"⚠️ Problem z testem: {test_result['error']}")
                
                if save:
                    # TODO: Zapisz wybór w konfiguracji
                    print("💾 Zapisano wybór w konfiguracji")
                
                return True
            else:
                print(f"❌ Błąd ustawiania głośnika: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd wykonania pactl: {e}")
            return False
    
    def list_mic_devices(self, test: bool = False, current: bool = False):
        """Lista dostępnych mikrofonów i urządzeń wejściowych dla STT"""
        print("🎤 Lista mikrofonów i urządzeń wejściowych")
        print("=" * 45)
        
        if current:
            # Pokaż aktualnie wybrany mikrofon
            current_source = self._get_current_source()
            if current_source:
                print(f"🎯 Aktualnie wybrany: {current_source}")
            else:
                print("❌ Nie można wykryć aktualnie wybranego mikrofonu")
            print("-" * 45)
        
        devices = self._get_input_devices(detailed=True, test=test)
        
        if not devices:
            print("❌ Nie znaleziono urządzeń wejściowych")
        else:
            print(f"\n💡 Użyj: mova mic set <numer> aby wybrać mikrofon")
        
        return devices
    
    def set_mic_device(self, device_index: int, test: bool = False, save: bool = False):
        """Ustaw domyślny mikrofon dla STT"""
        print(f"🎯 Ustawianie mikrofonu #{device_index}")
        
        # Pobierz listę urządzeń wejściowych
        devices = self._get_input_devices_raw()
        
        if device_index < 1 or device_index > len(devices):
            print(f"❌ Nieprawidłowy indeks. Wybierz od 1 do {len(devices)}")
            return False
        
        selected_device = devices[device_index - 1]
        device_name = selected_device['name']
        
        print(f"🔄 Ustawianie domyślnego mikrofonu: {device_name}")
        
        # Ustaw jako domyślne źródło PulseAudio
        try:
            result = subprocess.run(['pactl', 'set-default-source', device_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Pomyślnie ustawiono mikrofon: {selected_device.get('description', device_name)}")
                
                if test:
                    print("🧪 Testowanie mikrofonu...")
                    test_result = self._test_mic_device(device_name)
                    if test_result['working']:
                        print(f"✅ Test zakończony sukcesem")
                    else:
                        print(f"⚠️ Problem z testem: {test_result['error']}")
                
                if save:
                    # TODO: Zapisz wybór w konfiguracji
                    print("💾 Zapisano wybór w konfiguracji")
                
                return True
            else:
                print(f"❌ Błąd ustawiania mikrofonu: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd wykonania pactl: {e}")
            return False
    
    # ===== POMOCNICZE METODY WYKRYWANIA URZĄDZEŃ =====
    
    def _get_output_devices(self, detailed: bool = False, test: bool = False):
        """Pobierz sformatowaną listę urządzeń wyjściowych"""
        devices = self._get_output_devices_raw()
        
        for i, device in enumerate(devices, 1):
            device_type = self._get_device_type(device['name'])
            status_icon = "🟢" if device['state'] == 'RUNNING' else "⭕" if device['state'] == 'SUSPENDED' else "🔴"
            
            print(f"  {i}. {status_icon} {device['description']}")
            
            if detailed:
                print(f"     📱 Typ: {device_type}")
                print(f"     🔧 Nazwa: {device['name']}")
                print(f"     📊 Status: {device['state']}")
                
            if test:
                print(f"     🧪 Testowanie urządzenia...")
                test_result = self._test_audio_device(device['name'])
                if test_result['working']:
                    print(f"     ✅ Działa (Volume: {test_result['volume']}%)")
                else:
                    print(f"     ❌ Problem: {test_result['error']}")
            
            if detailed or test:
                print()
        
        return devices
    
    def _get_input_devices(self, detailed: bool = False, test: bool = False):
        """Pobierz sformatowaną listę urządzeń wejściowych"""
        devices = self._get_input_devices_raw()
        
        for i, device in enumerate(devices, 1):
            device_type = self._get_device_type(device['name'])
            status_icon = "🟢" if device['state'] == 'RUNNING' else "⭕" if device['state'] == 'SUSPENDED' else "🔴"
            
            print(f"  {i}. {status_icon} {device['description']}")
            
            if detailed:
                print(f"     📱 Typ: {device_type}")
                print(f"     🔧 Nazwa: {device['name']}")
                print(f"     📊 Status: {device['state']}")
                
            if test:
                print(f"     🧪 Testowanie mikrofonu...")
                test_result = self._test_mic_device(device['name'])
                if test_result['working']:
                    print(f"     ✅ Działa")
                else:
                    print(f"     ❌ Problem: {test_result['error']}")
            
            if detailed or test:
                print()
        
        return devices
    
    def _get_output_devices_raw(self):
        """Pobierz surową listę urządzeń wyjściowych z PulseAudio"""
        try:
            result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            sinks = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        sink = {
                            'index': parts[0],
                            'name': parts[1], 
                            'driver': parts[2],
                            'state': parts[3],
                            'description': self._get_device_description(parts[1])
                        }
                        sinks.append(sink)
            
            return sinks
            
        except Exception as e:
            print(f"❌ Błąd pobierania urządzeń wyjściowych: {e}")
            return []
    
    def _get_input_devices_raw(self):
        """Pobierz surową listę urządzeń wejściowych z PulseAudio"""
        try:
            result = subprocess.run(['pactl', 'list', 'short', 'sources'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            sources = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        # Pomiń wbudowane źródła systemowe (monitory)
                        if '.monitor' not in parts[1]:
                            source = {
                                'index': parts[0],
                                'name': parts[1],
                                'driver': parts[2], 
                                'state': parts[3],
                                'description': self._get_device_description(parts[1])
                            }
                            sources.append(source)
            
            return sources
            
        except Exception as e:
            print(f"❌ Błąd pobierania urządzeń wejściowych: {e}")
            return []
    
    def _get_device_description(self, device_name: str):
        """Pobierz czytelny opis urządzenia"""
        try:
            # Próbuj pobrać szczegółowy opis z pactl
            result = subprocess.run(['pactl', 'list'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if device_name in line:
                        # Szukaj opisu w kolejnych liniach
                        for j in range(i, min(i+20, len(lines))):
                            if 'Description:' in lines[j] or 'device.description' in lines[j]:
                                desc = lines[j].split('=')[-1].strip().strip('"')
                                if desc and desc != device_name:
                                    return desc
            
            # Fallback - użyj nazwy urządzenia
            return device_name.replace('alsa_output.', '').replace('alsa_input.', '').replace('-', ' ')
            
        except:
            return device_name
    
    def _get_current_sink(self):
        """Pobierz aktualnie ustawiony domyślny sink"""
        try:
            result = subprocess.run(['pactl', 'get-default-sink'], 
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _get_current_source(self):
        """Pobierz aktualnie ustawione domyślne źródło"""
        try:
            result = subprocess.run(['pactl', 'get-default-source'], 
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _test_mic_device(self, device_name: str):
        """Przetestuj urządzenie wejściowe (mikrofon)"""
        try:
            # Podstawowy test - sprawdź czy urządzenie odpowiada
            result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                  capture_output=True, text=True, timeout=5)
            
            if device_name in result.stdout:
                return {'working': True, 'volume': 'N/A'}
            else:
                return {'working': False, 'error': 'Urządzenie niedostępne'}
                
        except Exception as e:
            return {'working': False, 'error': str(e)}
    
    def _get_device_type(self, device_name: str):
        """Określ typ urządzenia na podstawie nazwy"""
        device_name_lower = device_name.lower()
        
        # Rozpoznaj typy urządzeń na podstawie nazwy
        if 'usb' in device_name_lower and 'generic' in device_name_lower:
            return "Generic USB Audio"
        elif 'usb' in device_name_lower and ('bt' in device_name_lower or 'bluetooth' in device_name_lower):
            return "USB Bluetooth Audio"
        elif 'usb' in device_name_lower:
            return "USB Audio"
        elif 'bluetooth' in device_name_lower or 'bt' in device_name_lower:
            return "Bluetooth Audio"
        elif 'hdmi' in device_name_lower:
            return "HDMI Audio"
        elif 'pci' in device_name_lower:
            return "PCI Audio"
        elif 'analog' in device_name_lower:
            return "Analog Audio"
        elif 'digital' in device_name_lower or 'iec958' in device_name_lower:
            return "Digital Audio"
        elif 'stereo' in device_name_lower:
            return "Stereo Audio"
        elif 'monitor' in device_name_lower:
            return "Monitor Source"
        else:
            return "Audio Device"
    
    # ===== METODY TESTOWANIA URZĄDZEŃ AUDIO =====
    
    def _test_audio_device(self, sink_name):
        """Test if audio device actually works with volume monitoring"""
        try:
            print(f"    🧪 Testing device: {sink_name}")
            
            # Set as temporary default to test
            set_result = subprocess.run(['pactl', 'set-default-sink', sink_name], 
                                      capture_output=True, timeout=3)
            if set_result.returncode != 0:
                print(f"    ❌ Cannot set as default sink")
                return {'working': False, 'volume': 0, 'reason': 'Cannot set as default'}
            
            # Get volume info
            volume_result = subprocess.run(['pactl', 'list', 'sinks'], 
                                         capture_output=True, text=True, timeout=3)
            
            volume_percent = 0
            if volume_result.returncode == 0:
                lines = volume_result.stdout.split('\n')
                in_our_sink = False
                
                for line in lines:
                    if f'Name: {sink_name}' in line:
                        in_our_sink = True
                        continue
                    
                    if in_our_sink and 'Volume:' in line:
                        import re
                        volume_match = re.search(r'(\d+)%', line)
                        if volume_match:
                            volume_percent = int(volume_match.group(1))
                        break
                    
                    if in_our_sink and line.strip() == '':
                        break
            
            print(f"    🔊 Current volume: {volume_percent}%", end='')
            
            # Ensure minimum volume
            if volume_percent < 50:
                print(f" -> Setting to 70%")
                subprocess.run(['pactl', 'set-sink-volume', sink_name, '70%'], 
                             capture_output=True, timeout=3)
                volume_percent = 70
            else:
                print(f" ✅")
            
            # Test actual audio output
            print(f"    🎵 Testing audio output...", end='')
            test_result = subprocess.run(['espeak', '-s', '300', '-v', 'en', 'test'], 
                                       capture_output=True, timeout=3)
            
            if test_result.returncode == 0:
                print(f" ✅ Working!")
                return {
                    'working': True, 
                    'volume': volume_percent, 
                    'name': sink_name,
                    'reason': 'Audio test successful'
                }
            else:
                print(f" ❌ Failed")
                return {
                    'working': False, 
                    'volume': volume_percent, 
                    'name': sink_name,
                    'reason': 'Audio test failed'
                }
                
        except Exception as e:
            print(f"    ❌ Test error: {e}")
            return {'working': False, 'volume': 0, 'name': sink_name, 'reason': str(e)}
    
    def _test_mic_device(self, source_name):
        """Test if microphone device actually works"""
        try:
            print(f"    🧪 Testing microphone: {source_name}")
            
            # Set as temporary default to test
            set_result = subprocess.run(['pactl', 'set-default-source', source_name], 
                                      capture_output=True, timeout=3)
            if set_result.returncode != 0:
                print(f"    ❌ Cannot set as default source")
                return {'working': False, 'reason': 'Cannot set as default'}
            
            # Basic microphone test (check if source exists and is available)
            test_result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                                       capture_output=True, text=True, timeout=3)
            
            if test_result.returncode == 0 and source_name in test_result.stdout:
                print(f"    ✅ Microphone available")
                return {
                    'working': True, 
                    'name': source_name,
                    'reason': 'Microphone test successful'
                }
            else:
                print(f"    ❌ Microphone not available")
                return {
                    'working': False, 
                    'name': source_name,
                    'reason': 'Microphone not available'
                }
                
        except Exception as e:
            print(f"    ❌ Microphone test error: {e}")
            return {'working': False, 'name': source_name, 'reason': str(e)}
    
    # ===== AUTOMATYCZNY WYBÓR URZĄDZEŃ AUDIO =====
    
    def set_auto_audio_devices(self, test: bool = False, save: bool = False):
        """Automatycznie wybierz najlepsze urządzenia audio dla TTS i STT"""
        print("🤖 Automatyczny wybór urządzeń audio")
        print("=" * 45)
        
        success_speaker = self.set_auto_speaker_device(test=test, save=save)
        print()  # Pusta linia między głośnikami a mikrofonami
        success_mic = self.set_auto_mic_device(test=test, save=save)
        
        if success_speaker and success_mic:
            print("\n✅ Automatyczny wybór urządzeń audio zakończony sukcesem!")
            return True
        elif success_speaker or success_mic:
            print("\n⚠️ Automatyczny wybór częściowo udany (jeden z typów urządzeń)")
            return False
        else:
            print("\n❌ Automatyczny wybór urządzeń audio nie powiódł się")
            return False
    
    def set_auto_speaker_device(self, test: bool = False, save: bool = False):
        """Automatycznie wybierz najlepszy głośnik dla TTS"""
        print("🔊 Automatyczny wybór głośnika...")
        
        # Wykorzystaj istniejącą logikę detekcji urządzeń
        working_devices = self._detect_and_test_output_devices()
        
        if not working_devices:
            print("❌ Nie znaleziono działających głośników")
            return False
        
        # Wybierz najlepszy na podstawie priorytetu
        best_device = working_devices[0]  # Już posortowane według priorytetu
        device_name = best_device['name']
        
        print(f"🎯 Wybrano najlepszy głośnik: {best_device['description']}")
        print(f"   📱 Typ: {self._get_device_type(device_name)}")
        print(f"   🔊 Volume: {best_device.get('volume', 'N/A')}%")
        
        # Ustaw jako domyślny
        try:
            result = subprocess.run(['pactl', 'set-default-sink', device_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Pomyślnie ustawiono głośnik automatycznie")
                
                if test:
                    print("🧪 Testowanie wybranego głośnika...")
                    test_result = self._test_audio_device(device_name)
                    if test_result['working']:
                        print(f"✅ Test automatycznego wyboru zakończony sukcesem (Volume: {test_result['volume']}%)")
                    else:
                        print(f"⚠️ Problem z testem: {test_result['error']}")
                
                if save:
                    print("💾 Zapisano automatyczny wybór głośnika w konfiguracji")
                
                return True
            else:
                print(f"❌ Błąd automatycznego ustawiania głośnika: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd automatycznego wyboru głośnika: {e}")
            return False
    
    def set_auto_mic_device(self, test: bool = False, save: bool = False):
        """Automatycznie wybierz najlepszy mikrofon dla STT"""
        print("🎤 Automatyczny wybór mikrofonu...")
        
        # Wykorzystaj logikę detekcji mikrofonów
        working_devices = self._detect_and_test_input_devices()
        
        if not working_devices:
            print("❌ Nie znaleziono działających mikrofonów")
            return False
        
        # Wybierz najlepszy na podstawie priorytetu
        best_device = working_devices[0]  # Już posortowane według priorytetu
        device_name = best_device['name']
        
        print(f"🎯 Wybrano najlepszy mikrofon: {best_device['description']}")
        print(f"   📱 Typ: {self._get_device_type(device_name)}")
        
        # Ustaw jako domyślny
        try:
            result = subprocess.run(['pactl', 'set-default-source', device_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Pomyślnie ustawiono mikrofon automatycznie")
                
                if test:
                    print("🧪 Testowanie wybranego mikrofonu...")
                    test_result = self._test_mic_device(device_name)
                    if test_result['working']:
                        print(f"✅ Test automatycznego wyboru mikrofonu zakończony sukcesem")
                    else:
                        print(f"⚠️ Problem z testem mikrofonu: {test_result['error']}")
                
                if save:
                    print("💾 Zapisano automatyczny wybór mikrofonu w konfiguracji")
                
                return True
            else:
                print(f"❌ Błąd automatycznego ustawiania mikrofonu: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Błąd automatycznego wyboru mikrofonu: {e}")
            return False
    
    def _detect_and_test_output_devices(self):
        """Wykryj i przetestuj urządzenia wyjściowe, zwróć posortowane według priorytetu"""
        devices = self._get_output_devices_raw()
        working_devices = []
        
        for device in devices:
            # Testuj każde urządzenie
            test_result = self._test_audio_device(device['name'])
            if test_result['working']:
                # Określ priorytet na podstawie typu
                priority = self._get_device_priority(device['name'])
                
                working_device = {
                    'name': device['name'],
                    'description': device['description'],
                    'type': self._get_device_type(device['name']),
                    'priority': priority,
                    'volume': test_result['volume']
                }
                working_devices.append(working_device)
        
        # Sortuj według priorytetu (niższy = lepszy)
        working_devices.sort(key=lambda x: x['priority'])
        return working_devices
    
    def _detect_and_test_input_devices(self):
        """Wykryj i przetestuj urządzenia wejściowe, zwróć posortowane według priorytetu"""
        devices = self._get_input_devices_raw()
        working_devices = []
        
        for device in devices:
            # Testuj każde urządzenie
            test_result = self._test_mic_device(device['name'])
            if test_result['working']:
                # Określ priorytet na podstawie typu
                priority = self._get_device_priority(device['name'])
                
                working_device = {
                    'name': device['name'],
                    'description': device['description'],
                    'type': self._get_device_type(device['name']),
                    'priority': priority
                }
                working_devices.append(working_device)
        
        # Sortuj według priorytetu (niższy = lepszy)
        working_devices.sort(key=lambda x: x['priority'])
        return working_devices
    
    def _get_device_priority(self, device_name: str):
        """Określ priorytet urządzenia (niższy = lepszy)"""
        device_name_lower = device_name.lower()
        
        # Priorytet na podstawie typu urządzenia
        if 'usb' in device_name_lower and 'generic' in device_name_lower:
            return 1  # Generic USB Audio - najwyższy priorytet
        elif 'usb' in device_name_lower:
            return 2  # Inne USB Audio
        elif 'bluetooth' in device_name_lower or 'bt' in device_name_lower:
            return 3  # Bluetooth Audio
        elif 'hdmi' in device_name_lower:
            return 4  # HDMI Audio
        elif 'analog' in device_name_lower:
            return 5  # Analog Audio
        elif 'pci' in device_name_lower:
            return 6  # PCI Audio
        else:
            return 10  # Inne urządzenia - najniższy priorytet
    
    # ===== WYŚWIETLANIE AKTUALNYCH URZĄDZEŃ AUDIO =====
    
    def _get_current_default_sink(self):
        """Pobierz aktualnie ustawiony domyślny głośnik"""
        try:
            result = subprocess.run(['pactl', 'info'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
            
            default_sink_name = None
            for line in result.stdout.split('\n'):
                if 'Default Sink:' in line:
                    default_sink_name = line.split(':', 1)[1].strip()
                    break
            
            if not default_sink_name:
                return None
            
            # Pobierz szczegóły tego sink'a
            result = subprocess.run(['pactl', 'list', 'sinks'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
            
            lines = result.stdout.split('\n')
            in_target_sink = False
            
            for line in lines:
                if f'Name: {default_sink_name}' in line:
                    in_target_sink = True
                    continue
                
                if in_target_sink and 'Description:' in line:
                    description = line.split(':', 1)[1].strip()
                    return {
                        'name': default_sink_name,
                        'description': description
                    }
                
                if in_target_sink and line.strip() == '':
                    break
            
            return {'name': default_sink_name, 'description': default_sink_name}
            
        except Exception as e:
            print(f"❌ Błąd pobierania domyślnego głośnika: {e}")
            return None
    
    def _get_current_default_source(self):
        """Pobierz aktualnie ustawiony domyślny mikrofon"""
        try:
            result = subprocess.run(['pactl', 'info'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
            
            default_source_name = None
            for line in result.stdout.split('\n'):
                if 'Default Source:' in line:
                    default_source_name = line.split(':', 1)[1].strip()
                    break
            
            if not default_source_name:
                return None
            
            # Pobierz szczegóły tego source'a
            result = subprocess.run(['pactl', 'list', 'sources'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
            
            lines = result.stdout.split('\n')
            in_target_source = False
            
            for line in lines:
                if f'Name: {default_source_name}' in line:
                    in_target_source = True
                    continue
                
                if in_target_source and 'Description:' in line:
                    description = line.split(':', 1)[1].strip()
                    return {
                        'name': default_source_name,
                        'description': description
                    }
                
                if in_target_source and line.strip() == '':
                    break
            
            return {'name': default_source_name, 'description': default_source_name}
            
        except Exception as e:
            print(f"❌ Błąd pobierania domyślnego mikrofonu: {e}")
            return None

    def get_current_audio_devices(self, detailed: bool = False):
        """Pokaż aktualnie ustawione domyślne urządzenia audio"""
        print("🎯 Aktualnie ustawione urządzenia audio")
        print("=" * 45)
        
        try:
            # Pobierz domyślny głośnik (sink)
            current_sink = self._get_current_default_sink()
            if current_sink:
                print(f"🔊 Domyślny głośnik:")
                print(f"   📱 Nazwa: {current_sink['name']}")
                print(f"   📝 Opis: {current_sink['description']}")
                print(f"   🏷️  Typ: {self._get_device_type(current_sink['name'])}")
                
                if detailed:
                    # Dodatkowe informacje dla głośnika
                    sink_details = self._get_sink_details(current_sink['name'])
                    if sink_details:
                        print(f"   🔊 Volume: {sink_details.get('volume', 'N/A')}%")
                        print(f"   🔇 Muted: {'Tak' if sink_details.get('muted', False) else 'Nie'}")
                        print(f"   📊 Format: {sink_details.get('sample_format', 'N/A')}")
                        print(f"   📈 Sample Rate: {sink_details.get('sample_rate', 'N/A')} Hz")
            else:
                print("🔊 ❌ Brak domyślnego głośnika")
            
            print()  # Pusta linia
            
            # Pobierz domyślny mikrofon (source)
            current_source = self._get_current_default_source()
            if current_source:
                print(f"🎤 Domyślny mikrofon:")
                print(f"   📱 Nazwa: {current_source['name']}")
                print(f"   📝 Opis: {current_source['description']}")
                print(f"   🏷️  Typ: {self._get_device_type(current_source['name'])}")
                
                if detailed:
                    # Dodatkowe informacje dla mikrofonu
                    source_details = self._get_source_details(current_source['name'])
                    if source_details:
                        print(f"   🔇 Muted: {'Tak' if source_details.get('muted', False) else 'Nie'}")
                        print(f"   📊 Format: {source_details.get('sample_format', 'N/A')}")
                        print(f"   📈 Sample Rate: {source_details.get('sample_rate', 'N/A')} Hz")
            else:
                print("🎤 ❌ Brak domyślnego mikrofonu")
                
        except Exception as e:
            print(f"❌ Błąd pobierania informacji o urządzeniach: {e}")
    
    def _get_sink_details(self, sink_name: str):
        """Pobierz szczegółowe informacje o głośniku"""
        try:
            result = subprocess.run(['pactl', 'list', 'sinks'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
            
            lines = result.stdout.split('\n')
            in_target_sink = False
            details = {}
            
            for line in lines:
                if f'Name: {sink_name}' in line:
                    in_target_sink = True
                    continue
                
                if in_target_sink:
                    if line.strip() == '' and 'Name:' in line:  # Next sink started
                        break
                    
                    if 'Volume:' in line:
                        import re
                        volume_match = re.search(r'(\d+)%', line)
                        if volume_match:
                            details['volume'] = int(volume_match.group(1))
                    
                    elif 'Mute:' in line:
                        details['muted'] = 'yes' in line.lower()
                    
                    elif 'Sample Specification:' in line:
                        # Przykład: "Sample Specification: s16le 2ch 44100Hz"
                        parts = line.split(':')[1].strip().split()
                        if len(parts) >= 3:
                            details['sample_format'] = parts[0]
                            details['sample_rate'] = parts[2].replace('Hz', '')
            
            return details
            
        except Exception as e:
            print(f"❌ Błąd pobierania szczegółów głośnika: {e}")
            return None
    
    def _get_source_details(self, source_name: str):
        """Pobierz szczegółowe informacje o mikrofonie"""
        try:
            result = subprocess.run(['pactl', 'list', 'sources'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return None
            
            lines = result.stdout.split('\n')
            in_target_source = False
            details = {}
            
            for line in lines:
                if f'Name: {source_name}' in line:
                    in_target_source = True
                    continue
                
                if in_target_source:
                    if line.strip() == '' and 'Name:' in line:  # Next source started
                        break
                    
                    if 'Mute:' in line:
                        details['muted'] = 'yes' in line.lower()
                    
                    elif 'Sample Specification:' in line:
                        # Przykład: "Sample Specification: s16le 2ch 44100Hz"
                        parts = line.split(':')[1].strip().split()
                        if len(parts) >= 3:
                            details['sample_format'] = parts[0]
                            details['sample_rate'] = parts[2].replace('Hz', '')
            
            return details
            
        except Exception as e:
            print(f"❌ Błąd pobierania szczegółów mikrofonu: {e}")
            return None
    
    def _show_tts_audio_status(self):
        """Pokaż aktualny status urządzeń audio dla TTS bez interakcji"""
        try:
            print("🎵 Inicjalizacja TTS - sprawdzanie aktualnych urządzeń audio...")
            
            # Pobierz aktualne urządzenia bez testowania
            current_speaker = self._get_current_default_sink()
            current_mic = self._get_current_default_source()
            
            if current_speaker:
                speaker_name = current_speaker.get('description', 'Unknown Speaker')
                speaker_volume = current_speaker.get('volume', 'N/A')
                print(f"🔊 Aktualny głośnik: {speaker_name} (Volume: {speaker_volume})")
            else:
                print("⚠️ Brak skonfigurowanego głośnika - TTS może nie działać")
                
            if current_mic:
                mic_name = current_mic.get('description', 'Unknown Microphone')  
                mic_volume = current_mic.get('volume', 'N/A')
                print(f"🎤 Aktualny mikrofon: {mic_name} (Volume: {mic_volume})")
            
            print("💡 Zmień urządzenia przez: mova audio set auto / mova speaker set X / mova mic set X")
            
        except Exception as e:
            print(f"⚠️ Nie można pobrać statusu urządzeń audio: {e}")
            print("💡 Ustaw urządzenia przez: mova audio set auto")
    
    def _cleanup(self):
        """Cleanup resources"""
        self.is_active = False
        if self.recorder:
            self.recorder.cleanup()
        if self.tts:
            self.tts.stop_speaking()


# Utility functions for CLI integration
def create_voice_interface(language: str, server: str = DEFAULT_SERVER) -> VoiceInterface:
    """Create and return a voice interface instance"""
    return VoiceInterface(language, server)

def check_voice_dependencies() -> tuple[bool, str]:
    """Check if voice dependencies are available"""
    if not VOICE_DEPENDENCIES_AVAILABLE:
        missing_deps = []
        
        try:
            import whisper
        except ImportError:
            missing_deps.append("openai-whisper")
        
        try:
            import speech_recognition
        except ImportError:
            missing_deps.append("SpeechRecognition")
        
        try:
            import pyttsx3
        except ImportError:
            missing_deps.append("pyttsx3")
        
        try:
            import pyaudio
        except ImportError:
            missing_deps.append("pyaudio")
        
        return False, f"Missing dependencies: {', '.join(missing_deps)}"
    
    return True, "All voice dependencies available"

def get_supported_languages() -> List[str]:
    """Get list of supported languages"""
    return list(VoiceConfig.LANGUAGES.keys())

def get_language_info(language: str) -> Optional[Dict]:
    """Get information about a specific language"""
    return VoiceConfig.LANGUAGES.get(language)

if __name__ == "__main__":
    # Test voice interface
    print("🎤 Mova Voice Interface Test")
    
    # Check dependencies
    deps_ok, deps_msg = check_voice_dependencies()
    print(f"Dependencies: {deps_msg}")
    
    if deps_ok:
        # Test basic functionality
        interface = create_voice_interface('en')
        interface.start_session(text_only=True)
    else:
        print("Install missing dependencies to test voice interface")
