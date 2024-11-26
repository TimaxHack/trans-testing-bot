from dataclasses import dataclass
from typing import List, Dict
from environs import Env

@dataclass
class APIConfig:
    deep_foundation_key: str
    # Add other API keys here if needed

@dataclass
class BotConfig:
    bot_token: str
    api: APIConfig
    models: List[str]

def load_config() -> BotConfig or None:
    try:
        env = Env()
        return BotConfig(
            bot_token=env.str("TELEGRAM_API_TOKEN"),
            api=APIConfig(
                deep_foundation_key=env.str("API_KEY")
                # Add keys for other APIs here
            ),
            models=env.list("MODELS", subcast=str, default=["whisper-1", "whisper-2", "another_model"]) # Default models
        )
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")
        return None

