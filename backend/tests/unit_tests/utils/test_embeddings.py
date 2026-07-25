from unittest.mock import MagicMock, patch

import pytest

from app.utils.embeddings import (
    _normalize_model_name,
    generate_embedding,
    generate_embedding_async,
    get_gemini_api_key,
)


class TestEmbeddings:
    @patch("app.utils.embeddings.settings")
    def test_get_gemini_api_key_empty(self, mock_settings):
        mock_settings.GEMINI_API_KEY = None

        result = get_gemini_api_key()

        assert result == ""

    @patch("app.utils.embeddings.settings")
    def test_get_gemini_api_key_string(self, mock_settings):
        mock_settings.GEMINI_API_KEY = "test-key-123"

        result = get_gemini_api_key()

        assert result == "test-key-123"

    @patch("app.utils.embeddings.settings")
    def test_get_gemini_api_key_json_list(self, mock_settings):
        mock_settings.GEMINI_API_KEY = '["key1", "key2"]'

        result = get_gemini_api_key()

        assert result in ["key1", "key2"]

    def test_normalize_model_name(self):
        assert _normalize_model_name("") == "models/gemini-embedding-001"
        assert _normalize_model_name("embedding-001") == "models/gemini-embedding-001"
        assert _normalize_model_name("models/custom-model") == "models/custom-model"
        assert _normalize_model_name("custom-model") == "models/custom-model"

    @patch("app.utils.embeddings.get_gemini_api_key", return_value="fake-key")
    @patch("app.utils.embeddings.httpx.post")
    def test_generate_embedding_success(self, mock_post, mock_get_key):
        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": {"values": [0.5] * 768}}
        mock_post.return_value = mock_response

        result = generate_embedding("Hello world")

        assert len(result) == 768
        assert result[0] == 0.5
        mock_post.assert_called_once()

    @patch("app.utils.embeddings.get_gemini_api_key", return_value="")
    def test_generate_embedding_no_api_key(self, mock_get_key):
        result = generate_embedding("Hello world")

        assert len(result) == 768
        assert all(v == 0.0 for v in result)

    @pytest.mark.asyncio
    @patch("app.utils.embeddings.get_gemini_api_key", return_value="fake-key")
    @patch("app.utils.embeddings.httpx.AsyncClient.post")
    async def test_generate_embedding_async_success(
        self, mock_post_async, mock_get_key
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": {"values": [0.1] * 768}}
        mock_post_async.return_value = mock_response

        result = await generate_embedding_async("Hello async")

        assert len(result) == 768
        assert result[0] == 0.1
        mock_post_async.assert_called_once()
