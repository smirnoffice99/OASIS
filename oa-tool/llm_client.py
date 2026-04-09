"""
llm_client.py — LLM 호출 단일 창구
config.yaml의 provider/model 설정에 따라 Claude / OpenAI / Gemini를 투명하게 전환.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml


# WinRT 전용 이벤트 루프 — 항상 실행 중인 데몬 스레드에서 돌아간다.
# ThreadPoolExecutor 스레드마다 새 루프를 만들면 WinRT 완료 콜백이 전달되지 않아
# await가 영원히 대기(hang)하는 문제를 피하기 위해 루프를 하나로 유지한다.
_winrt_loop: "asyncio.AbstractEventLoop | None" = None
_winrt_loop_lock: "threading.Lock | None" = None


def _get_winrt_loop():
    """WinRT 전용 asyncio 루프를 반환한다. 최초 호출 시 데몬 스레드와 함께 생성한다."""
    import asyncio
    import threading
    global _winrt_loop, _winrt_loop_lock

    if _winrt_loop_lock is None:
        _winrt_loop_lock = threading.Lock()

    if _winrt_loop is not None and _winrt_loop.is_running():
        return _winrt_loop

    with _winrt_loop_lock:
        if _winrt_loop is not None and _winrt_loop.is_running():
            return _winrt_loop

        loop = asyncio.new_event_loop()

        def _run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        t = threading.Thread(target=_run_loop, daemon=True, name="winrt-ocr-loop")
        t.start()
        _winrt_loop = loop
        return loop


def _ocr_image_windows(image_bytes: bytes) -> str:
    """
    Windows WinRT OCR API를 Python 프로세스 내에서 직접 호출하여 텍스트를 추출한다.

    winrt 패키지(pywinrt)를 사용하므로 powershell.exe 자식 프로세스를 전혀 띄우지 않는다.
    → PyInstaller 번들 DLL이 자식 프로세스 PATH를 오염시키는 0xc0000142 문제가
      구조적으로 발생하지 않는다.

    WinRT 전용 데몬 루프(run_forever)에 코루틴을 제출하고 결과를 동기적으로 기다린다.
    루프가 항상 실행 중이므로 WinRT 완료 콜백이 정상적으로 전달된다.

    winrt 패키지가 없거나 Windows가 아니면 ImportError가 발생하며,
    호출부(ocr_image)에서 LLM Vision fallback으로 넘어간다.
    """
    import asyncio

    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import DataWriter, InMemoryRandomAccessStream

    async def _run() -> str:
        stream = InMemoryRandomAccessStream()
        writer = DataWriter(stream)
        writer.write_bytes(image_bytes)
        await writer.store_async()
        await writer.flush_async()
        stream.seek(0)

        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()

        best = ""
        for tag in ["ko", "en-US"]:
            lang = Language(tag)
            if OcrEngine.is_language_supported(lang):
                engine = OcrEngine.try_create_from_language(lang)
                if engine:
                    result = await engine.recognize_async(bitmap)
                    if len(result.text) > len(best):
                        best = result.text
        return best

    loop = _get_winrt_loop()
    future = asyncio.run_coroutine_threadsafe(_run(), loop)
    return future.result(timeout=60)



def _bundle_root() -> Path:
    """PyInstaller 번들이면 _MEIPASS, 아니면 이 파일의 디렉토리를 반환."""
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def _load_config() -> dict:
    config_path = _bundle_root() / "config.yaml"
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
        prompt_path = _bundle_root() / "prompts" / f"{prompt_name}.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return ""

    # ------------------------------------------------------------------
    # OCR — 이미지 기반 PDF 페이지 텍스트 추출
    # ------------------------------------------------------------------

    def ocr_image(self, image_bytes: bytes) -> str:
        """
        PNG 이미지 바이트에서 텍스트를 추출한다.
        이미지 기반 PDF 페이지 OCR에 사용된다.

        Windows OCR API를 우선 시도하고, 실패 시 LLM Vision으로 fallback한다.

        Args:
            image_bytes: PNG 형식의 이미지 바이트

        Returns:
            추출된 텍스트 (str)
        """
        try:
            text = _ocr_image_windows(image_bytes)
            if text.strip():
                return text
            raise ValueError("Windows OCR 결과가 비어 있음")
        except Exception as e:
            print(f"[정보] Windows OCR 실패 ({e}), LLM Vision으로 재시도합니다.")
            return self._ocr_image_llm(image_bytes)

    def _ocr_image_llm(self, image_bytes: bytes) -> str:
        """LLM Vision으로 OCR (Windows OCR fallback).

        한글 텍스트는 획이 가늘어 JPEG 손실 압축에 민감하므로 PNG를 그대로 사용한다.
        """
        if self.provider == "claude":
            return self._ocr_image_claude(image_bytes)
        elif self.provider == "openai":
            return self._ocr_image_openai(image_bytes)
        elif self.provider == "gemini":
            return self._ocr_image_gemini(image_bytes)
        else:
            raise ValueError(f"지원하지 않는 provider: {self.provider}")

    _OCR_PROMPT = (
        "이 PDF 페이지 이미지에서 텍스트를 원문 그대로 추출하라. "
        "레이아웃과 줄바꿈을 최대한 보존하되, 이미지 설명이나 주석 없이 텍스트만 출력하라."
    )

    def _ocr_image_claude(self, image_bytes: bytes) -> str:
        import base64
        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.b64encode(image_bytes).decode(),
                        },
                    },
                    {"type": "text", "text": self._OCR_PROMPT},
                ],
            }],
        )
        return response.content[0].text

    def _ocr_image_openai(self, image_bytes: bytes) -> str:
        import base64
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
                        },
                    },
                    {"type": "text", "text": self._OCR_PROMPT},
                ],
            }],
        )
        return response.choices[0].message.content

    def _ocr_image_gemini(self, image_bytes: bytes) -> str:
        import google.generativeai.protos as protos
        model = self._client.GenerativeModel(self.model)
        part = protos.Part(inline_data=protos.Blob(mime_type="image/png", data=image_bytes))
        response = model.generate_content([part, self._OCR_PROMPT])
        return response.text

    def __repr__(self) -> str:
        return f"LLMClient(provider={self.provider!r}, model={self.model!r})"
