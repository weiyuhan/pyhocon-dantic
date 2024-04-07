import json
import os
from typing import Any, Dict, Tuple, Type

import pyhocon
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


class HoconConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: Type[BaseSettings], config_path: str):
        self.hocon_config = pyhocon.ConfigFactory.parse_file(config_path)
        super().__init__(settings_cls)

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        if field.alias or field.validation_alias:
            field_name = str(field.alias) or str(field.validation_alias)
            value = self.hocon_config.get(field.alias)
        else:
            value = self.hocon_config.get(field_name)

        return value, field_name, type(value) in (dict, list, pyhocon.ConfigTree)

    def decode_complex_value(
        self, field_name: str, field: FieldInfo, value: Any
    ) -> Any:
        if isinstance(value, pyhocon.ConfigTree):
            return dict(value)
        if isinstance(value, list):
            return list(value)
        if isinstance(value, pyhocon.ConfigList):
            return list(value)
        return json.loads(value)

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value
        return d


class HoconSettings(BaseSettings):
    def __init__(self, **data: Any):
        super().__init__(**data)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # read hocon config path from environment variable
        hocon_config_path = None
        if os.getenv("HOCON_CONFIG_PATH"):
            hocon_config_path = os.getenv("HOCON_CONFIG_PATH")

        if not hocon_config_path:
            raise ValueError(
                "hocon_config_path not set, please set it in environment variable HOCON_CONFIG_PATH"
            )

        return (
            init_settings,
            env_settings,
            HoconConfigSettingsSource(settings_cls, hocon_config_path),
            dotenv_settings,
            file_secret_settings,
        )
