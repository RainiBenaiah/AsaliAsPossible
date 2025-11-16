from pydantic import BaseModel

class UserSettings(BaseModel):
    user_id: str
    temperature_alerts: bool = True
    weight_monitoring: bool = True
    sound_analysis: bool = True
    push_notifications: bool = True
    email_alerts: bool = False
    data_backup: bool = True
    monitoring_frequency: str = "Every 15 minutes"
    alert_threshold: str = "Medium and High priority"

class SettingsUpdate(BaseModel):
    temperature_alerts: bool
    weight_monitoring: bool
    sound_analysis: bool
    push_notifications: bool
    email_alerts: bool
    data_backup: bool
    monitoring_frequency: str
    alert_threshold: str