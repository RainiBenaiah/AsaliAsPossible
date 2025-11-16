import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Tuple, Dict
import traceback
import pickle

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("ERROR: TensorFlow not installed!")

class AudioService:
    """
    Service for processing audio files and extracting features
    
    CORRECTED Configuration (matching THE  model):
    - Sample rate: 22050 Hz
    - Duration: 10 seconds
    - Time steps: 431
    - Features: 120 total (40 MFCC + 80 Mel)
    - Model input shape: (None, 431, 120)
    """
    
    TARGET_SAMPLE_RATE = 22050
    TARGET_DURATION = 10
    N_MFCC = 40
    N_MELS = 80  # Changed from 128 to 80 to get 120 total features
    
    def __init__(self, model_path: str, label_encoder_path: str = None):
        """Load the audio classification model and label encoder"""
        self.model = None
        self.label_encoder = None
        self.class_names = ['active', 'inactive', 'queenless']
        self.model_path = model_path
        self.label_encoder_path = label_encoder_path
        self.mock_mode = True
        
        print("=" * 70)
        print("AUDIO SERVICE INITIALIZATION")
        print("=" * 70)
        
        # Check TensorFlow
        if not TF_AVAILABLE:
            print("ERROR: TensorFlow not available")
            return
        
        print(f"TensorFlow version: {tf.__version__}")
        
        # Load label encoder if provided
        if label_encoder_path:
            label_path = Path(label_encoder_path)
            if label_path.exists():
                try:
                    with open(label_encoder_path, 'rb') as f:
                        self.label_encoder = pickle.load(f)
                    print(f"Label encoder loaded from {label_encoder_path}")
                    if hasattr(self.label_encoder, 'classes_'):
                        self.class_names = list(self.label_encoder.classes_)
                        print(f"   Classes: {self.class_names}")
                except Exception as e:
                    print(f"WARNING: Could not load label encoder: {e}")
            else:
                print(f"WARNING: Label encoder not found at {label_encoder_path}")
        
        # Check model file
        model_file = Path(model_path)
        print(f"\nLooking for model at: {model_path}")
        
        if not model_file.exists():
            print(f"ERROR: Model file not found!")
            print(f"Checked: {model_file.absolute()}")
            return
        
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"Model file found: {size_mb:.2f} MB")
        
        # Load model
        try:
            print("Loading model...")
            self.model = tf.keras.models.load_model(model_path)
            self.mock_mode = False
            
            print("SUCCESS: Model loaded!")
            
            if hasattr(self.model, 'input_shape'):
                print(f"   Input shape: {self.model.input_shape}")
            if hasattr(self.model, 'output_shape'):
                print(f"   Output shape: {self.model.output_shape}")
            
            # Verify expected input shape
            expected_shape = self.model.input_shape
            if expected_shape:
                expected_features = expected_shape[-1]
                actual_features = self.N_MFCC + self.N_MELS
                
                if expected_features != actual_features:
                    print(f"\n   WARNING: Feature mismatch!")
                    print(f"   Model expects: {expected_features} features")
                    print(f"   Service provides: {actual_features} features")
                    print(f"   This will cause errors!")
                else:
                    print(f"   Feature dimensions match: {actual_features} features")
            
            total_params = sum([tf.keras.backend.count_params(w) for w in self.model.trainable_weights])
            print(f"   Parameters: {total_params:,}")
            
            print(f"\nConfiguration:")
            print(f"   MFCC coefficients: {self.N_MFCC}")
            print(f"   Mel bands: {self.N_MELS}")
            print(f"   Total features: {self.N_MFCC + self.N_MELS}")
            print(f"   Sample rate: {self.TARGET_SAMPLE_RATE} Hz")
            print(f"   Duration: {self.TARGET_DURATION} seconds")
            
            print("\nREADY: Using REAL model for classification")
            
        except Exception as e:
            print(f"ERROR: Failed to load model!")
            print(f"Error: {e}")
            traceback.print_exc()
            self.model = None
            self.mock_mode = True
        
        print("=" * 70)
    
    def load_and_preprocess_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and preprocess"""
        try:
            audio, sr = librosa.load(
                audio_path, 
                sr=self.TARGET_SAMPLE_RATE,
                duration=self.TARGET_DURATION,
                mono=True
            )
            
            target_length = self.TARGET_SAMPLE_RATE * self.TARGET_DURATION
            if len(audio) < target_length:
                audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
            else:
                audio = audio[:target_length]
            
            return audio, sr
            
        except Exception as e:
            raise Exception(f"Error loading audio: {str(e)}")
    
    def extract_mfcc_features(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Extract MFCC features"""
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=self.N_MFCC,
            n_fft=2048,
            hop_length=512
        )
        return mfcc
    
    def extract_mel_spectrogram(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Extract Mel spectrogram features"""
        mel = librosa.feature.melspectrogram(
            y=audio,
            sr=sr,
            n_mels=self.N_MELS,  # Now 80 instead of 128
            n_fft=2048,
            hop_length=512
        )
        mel_db = librosa.power_to_db(mel, ref=np.max)
        return mel_db
    
    def prepare_features_for_model(self, mfcc: np.ndarray, mel: np.ndarray) -> np.ndarray:
        """
        Prepare features for model
        
        Stacks MFCC and Mel to get correct input shape:
        - MFCC: (40, 431) → transpose to (431, 40)
        - Mel: (80, 431) → transpose to (431, 80)
        - Combined: (431, 120)
        - With batch dimension: (1, 431, 120)
        """
        mfcc_transposed = mfcc.T  # (431, 40)
        mel_transposed = mel.T     # (431, 80)
        
        # Stack features: (431, 120) where 120 = 40 MFCC + 80 Mel
        combined_features = np.concatenate([mfcc_transposed, mel_transposed], axis=1)
        
        # Add batch dimension: (1, 431, 120)
        features = np.expand_dims(combined_features, axis=0)
        
        return features
    
    def _mock_classification(self, audio_path: str) -> Dict:
        """Mock classification for testing"""
        try:
            audio, sr = self.load_and_preprocess_audio(audio_path)
            energy = np.sum(audio ** 2) / len(audio)
            
            if energy > 0.01:
                probabilities = [0.75, 0.20, 0.05]
            elif energy > 0.001:
                probabilities = [0.40, 0.55, 0.05]
            else:
                probabilities = [0.20, 0.60, 0.20]
            
            predicted_class = self.class_names[np.argmax(probabilities)]
            confidence = max(probabilities)
            
            result = {
                'status': predicted_class,
                'confidence': round(confidence * 100, 1),
                'probabilities': {
                    self.class_names[0]: round(probabilities[0] * 100, 1),
                    self.class_names[1]: round(probabilities[1] * 100, 1),
                    self.class_names[2]: round(probabilities[2] * 100, 1),
                },
                'queenless_risk': round(probabilities[2] * 100, 1),
                'queen_present': predicted_class == 'active',
                'mock_mode': True
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'active',
                'confidence': 75.0,
                'probabilities': {
                    'active': 75.0,
                    'inactive': 20.0,
                    'queenless': 5.0,
                },
                'queenless_risk': 5.0,
                'queen_present': True,
                'mock_mode': True,
                'error': str(e)
            }
    
    def classify_audio(self, audio_path: str) -> Dict:
        """Complete pipeline: Load → Extract features → Classify"""
        
        if self.mock_mode or self.model is None:
            print(f"WARNING: Using mock classification (model not loaded)")
            return self._mock_classification(audio_path)
        
        try:
            print(f"Classifying with REAL model: {audio_path}")
            
            # Load and preprocess
            audio, sr = self.load_and_preprocess_audio(audio_path)
            print(f"   Audio loaded: {len(audio)} samples at {sr}Hz")
            
            # Extract features
            mfcc = self.extract_mfcc_features(audio, sr)
            mel = self.extract_mel_spectrogram(audio, sr)
            print(f"   Features extracted: MFCC {mfcc.shape}, Mel {mel.shape}")
            
            # Prepare for model
            features = self.prepare_features_for_model(mfcc, mel)
            print(f"   Input shape: {features.shape}")
            print(f"   Expected by model: {self.model.input_shape}")
            
            # Verify shape matches
            if features.shape[1:] != self.model.input_shape[1:]:
                raise ValueError(
                    f"Shape mismatch! Features: {features.shape}, "
                    f"Model expects: {self.model.input_shape}"
                )
            
            # Predict
            predictions = self.model.predict(features, verbose=0)
            probabilities = predictions[0]
            print(f"   Raw predictions: {probabilities}")
            
            # Get predicted class
            predicted_class_idx = np.argmax(probabilities)
            
            # Use label encoder if available
            if self.label_encoder is not None:
                predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
                print(f"   Decoded class: {predicted_class}")
            else:
                predicted_class = self.class_names[predicted_class_idx]
            
            confidence = float(probabilities[predicted_class_idx])
            print(f"   Result: {predicted_class} ({confidence*100:.1f}%)")
            
            # Build result with all class probabilities
            result = {
                'status': predicted_class,
                'confidence': round(confidence * 100, 1),
                'probabilities': {
                    self.class_names[i]: round(float(probabilities[i]) * 100, 1)
                    for i in range(len(self.class_names))
                },
                'queenless_risk': round(float(probabilities[self.class_names.index('queenless')] if 'queenless' in self.class_names else probabilities[-1]) * 100, 1),
                'queen_present': predicted_class == 'active',
                'mock_mode': False
            }
            
            return result
            
        except Exception as e:
            print(f"ERROR during classification: {e}")
            traceback.print_exc()
            print("Falling back to mock classification")
            return self._mock_classification(audio_path)
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate audio file meets requirements"""
        try:
            path = Path(file_path)
            if not path.exists():
                return False, "File not found"
            
            file_size = path.stat().st_size
            if file_size == 0:
                return False, "File is empty"
            if file_size > 50 * 1024 * 1024:
                return False, "File too large (max 50MB)"
            
            try:
                audio_info = sf.info(file_path)
                duration = audio_info.duration
                
                if duration < 1:
                    return False, f"Audio too short: {duration:.1f}s (minimum 1s)"
                if duration > 60:
                    return False, f"Audio too long: {duration:.1f}s (maximum 60s)"
                
                if audio_info.samplerate < 8000:
                    return False, f"Sample rate too low: {audio_info.samplerate}Hz"
                
                return True, f"Valid ({duration:.1f}s, {audio_info.samplerate}Hz)"
                
            except Exception as e:
                try:
                    y, sr = librosa.load(file_path, duration=1, sr=None)
                    if len(y) == 0:
                        return False, "Could not load audio data"
                    return True, "Valid (verified with librosa)"
                except Exception as e2:
                    return False, f"Could not load audio: {str(e2)}"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Singleton instance
_audio_service_instance = None

def get_audio_service() -> AudioService:
    """Get singleton instance of AudioService"""
    global _audio_service_instance
    
    if _audio_service_instance is None:
        model_path = "ml_models/audio/sound_classifier_cnn_lstm.keras"
        label_encoder_path = "ml_models/audio/label_encoder.pkl"
        
        _audio_service_instance = AudioService(
            model_path=model_path,
            label_encoder_path=label_encoder_path
        )
    
    return _audio_service_instance