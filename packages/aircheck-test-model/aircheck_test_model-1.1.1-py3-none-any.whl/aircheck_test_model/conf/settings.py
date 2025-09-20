from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "AIRCHECK-model"
    debug: bool = False
