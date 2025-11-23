"""
Lazy imports for ML services to speed up server startup.
Services are only imported when first accessed, not at startup.
"""

_audio_service = None
_forecasting_service = None
_rl_service = None

def get_audio_service_lazy():
    """Lazy load audio service on first access"""
    global _audio_service
    if _audio_service is None:
        from services.audio_service import get_audio_service
        _audio_service = get_audio_service()
    return _audio_service

def get_forecasting_service_lazy():
    """Lazy load forecasting service on first access"""
    global _forecasting_service
    if _forecasting_service is None:
        from services.forecasting_service import get_forecasting_service
        _forecasting_service = get_forecasting_service()
    return _forecasting_service

def get_rl_service_lazy():
    """Lazy load RL service on first access"""
    global _rl_service
    if _rl_service is None:
        from services.rl_service import get_rl_service
        _rl_service = get_rl_service()
    return _rl_service