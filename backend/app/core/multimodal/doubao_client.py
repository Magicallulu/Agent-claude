import base64
import logging
import time
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


class DoubaoClient:
    """火山引擎 ARK (方舟) 平台 Doubao API 客户端。

    Provides STT (speech-to-text), TTS (text-to-speech), and OCR (vision)
    via the ARK OpenAI-compatible endpoints.
    """

    def __init__(
        self,
        api_key: str = "",
        app_id: str = "",
        base_url: str = ARK_BASE_URL,
        stt_model: str = "doubao-voice-stt",
        tts_model: str = "doubao-voice-tts",
        vision_model: str = "doubao-vision-pro-32k",
    ):
        self.api_key = api_key or settings.doubao_api_key
        self.app_id = app_id or settings.doubao_app_id
        self.base_url = base_url
        self.stt_model = stt_model
        self.tts_model = tts_model
        self.vision_model = vision_model

    @property
    def _headers(self) -> dict:
        h = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.app_id:
            h["x-app-id"] = self.app_id
        return h

    async def speech_to_text(self, audio_bytes: bytes, audio_format: str = "wav") -> str:
        """将音频字节流转写为文本。

        Args:
            audio_bytes: 音频数据 (WAV, MP3, etc.)
            audio_format: 音频格式标识

        Returns:
            转写后的文本
        """
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        payload = {
            "model": self.stt_model,
            "input": b64,
            "format": audio_format,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/audio/transcriptions",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("text", "")

    async def text_to_speech(
        self, text: str, voice: str = "zh_female_qingxin", speed: float = 1.0
    ) -> bytes:
        """将文本合成为语音。

        Args:
            text: 要合成的文本
            voice: 音色标识
            speed: 语速倍率 (0.5-2.0)

        Returns:
            MP3 音频字节流
        """
        payload = {
            "model": self.tts_model,
            "input": text,
            "voice": voice,
            "speed": speed,
            "response_format": "mp3",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/audio/speech",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.content

    async def ocr_image(self, image_bytes: bytes) -> str:
        """对图片/PDF进行OCR提取文本。

        使用 Doubao 视觉模型识别报告中的文字内容。

        Args:
            image_bytes: 图片数据 (PNG, JPG) 或 PDF 首页截图

        Returns:
            提取的文本内容
        """
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/png;base64,{b64}"

        payload = {
            "model": self.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                        {
                            "type": "text",
                            "text": (
                                "请仔细识别并提取这份医学报告中的所有文字内容，"
                                "包括检查项目、检测结果、参考范围、异常标记等。"
                                "不要总结或解释，只输出原文内容。"
                            ),
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


_doubao_client: Optional[DoubaoClient] = None


def get_doubao_client() -> DoubaoClient:
    """获取 DoubaoClient 懒加载单例。

    首次调用时通过 settings 初始化，后续返回同一个实例。
    测试中可通过直接替换 _doubao_client 来注入 mock。
    """
    global _doubao_client
    if _doubao_client is None:
        _doubao_client = DoubaoClient()
    return _doubao_client
