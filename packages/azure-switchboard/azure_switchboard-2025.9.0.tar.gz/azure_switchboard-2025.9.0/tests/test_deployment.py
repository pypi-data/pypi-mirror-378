import asyncio
from unittest.mock import patch

import pytest
import respx
from httpx import Response, TimeoutException

from azure_switchboard import Deployment, DeploymentError

from .conftest import (
    COMPLETION_PARAMS,
    COMPLETION_RESPONSE,
    COMPLETION_RESPONSE_JSON,
    COMPLETION_STREAM_CHUNKS,
    chat_completion_mock,
    collect_chunks,
)


class TestDeployment:
    """Deployment functionality tests."""

    async def test_init(self, deployment: Deployment):
        """Test initialization of Deployment."""
        assert deployment is not None
        assert deployment.client is not None
        assert deployment.models is not None
        assert deployment.model("gpt-4o-mini") is not None
        assert deployment.model("gpt-4o") is not None

    @pytest.mark.mock_models("gpt-4o-mini")
    async def test_completion(
        self, mock_client: respx.MockRouter, deployment: Deployment
    ):
        """Test basic chat completion functionality."""

        deployment.client.max_retries = 0

        response = await deployment.create(**COMPLETION_PARAMS)
        assert mock_client.routes["gpt-4o-mini"].call_count == 1
        assert response == COMPLETION_RESPONSE

        # Check token usage tracking
        model = deployment.model("gpt-4o-mini")
        usage = model.stats()
        assert usage.tpm.startswith(str(COMPLETION_RESPONSE.usage.total_tokens))  # pyright: ignore[reportOptionalMemberAccess]
        assert usage.rpm.startswith("1")

        # Test exception handling
        mock_client.routes["gpt-4o-mini"].side_effect = Exception("test")
        with pytest.raises(DeploymentError):  # (openai.APIConnectionError):
            await deployment.create(**COMPLETION_PARAMS)
        assert mock_client.routes["gpt-4o-mini"].call_count == 2

        # account for preflight estimate
        usage = model.stats()
        assert "23/" in usage.tpm
        assert "2/" in usage.rpm

    async def test_streaming(self, deployment: Deployment):
        """Test streaming functionality.

        It's annoying to try to mock HTTP streaming responses so we cheat
        a little bit with an AsyncMock.
        """

        deployment.client.max_retries = 0

        with patch.object(
            deployment.client.chat.completions,
            "create",
            side_effect=chat_completion_mock(),
        ) as mock:
            stream = await deployment.create(stream=True, **COMPLETION_PARAMS)
            mock.assert_called_once()

            # verify basic behavior
            received_chunks, content = await collect_chunks(stream)
            assert len(received_chunks) == len(COMPLETION_STREAM_CHUNKS)
            assert content == "Hello, world!"

            # Verify token usage tracking
            usage = deployment.model("gpt-4o-mini").stats()
            assert "20/" in usage.tpm
            assert "1/" in usage.rpm

        # verify exception handling
        with patch.object(
            deployment.client.chat.completions,
            "create",
            side_effect=Exception("test"),
        ) as mock:
            with pytest.raises(DeploymentError):
                stream = await deployment.create(stream=True, **COMPLETION_PARAMS)
                async for _ in stream:
                    pass
            mock.assert_called_once()

            usage = deployment.model("gpt-4o-mini").stats()
            assert "23/" in usage.tpm
            assert "2/" in usage.rpm

        # Test midstream exception handling
        with patch.object(
            deployment.client.chat.completions,
            "create",
            side_effect=chat_completion_mock(),
        ) as mock:
            stream = await deployment.create(stream=True, **COMPLETION_PARAMS)

            with patch.object(
                stream._self_model,  # type: ignore[reportAttributeAccessIssue]
                "spend_tokens",
                side_effect=Exception("asyncstream error"),
            ):
                with pytest.raises(DeploymentError, match="Error in wrapped stream"):
                    await collect_chunks(stream)
                assert mock.call_count == 1
                assert not deployment.model("gpt-4o-mini").is_healthy()

            deployment.model("gpt-4o-mini").mark_up()
            assert deployment.model("gpt-4o-mini").is_healthy()

    async def test_mark_down(self, deployment: Deployment):
        """Test model-level cooldown functionality."""

        model = deployment.model("gpt-4o-mini")

        model.mark_down()
        assert not model.is_healthy()

        model.mark_up()
        assert model.is_healthy()

    async def test_valid_model(self, deployment: Deployment):
        """Test that an invalid model raises an error."""

        with pytest.raises(DeploymentError, match="gpt-fake not configured"):
            await deployment.create(model="gpt-fake", messages=[])

    async def test_usage(self, deployment: Deployment):
        """Test client-level counters"""

        # Reset and verify initial state
        for model in deployment.models.values():
            assert "tpm='0" in str(model)

        # Test client-level usage
        model = deployment.model("gpt-4o-mini")
        usage = model.stats()
        assert usage.tpm == f"0/{model.tpm_limit}"
        assert usage.rpm == f"0/{model.rpm_limit}"

        # Set and verify values
        model.spend_tokens(100)
        model.spend_request(5)
        usage = model.stats()
        assert usage.tpm == f"100/{model.tpm_limit}"
        assert usage.rpm == f"5/{model.rpm_limit}"

        # Reset and verify again
        deployment.reset_usage()
        usage = model.stats()
        assert usage.tpm == f"0/{model.tpm_limit}"
        assert usage.rpm == f"0/{model.rpm_limit}"
        assert model.last_reset > 0

    async def test_utilization(self, deployment: Deployment):
        """Test utilization calculation."""

        model = deployment.model("gpt-4o-mini")

        # Check initial utilization (nonzero due to random splay)
        initial_util = model.util
        assert 0 <= initial_util < 0.02

        # Test token-based utilization
        model.spend_tokens(5000)  # 50% of TPM limit
        util_with_tokens = model.util
        assert 0.5 <= util_with_tokens < 0.52

        # Test request-based utilization
        model.reset_usage()
        model.spend_request(30)  # 50% of RPM limit
        util_with_requests = model.util
        assert 0.5 <= util_with_requests < 0.52

        # Test combined utilization (should take max of the two)
        model.reset_usage()
        model.spend_tokens(6000)  # 60% of TPM
        model.spend_request(30)  # 50% of RPM
        util_with_both = model.util
        assert 0.6 <= util_with_both < 0.62

        # Test unhealthy client
        model.mark_down()
        assert model.util == 1

    @pytest.mark.mock_models("gpt-4o-mini", "gpt-4o")
    async def test_multiple_models(
        self, mock_client: respx.MockRouter, deployment: Deployment
    ):
        """Test that multiple models are handled correctly."""

        gpt4o = deployment.models["gpt-4o"]
        gpt4o_mini = deployment.models["gpt-4o-mini"]

        assert gpt4o is not None
        assert gpt4o_mini is not None

        _ = await deployment.create(
            model="gpt-4o", messages=COMPLETION_PARAMS["messages"]
        )
        assert mock_client.routes["gpt-4o"].call_count == 1
        assert gpt4o.rpm_usage == 1
        assert gpt4o.tpm_usage > 0
        assert gpt4o_mini.tpm_usage == 0
        assert gpt4o_mini.rpm_usage == 0

        _ = await deployment.create(**COMPLETION_PARAMS)
        assert mock_client.routes["gpt-4o-mini"].call_count == 1

        assert gpt4o.rpm_usage == 1
        assert gpt4o.tpm_usage > 0
        assert gpt4o_mini.tpm_usage > 0
        assert gpt4o_mini.rpm_usage == 1

    @pytest.mark.mock_models("gpt-4o-mini")
    async def test_concurrency(
        self, mock_client: respx.MockRouter, deployment: Deployment
    ):
        """Test handling of multiple concurrent requests."""

        # Create and run concurrent requests
        num_requests = 10
        tasks = [deployment.create(**COMPLETION_PARAMS) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)

        # Verify results
        model = deployment.models["gpt-4o-mini"]
        assert len(responses) == num_requests
        assert all(r == COMPLETION_RESPONSE for r in responses)
        assert mock_client.routes["gpt-4o-mini"].call_count == num_requests
        usage = model.stats()
        assert usage.tpm == f"{20 * num_requests}/10000"
        assert usage.rpm == f"{num_requests}/60"

    @pytest.mark.mock_models("gpt-4o-mini")
    async def test_timeout_retry(
        self, mock_client: respx.MockRouter, deployment: Deployment
    ):
        """Test timeout retry behavior."""

        # Test successful retry after timeouts
        expected_response = Response(status_code=200, json=COMPLETION_RESPONSE_JSON)
        mock_client.routes["gpt-4o-mini"].side_effect = [
            TimeoutException("Timeout 1"),
            TimeoutException("Timeout 2"),
            expected_response,
        ]
        response = await deployment.create(**COMPLETION_PARAMS)
        assert response == COMPLETION_RESPONSE
        assert mock_client.routes["gpt-4o-mini"].call_count == 3

        # Test failure after max retries
        mock_client.routes["gpt-4o-mini"].reset()
        mock_client.routes["gpt-4o-mini"].side_effect = [
            TimeoutException("Timeout 1"),
            TimeoutException("Timeout 2"),
            TimeoutException("Timeout 3"),
        ]

        with pytest.raises(DeploymentError):  # (openai.APITimeoutError):
            await deployment.create(**COMPLETION_PARAMS)
        assert mock_client.routes["gpt-4o-mini"].call_count == 3
        assert not deployment.is_healthy("gpt-4o-mini")

    async def test_invalid_model(self, deployment: Deployment):
        """Test that an invalid or unconfigured model is not eligible on a deployment."""

        assert not deployment.is_healthy("invalid-model")
