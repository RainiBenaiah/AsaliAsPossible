"""
Diagnostic script to find and test your audio model
Run this to check where your model is and if it loads correctly

Usage:
    cd backend
    python check_audio_model.py
"""

import sys
from pathlib import Path
import traceback

print("=" * 70)
print("AUDIO MODEL DIAGNOSTIC")
print("=" * 70)

# Check for model files
print("\n1. SEARCHING FOR MODEL FILES...")
print("-" * 70)

model_locations = [
    "ml_models/audio/sound_classifier_cnn_lstm.keras",
    "ml_models/audio/sound_classifier_cnn_lstm.h5",
    "ml_models/sound_classifier_cnn_lstm.keras",
    "audio\sound_classifier_cnn_lstm.keras",
    "services/sound_classifier_cnn_lstm.keras",
    "sound_classifier_cnn_lstm.keras",
]

found_models = []

for loc in model_locations:
    path = Path(loc)
    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        found_models.append((loc, size_mb))
        print(f"   FOUND: {loc} ({size_mb:.2f} MB)")

if not found_models:
    print("   NO MODEL FILES FOUND in standard locations")
    print("\n   Searching entire ml_models directory...")
    
    if Path("ml_models").exists():
        keras_files = list(Path("ml_models").rglob("*.keras"))
        h5_files = list(Path("ml_models").rglob("*.h5"))
        all_models = keras_files + h5_files
        
        if all_models:
            print(f"\n   Found {len(all_models)} model file(s):")
            for model_file in all_models:
                size_mb = model_file.stat().st_size / (1024 * 1024)
                print(f"      {model_file} ({size_mb:.2f} MB)")
                found_models.append((str(model_file), size_mb))
        else:
            print("   No .keras or .h5 files found in ml_models directory")
    else:
        print("   ml_models directory doesn't exist!")

if not found_models:
    print("\n" + "=" * 70)
    print("ERROR: No model files found!")
    print("=" * 70)
    print("\nPlease tell me:")
    print("1. Where is your model file located?")
    print("2. What is the file name?")
    print("3. What format is it (.keras, .h5, .pb)?")
    sys.exit(1)

# Try to load TensorFlow
print("\n2. CHECKING TENSORFLOW...")
print("-" * 70)

try:
    import tensorflow as tf
    print(f"   TensorFlow version: {tf.__version__}")
    print("   TensorFlow: OK")
except ImportError as e:
    print("   ERROR: TensorFlow not installed!")
    print(f"   {e}")
    print("\n   Install with: pip install tensorflow --break-system-packages")
    sys.exit(1)

# Try to load each model
print("\n3. TESTING MODEL LOADING...")
print("-" * 70)

working_model = None

for model_path, size_mb in found_models:
    print(f"\nTesting: {model_path}")
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"   SUCCESS: Model loaded!")
        print(f"   Model summary:")
        
        # Get input shape
        if hasattr(model, 'input_shape'):
            print(f"      Input shape: {model.input_shape}")
        
        # Get output shape
        if hasattr(model, 'output_shape'):
            print(f"      Output shape: {model.output_shape}")
        
        # Count parameters
        total_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
        print(f"      Parameters: {total_params:,}")
        
        working_model = model_path
        print(f"\n   THIS MODEL WORKS!")
        break
        
    except Exception as e:
        print(f"   FAILED: {e}")
        print("   Traceback:")
        traceback.print_exc()

if not working_model:
    print("\n" + "=" * 70)
    print("ERROR: No models could be loaded!")
    print("=" * 70)
    print("\nPossible issues:")
    print("1. Model file is corrupted")
    print("2. Model was saved with different TensorFlow version")
    print("3. Model format is incompatible")
    print("\nPlease share:")
    print("- How you trained/saved the model")
    print("- TensorFlow version used for training")
    print("- Any error messages above")
    sys.exit(1)

# Test with audio service
print("\n4. TESTING AUDIO SERVICE...")
print("-" * 70)

try:
    # Temporarily update the path if needed
    if working_model != "ml_models/audio/sound_classifier_cnn_lstm.keras":
        print(f"   NOTE: Your model is at: {working_model}")
        print(f"   But audio_service.py expects: ml_models/audio/sound_classifier_cnn_lstm.keras")
        print(f"\n   You should either:")
        print(f"   A) Move model to: ml_models/audio/sound_classifier_cnn_lstm.keras")
        print(f"   B) Update audio_service.py model_path to: {working_model}")
    
    from services.audio_service import get_audio_service
    service = get_audio_service()
    
    if service.model is not None and not service.mock_mode:
        print("\n   SUCCESS: Audio service loaded with REAL model!")
        print(f"   Model path: {service.model_path}")
    elif service.mock_mode:
        print("\n   WARNING: Audio service is in MOCK mode")
        print("   This means it couldn't load your model")
        print(f"\n   Expected path: {service.model_path}")
        print(f"   Actual model location: {working_model}")
    
except Exception as e:
    print(f"\n   ERROR loading audio service: {e}")
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if working_model:
    print(f"\nYour model file: {working_model}")
    print(f"Expected location: ml_models/audio/sound_classifier_cnn_lstm.keras")
    
    if working_model == "ml_models/audio/sound_classifier_cnn_lstm.keras":
        print("\nStatus: PERFECT! Model is in the correct location")
    else:
        print("\nAction needed:")
        print(f"\nOption A - Move the model (recommended):")
        print(f"   mkdir -p ml_models/audio/")
        print(f"   cp {working_model} ml_models/audio/sound_classifier_cnn_lstm.keras")
        
        print(f"\nOption B - Update audio_service.py:")
        print(f"   Change line: model_path = 'ml_models/audio/sound_classifier_cnn_lstm.keras'")
        print(f"   To: model_path = '{working_model}'")

print("\n" + "=" * 70)