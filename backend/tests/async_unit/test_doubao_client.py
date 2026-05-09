import base64
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.multimodal.doubao_client import DoubaoClient, get_doubao_client


class TestDoubaoClientInit:
    def test_uses_settings_by_default(self):
        client = DoubaoClient(api_key="sk-test", app_id="app-1")
        assert client.api_key == "sk-test"
        assert client.app_id == "app-1"

    def test_default_models(self):
        client = DoubaoClient(api_key="sk-test")
        assert client.stt_model == "doubao-voice-stt"
        assert client.tts_model == "doubao-voice-tts"
        assert client.vision_model == "doubao-vision-pro-32k"

    def test_auth_headers_without_app_id(self):
        client = DoubaoClient(api_key="sk-test")
        headers = client._headers
        assert headers["Authorization"] == "Bearer sk-test"
        assert "x-app-id" not in headers

    def test_auth_headers_with_app_id(self):
        client = DoubaoClient(api_key="sk-test", app_id="app-1")
        headers = client._headers
        assert headers["x-app-id"] == "app-1"


class TestDoubaoClientSTT:
    @pytest.mark.asyncio
    async def test_speech_to_text_sends_b64_audio(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"text": "患者头痛三天"}

        client = DoubaoClient(api_key="sk-test")
        audio = b"\x00\x01\x02\x03"

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            result = await client.speech_to_text(audio, audio_format="wav")

        assert result == "患者头痛三天"
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["model"] == "doubao-voice-stt"
        assert payload["format"] == "wav"
        assert payload["input"] == base64.b64encode(audio).decode("utf-8")
        assert call_args.kwargs["headers"]["Authorization"] == "Bearer sk-test"


class TestDoubaoClientTTS:
    @pytest.mark.asyncio
    async def test_text_to_speech_returns_audio_bytes(self):
        audio_data = b"mp3-audio-bytes"
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.content = audio_data

        client = DoubaoClient(api_key="sk-test")

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            result = await client.text_to_speech("你好", voice="zh_female_qingxin", speed=1.0)

        assert result == audio_data
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["input"] == "你好"
        assert payload["voice"] == "zh_female_qingxin"
        assert payload["response_format"] == "mp3"


class TestDoubaoClientOCR:
    @pytest.mark.asyncio
    async def test_ocr_image_sends_b64_image(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "血常规 白细胞: 5.2×10⁹/L"}}]
        }

        client = DoubaoClient(api_key="sk-test")
        img = b"\xff\xd8\xff\xe0"

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_resp
            mock_client_cls.return_value = mock_client

            result = await client.ocr_image(img)

        assert "血常规" in result
        call_args = mock_client.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["model"] == "doubao-vision-pro-32k"
        messages = payload["messages"]
        # Verify the image content is in the messages
        user_content = messages[0]["content"]
        assert user_content[0]["type"] == "image_url"
        assert "base64" in user_content[0]["image_url"]["url"]


class TestGetDoubaoClient:
    def test_returns_singleton(self):
        from app.core.multimodal import doubao_client as mod
        original = mod._doubao_client
        mod._doubao_client = None
        try:
            c1 = get_doubao_client()
            c2 = get_doubao_client()
            assert c1 is c2
        finally:
            mod._doubao_client = original
