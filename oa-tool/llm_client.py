"""
llm_client.py — LLM 호출 단일 창구
config.yaml의 provider/model 설정에 따라 Claude / OpenAI / Gemini를 투명하게 전환.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml


def _load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class LLMClient:
    """단일 인터페이스로 Claude / OpenAI / Gemini를 호출하는 클라이언트."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or _load_config()
        self.provider: str = self.config["provider"].lower()
        self.model: str = self.config["model"]
        self.max_tokens: int = self.config.get("max_tokens", 4096)
        self._client = self._init_client()

    # ------------------------------------------------------------------
    # 내부 초기화
    # ------------------------------------------------------------------

    def _init_client(self):
        api_key_env: str = self.config.get("api_key_env", "")
        api_key: str = os.environ.get(api_key_env, "")

        if self.provider == "claude":
            try:
                import anthropic  # noqa: PLC0415
            except ImportError:
                raise ImportError("anthropic 패키지가 설치되지 않았습니다: pip install anthropic")
            if not api_key:
                raise EnvironmentError(
                    f"환경변수 {api_key_env}가 설정되지 않았습니다."
                )
            return anthropic.Anthropic(api_key=api_key)

        elif self.provider == "openai":
            try:
                import openai  # noqa: PLC0415
            except ImportError:
                raise ImportError("openai 패키지가 설치되지 않았습니다: pip install openai")
            if not api_key:
                raise EnvironmentError(
                    f"환경변수 {api_key_env}가 설정되지 않았습니다."
                )
            import openai as _openai  # noqa: PLC0415
            return _openai.OpenAI(api_key=api_key)

        elif self.provider == "gemini":
            try:
                import google.generativeai as genai  # noqa: PLC0415
            except ImportError:
                raise ImportError(
                    "google-generativeai 패키지가 설치되지 않았습니다: "
                    "pip install google-generativeai"
                )
            if not api_key:
                raise EnvironmentError(
                    f"환경변수 {api_key_env}가 설정되지 않았습니다."
                )
            genai.configure(api_key=api_key)
            return genai

        else:
            raise ValueError(
                f"지원하지 않는 provider: '{self.provider}'. "
                "claude / openai / gemini 중 하나를 config.yaml에 설정하세요."
            )

    # ------------------------------------------------------------------
    # 공개 인터페이스
    # ------------------------------------------------------------------

    def chat(
        self,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.3,
    ) -> str:
        """
        LLM에 단일 메시지를 보내고 응답 텍스트를 반환한다.

        Args:
            user_message:  사용자(분석 요청) 메시지
            system_prompt: 시스템 지침 (선택)
            temperature:   생성 다양성 (0.0 ~ 1.0)

        Returns:
            LLM 응답 텍스트 (str)
        """
        if self.provider == "claude":
            return self._chat_claude(user_message, system_prompt, temperature)
        elif self.provider == "openai":
            return self._chat_openai(user_message, system_prompt, temperature)
        elif self.provider == "gemini":
            return self._chat_gemini(user_message, system_prompt, temperature)
        else:
            raise ValueError(f"지원하지 않는 provider: {self.provider}")

    def chat_stream(
        self,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.3,
    ):
        """
        LLM 응답을 청크(chunk) 단위로 스트리밍한다.

        Yields:
            str: 텍스트 청크
        """
        if self.provider == "claude":
            yield from self._stream_claude(user_message, system_prompt, temperature)
        elif self.provider == "openai":
            yield from self._stream_openai(user_message, system_prompt, temperature)
        elif self.provider == "gemini":
            yield from self._stream_gemini(user_message, system_prompt, temperature)
        else:
            raise ValueError(f"지원하지 않는 provider: {self.provider}")

    # ------------------------------------------------------------------
    # Provider별 구현
    # ------------------------------------------------------------------

    def _chat_claude(
        self, user_message: str, system_prompt: str, temperature: float
    ) -> str:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": user_message}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)
        return response.content[0].text

    def _chat_openai(
        self, user_message: str, system_prompt: str, temperature: float
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def _chat_gemini(
        self, user_message: str, system_prompt: str, temperature: float
    ) -> str:
        full_prompt = (
            f"{system_prompt}\n\n{user_message}" if system_prompt else user_message
        )
        model = self._client.GenerativeModel(self.model)
        generation_config = self._client.types.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=temperature,
        )
        response = model.generate_content(
            full_prompt, generation_config=generation_config
        )
        return response.text

    # ------------------------------------------------------------------
    # Provider별 스트리밍 구현
    # ------------------------------------------------------------------

    def _stream_claude(
        self, user_message: str, system_prompt: str, temperature: float
    ):
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": user_message}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        with self._client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text

    def _stream_openai(
        self, user_message: str, system_prompt: str, temperature: float
    ):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=temperature,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _stream_gemini(
        self, user_message: str, system_prompt: str, temperature: float
    ):
        full_prompt = (
            f"{system_prompt}\n\n{user_message}" if system_prompt else user_message
        )
        model = self._client.GenerativeModel(self.model)
        generation_config = self._client.types.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=temperature,
        )
        response = model.generate_content(
            full_prompt, generation_config=generation_config, stream=True
        )
        for chunk in response:
            # 일부 청크는 텍스트 없이 안전 등급/메타데이터만 포함하므로
            # ValueError가 발생할 수 있어 개별적으로 처리한다
            try:
                text = chunk.text
                if text:
                    yield text
            except (ValueError, AttributeError):
                continue

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------

    def load_prompt(self, prompt_name: str) -> str:
        """
        prompts/{prompt_name}.txt 파일을 읽어 반환한다.
        파일이 없으면 빈 문자열을 반환한다.
        """
        prompt_path = Path(__file__).parent / "prompts" / f"{prompt_name}.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return ""

    def __repr__(self) -> str:
        return f"LLMClient(provider={self.provider!r}, model={self.model!r})"
