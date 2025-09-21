import os
from enum import StrEnum
from pathlib import Path

from loguru import logger
from pydantic import AnyHttpUrl, BaseModel, SecretStr, field_validator, model_validator


class KonaEndpointType(StrEnum):
    HTTP = 'http'
    HTTPS = 'https'
    SOCAT = 'socat'
    NC = 'nc'
    NCAT_SSL = 'ncat-ssl'


class KonaChallengeItem(BaseModel):
    class CTFD(BaseModel):
        class ChallengeState(StrEnum):
            VISIBLE = 'visible'
            HIDDEN = 'hidden'

        class Hint(BaseModel):
            hint: str
            cost: int = 0
            title: str | None = None

        state: ChallengeState = ChallengeState.VISIBLE
        type: str = 'dynamic'
        topics: list[str] = []
        tags: list[str] = []
        hints: list[Hint] = []
        connection_info: str = ''

    class Scoring(BaseModel):
        class CTFD(BaseModel):
            decay_function: str = 'logarithmic'
            decay: int = 60
            max_attempts: int = 0

        class RCTF(BaseModel):
            eligible_for_tiebreaks: bool = True

        ctfd: CTFD = CTFD()
        rctf: RCTF = RCTF()
        initial_value: int = 500
        minimum_value: int = 100

    class Flags(BaseModel):
        class CTFDFlag(BaseModel):
            type: str = 'static'
            flag: str

        rctf: str = ''
        ctfd: list[CTFDFlag] = []

    class Endpoint(BaseModel):
        name: str | None = None
        type: KonaEndpointType
        endpoint: str
        port: int | None = None

        @property
        def name_prefix(self) -> str:
            return f'{self.name}: ' if self.name else ''

        @property
        def http_port_if_needed(self) -> str:
            return f':{self.port}' if self.port else ''

        @property
        def http_endpoint(self) -> str:
            return f'{self.type.value}://{self.endpoint}{self.http_port_if_needed}'

    category: str
    name: str
    author: str

    description: str

    attachments: list[str] = []

    scoring: Scoring = Scoring()
    flags: Flags = Flags()
    endpoints: list[Endpoint] = []

    ctfd: CTFD = CTFD()

    @property
    def challenge_id(self) -> str:
        return f'{self.category}_{self.name}'

    @field_validator('description')
    @classmethod
    def strip_description(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode='after')
    def flag_is_set(self) -> 'KonaChallengeItem':
        if self.flags.rctf or self.flags.ctfd:
            return self
        msg = f'At least one flag must be set for challenge {self.challenge_id}'
        raise ValueError(msg)

    @model_validator(mode='after')
    def warn_attachments(self) -> 'KonaChallengeItem':
        if not self.attachments:
            logger.warning(f'No attachments set for challenge {self.challenge_id}')
        return self


class KonaChallengeConfig(BaseModel):
    class DiscoveryConfig(BaseModel):
        skip: bool = False

    discovery: DiscoveryConfig = DiscoveryConfig()
    challenges: list[KonaChallengeItem] = []


class KonaSecret(BaseModel):
    file_path: Path | None = None
    value: SecretStr | None = None
    env: str | None = None

    _loaded_value_do_not_use: SecretStr | None = None

    @field_validator('file_path')
    @classmethod
    def file_must_exist(cls, v: Path | None) -> Path | None:
        if v is None:
            return v
        if not v.exists():
            msg = f'file_path does not exist: {v}'
            raise ValueError(msg)
        if not v.is_file():
            msg = f'file_path is not a file: {v}'
            raise ValueError(msg)
        return v

    @model_validator(mode='after')
    def exactly_one_of(self) -> 'KonaSecret':
        provided = [f for f in ('file_path', 'value', 'env') if getattr(self, f) is not None]
        if len(provided) != 1:
            msg = 'exactly one of file_path, value, env must be provided'
            raise ValueError(msg)
        return self

    @property
    def loaded(self) -> str:
        if self.value is not None:
            return self.value.get_secret_value()

        if self._loaded_value_do_not_use is not None:
            return self._loaded_value_do_not_use.get_secret_value()

        if self.file_path is not None:
            self._loaded_value_do_not_use = SecretStr(self.file_path.read_text())
            return self._loaded_value_do_not_use.get_secret_value()

        if self.env is not None:
            value = os.getenv(self.env)
            if value is None:
                msg = f'Environment variable {self.env} is not set'
                raise ValueError(msg)
            self._loaded_value_do_not_use = SecretStr(value)
            return self._loaded_value_do_not_use.get_secret_value()

        raise RuntimeError


class KonaSecretOrValue(BaseModel):
    secret: str | None = None
    value: SecretStr | None = None

    @model_validator(mode='after')
    def exactly_one_of(self) -> 'KonaSecretOrValue':
        provided = [f for f in ('secret', 'value') if getattr(self, f) is not None]
        if len(provided) != 1:
            msg = 'exactly one of secret, value must be provided'
            raise ValueError(msg)
        return self

    def load(self, global_config: 'KonaGlobalConfig') -> str:
        if self.secret is not None:
            return global_config.secrets[self.secret].loaded
        if self.value is not None:
            return self.value.get_secret_value()
        raise RuntimeError


class KonaRCTFCredentials(BaseModel):
    base_url: AnyHttpUrl
    team_token: KonaSecretOrValue


class KonaCTFDCredentials(BaseModel):
    base_url: AnyHttpUrl
    admin_token: KonaSecretOrValue


class KonaDiscoveryConfig(BaseModel):
    challenge_folder_depth: int = 3


class KonaTemplatesConfig(BaseModel):
    # TODO(es3n1n): inlining text here is ugly, consider loading from files
    challenge_description: str = (
        '{{ challenge.description }}\n\n{{ endpoints_rendered.strip() }}\n\n**Author**: {{ challenge.author }}'
    )
    endpoints_text: str = """{% for endpoint in challenge.endpoints -%}
{% if endpoint.type == models.KonaEndpointType.SOCAT %}
{{ endpoint.name_prefix }}`socat -,raw,echo=0 tcp:{{ endpoint.endpoint }}:{{ endpoint.port or 1337 }}`
{% elif endpoint.type == models.KonaEndpointType.NC %}
{{ endpoint.name_prefix }}`nc {{ endpoint.endpoint }} {{ endpoint.port or 1337 }}`
{% elif endpoint.type == models.KonaEndpointType.NCAT_SSL %}
{{ endpoint.name_prefix }}`ncat --ssl {{ endpoint.endpoint }} {{ endpoint.port or 1337 }}`
{% elif endpoint.type in (models.KonaEndpointType.HTTP, models.KonaEndpointType.HTTPS) %}
{% if endpoint.name -%}
[{{ endpoint.name }}]({{ endpoint.http_endpoint }})
{% else -%}
[{{ endpoint.http_endpoint }}]({{ endpoint.http_endpoint }})
{% endif -%}
{% else -%}
unknown endpoint type {{ endpoint.type }}
{% endif -%}
{% endfor -%}"""
    ctfd_attribution: str = '**Author**: {{ challenge.author }}'

    @field_validator('challenge_description', 'endpoints_text', 'ctfd_attribution')
    @classmethod
    def strip_values(cls, v: str) -> str:
        return v.strip()


class KonaGlobalConfig(BaseModel):
    discovery: KonaDiscoveryConfig = KonaDiscoveryConfig()
    secrets: dict[str, KonaSecret] = {}
    rctf: KonaRCTFCredentials | None = None
    ctfd: KonaCTFDCredentials | None = None
    templates: KonaTemplatesConfig = KonaTemplatesConfig()
