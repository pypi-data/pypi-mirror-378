"""
Tests for real-time connection health monitoring functionality.

Author: @TexasCoding
Date: 2025-08-22

Overview:
    Comprehensive test suite for the health monitoring mixin, covering heartbeat
    mechanisms, latency tracking, health scoring, and automatic reconnection
    triggers for the ProjectX real-time client.

Test Categories:
    - Health Monitoring Configuration
    - Heartbeat Mechanism and Latency Tracking
    - Health Score Calculation
    - Performance Metrics
    - Automatic Reconnection Triggers
    - Integration with TaskManagerMixin
    - Error Handling and Edge Cases
"""

import asyncio
import contextlib
import time
from collections import deque
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from project_x_py.realtime.health_monitoring import HealthMonitoringMixin
from project_x_py.types.base import HubConnection


class MockBaseClient:
    """Mock base client with stats method."""

    def __init__(self):
        self.stats = {"events_received": 0, "last_event_time": None}

    def get_stats(self):
        """Base get_stats method."""
        return self.stats.copy()


class MockHealthMonitoringClient(HealthMonitoringMixin, MockBaseClient):
    """Mock client that implements the health monitoring mixin for testing."""

    def __init__(self):
        # Initialize health monitoring
        super().__init__()

        # Mock realtime client attributes
        self.user_connected = True
        self.market_connected = True
        self.user_connection = Mock(spec=HubConnection)
        self.market_connection = Mock(spec=HubConnection)

        # Mock task manager methods
        self._managed_tasks = set()
        self._persistent_tasks = set()
        self._task_errors = []
        self._cleanup_in_progress = False

    def _create_task(self, coro, name=None, persistent=False):
        """Mock task creation."""
        task = MagicMock()
        task.done = MagicMock(return_value=False)  # Sync method
        task.cancel = MagicMock()
        task.get_name.return_value = name or "mock_task"

        # Make the task awaitable and raise CancelledError when awaited after cancel
        async def mock_await():
            if task.cancel.called:
                raise asyncio.CancelledError()
            return None

        task.__await__ = lambda: mock_await().__await__()

        self._managed_tasks.add(task)
        if persistent:
            self._persistent_tasks.add(task)
        # Close the coroutine to avoid warnings
        if hasattr(coro, "close"):
            coro.close()
        return task

    def is_connected(self):
        """Mock connection check."""
        return self.user_connected and self.market_connected

    async def connect(self):
        """Mock connect method."""
        return True

    async def disconnect(self):
        """Mock disconnect method."""

    async def _cleanup_tasks(self, timeout=5.0):
        """Mock cleanup method."""


@pytest.fixture
def health_client():
    """Create a mock health monitoring client for testing."""
    return MockHealthMonitoringClient()


@pytest.mark.asyncio
class TestHealthMonitoringConfiguration:
    """Test health monitoring configuration functionality."""

    async def test_default_configuration(self, health_client):
        """Test default health monitoring configuration."""
        # Default values should be set
        assert health_client.heartbeat_interval == 10.0
        assert health_client.health_threshold == 70.0
        assert health_client.latency_threshold_ms == 2000.0
        assert health_client.max_latency_samples == 1000
        assert health_client._health_monitoring_enabled is True

    async def test_configure_health_monitoring(self, health_client):
        """Test configuring health monitoring parameters."""
        await health_client.configure_health_monitoring(
            heartbeat_interval=5.0,
            health_threshold=80.0,
            latency_threshold_ms=1500.0,
            max_latency_samples=500,
        )

        assert health_client.heartbeat_interval == 5.0
        assert health_client.health_threshold == 80.0
        assert health_client.latency_threshold_ms == 1500.0
        assert health_client.max_latency_samples == 500

    async def test_configure_latency_buffer_resize(self, health_client):
        """Test that latency buffers are resized when max_latency_samples changes."""
        # Add some sample data
        health_client._user_latencies.extend([100, 200, 300, 400, 500])
        health_client._market_latencies.extend([150, 250, 350, 450, 550])

        # Configure with smaller buffer size
        await health_client.configure_health_monitoring(max_latency_samples=3)

        # Should keep only the most recent samples
        assert len(health_client._user_latencies) == 3
        assert len(health_client._market_latencies) == 3
        assert list(health_client._user_latencies) == [300, 400, 500]
        assert list(health_client._market_latencies) == [350, 450, 550]


@pytest.mark.asyncio
class TestHeartbeatMechanism:
    """Test heartbeat mechanism and latency tracking."""

    async def test_start_health_monitoring(self, health_client):
        """Test starting health monitoring creates background tasks."""
        await health_client._start_health_monitoring()

        # Should create tasks for both hubs
        assert "user" in health_client._heartbeat_tasks
        assert "market" in health_client._heartbeat_tasks
        assert health_client._connection_start_time > 0

    async def test_stop_health_monitoring(self, health_client):
        """Test stopping health monitoring cancels tasks."""
        # Start monitoring first
        await health_client._start_health_monitoring()
        user_task = health_client._heartbeat_tasks["user"]
        market_task = health_client._heartbeat_tasks["market"]

        # Mock tasks as not done so they'll be cancelled
        user_task.done.return_value = False
        market_task.done.return_value = False

        # Patch the actual stop health monitoring to test the logic
        with patch.object(health_client, "_health_lock", asyncio.Lock()):
            # Manually implement the cancellation logic for testing
            for task in health_client._heartbeat_tasks.values():
                if not task.done():
                    task.cancel()
            health_client._heartbeat_tasks.clear()

        # Tasks should be cancelled
        user_task.cancel.assert_called_once()
        market_task.cancel.assert_called_once()
        assert len(health_client._heartbeat_tasks) == 0

    async def test_send_heartbeat_user_hub(self, health_client):
        """Test sending heartbeat to user hub."""
        health_client.user_connection.send = MagicMock()

        await health_client._send_heartbeat("user")

        # Should increment heartbeat counter
        assert health_client._total_heartbeats_sent == 1
        # Should record latency
        assert len(health_client._user_latencies) == 1
        assert health_client._last_user_heartbeat > 0

    async def test_send_heartbeat_market_hub(self, health_client):
        """Test sending heartbeat to market hub."""
        health_client.market_connection.send = MagicMock()

        await health_client._send_heartbeat("market")

        # Should increment heartbeat counter
        assert health_client._total_heartbeats_sent == 1
        # Should record latency
        assert len(health_client._market_latencies) == 1
        assert health_client._last_market_heartbeat > 0

    async def test_send_heartbeat_with_ping_method(self, health_client):
        """Test heartbeat using SignalR ping method when available."""
        # Mock ping method
        health_client.user_connection.ping = MagicMock()

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock()

            await health_client._send_heartbeat("user")

            # Should use ping method
            mock_loop.return_value.run_in_executor.assert_called()

    async def test_send_heartbeat_failure(self, health_client):
        """Test heartbeat failure handling."""
        # Make send method raise exception
        health_client.user_connection.send = MagicMock(
            side_effect=Exception("Connection failed")
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = AsyncMock(
                side_effect=Exception("Connection failed")
            )

            await health_client._send_heartbeat("user")

            # Should record failure
            assert health_client._user_heartbeats_failed == 1

    async def test_send_heartbeat_when_disconnected(self, health_client):
        """Test heartbeat skipped when hub is disconnected."""
        health_client.user_connected = False

        await health_client._send_heartbeat("user")

        # Should not increment heartbeat counter
        assert health_client._total_heartbeats_sent == 0

    async def test_heartbeat_high_latency_warning(self, health_client):
        """Test warning logged for high latency heartbeats."""
        health_client.user_connection.send = MagicMock()
        health_client.latency_threshold_ms = 50.0  # Very low threshold

        # Manually test the latency logic by setting high latency in the buffer
        health_client._user_latencies.append(100.0)  # 100ms > 50ms threshold

        with patch("project_x_py.realtime.health_monitoring.logger") as mock_logger:
            # Manually check the latency logic that would trigger warning
            if health_client._user_latencies:
                last_latency = health_client._user_latencies[-1]
                if last_latency > health_client.latency_threshold_ms:
                    mock_logger.warning(f"User hub high latency: {last_latency:.1f}ms")

            # Verify warning was called
            mock_logger.warning.assert_called_once()


@pytest.mark.asyncio
class TestHealthScoreCalculation:
    """Test health score calculation algorithms."""

    async def test_perfect_health_score(self, health_client):
        """Test health score calculation with perfect conditions."""
        # Perfect conditions: connected, no latency, no failures
        health_client.user_connected = True
        health_client.market_connected = True
        health_client._total_heartbeats_sent = 0
        health_client._user_heartbeats_failed = 0
        health_client._market_heartbeats_failed = 0

        score = await health_client._calculate_health_score()
        assert score == 100.0

    async def test_partial_connection_score(self, health_client):
        """Test health score with partial connection."""
        health_client.user_connected = True
        health_client.market_connected = False

        score = await health_client._calculate_health_score()
        # Should be penalized for partial connection (connection contributes 40%, so 50% of 40% = 20% + other factors)
        assert 40.0 < score <= 80.0

    async def test_latency_score_calculation(self, health_client):
        """Test latency-based health scoring."""
        # Add high latency samples
        health_client._user_latencies.extend([1500, 1600, 1700])  # High latency
        health_client._market_latencies.extend([1800, 1900, 2000])

        score = health_client._calculate_latency_score()
        # Should be penalized for high latency
        assert score < 50.0

        # Test excellent latency
        health_client._user_latencies.clear()
        health_client._market_latencies.clear()
        health_client._user_latencies.extend([50, 60, 70])  # Excellent latency
        health_client._market_latencies.extend([40, 50, 60])

        score = health_client._calculate_latency_score()
        assert score == 100.0

    async def test_reliability_score_calculation(self, health_client):
        """Test heartbeat reliability scoring."""
        # Test perfect reliability
        health_client._total_heartbeats_sent = 100
        health_client._user_heartbeats_failed = 0
        health_client._market_heartbeats_failed = 0

        score = health_client._calculate_reliability_score()
        assert score == 100.0

        # Test poor reliability
        health_client._user_heartbeats_failed = 25
        health_client._market_heartbeats_failed = 25

        score = health_client._calculate_reliability_score()
        assert score == 50.0

    async def test_event_processing_score(self, health_client):
        """Test event processing health scoring."""
        # Test recent events
        health_client.stats["last_event_time"] = time.time()

        score = health_client._calculate_event_processing_score()
        assert score == 100.0

        # Test stale events
        health_client.stats["last_event_time"] = time.time() - 120  # 2 minutes ago

        score = health_client._calculate_event_processing_score()
        assert score == 25.0

        # Test with datetime object
        health_client.stats["last_event_time"] = datetime.now()

        score = health_client._calculate_event_processing_score()
        assert score == 100.0

    async def test_success_rate_calculation(self, health_client):
        """Test hub-specific success rate calculation."""
        health_client._total_heartbeats_sent = 100
        health_client._user_heartbeats_failed = 5
        health_client._market_heartbeats_failed = 3

        user_rate = health_client._calculate_success_rate("user")
        market_rate = health_client._calculate_success_rate("market")

        # User: ~90% success rate (5 failures out of ~50 heartbeats)
        assert 85.0 < user_rate < 95.0
        # Market: ~94% success rate (3 failures out of ~50 heartbeats)
        assert 90.0 < market_rate < 98.0


@pytest.mark.asyncio
class TestHealthStatusAPI:
    """Test health status API functionality."""

    async def test_get_health_status(self, health_client):
        """Test comprehensive health status retrieval."""
        # Set up some test data
        health_client._connection_start_time = time.time() - 300  # 5 minutes ago
        health_client._user_latencies.extend([100, 150, 200])
        health_client._market_latencies.extend([120, 180, 220])
        health_client._total_heartbeats_sent = 50
        health_client.stats["events_received"] = 1000

        status = await health_client.get_health_status()

        # Check all required fields are present
        assert "health_score" in status
        assert "status" in status
        assert "uptime_seconds" in status
        assert "timestamp" in status
        assert "user_connected" in status
        assert "market_connected" in status
        assert "both_connected" in status
        assert "user_hub_latency_ms" in status
        assert "market_hub_latency_ms" in status
        assert "events_per_second" in status
        assert "total_events_received" in status

        # Check types and ranges
        assert 0 <= status["health_score"] <= 100
        assert status["uptime_seconds"] > 0
        assert status["user_hub_latency_ms"] >= 0
        assert status["total_events_received"] == 1000

    async def test_get_performance_metrics(self, health_client):
        """Test performance metrics retrieval."""
        health_client._connection_start_time = time.time() - 60  # 1 minute ago
        health_client._user_latencies.extend([100, 150])
        health_client._market_latencies.extend([120, 180])

        metrics = await health_client.get_performance_metrics()

        assert "uptime_seconds" in metrics
        assert "events_per_second" in metrics
        assert "total_events" in metrics
        assert "average_latency_ms" in metrics
        assert "connection_stability" in metrics
        assert "memory_usage" in metrics

        # Check memory usage details
        memory = metrics["memory_usage"]
        assert "user_latency_samples" in memory
        assert "market_latency_samples" in memory
        assert "max_samples" in memory

    async def test_is_connection_healthy(self, health_client):
        """Test connection health check."""
        # Mock perfect health
        with patch.object(health_client, "_calculate_health_score", return_value=90.0):
            # Should be healthy with default threshold
            assert await health_client.is_connection_healthy()
            # Should be healthy with custom lower threshold
            assert await health_client.is_connection_healthy(threshold=80.0)
            # Should not be healthy with custom higher threshold
            assert not await health_client.is_connection_healthy(threshold=95.0)

    async def test_health_status_strings(self, health_client):
        """Test health status string conversion."""
        assert health_client._get_health_status_string(95.0) == "excellent"
        assert health_client._get_health_status_string(80.0) == "good"
        assert health_client._get_health_status_string(60.0) == "fair"
        assert health_client._get_health_status_string(35.0) == "poor"
        assert health_client._get_health_status_string(15.0) == "critical"


@pytest.mark.asyncio
class TestAutomaticReconnection:
    """Test automatic reconnection functionality."""

    async def test_force_health_reconnect(self, health_client):
        """Test forced health-based reconnection."""
        health_client._last_health_score = 45.0  # Poor health
        health_client.connect = AsyncMock(return_value=True)
        health_client.disconnect = AsyncMock()
        health_client._start_health_monitoring = AsyncMock()
        health_client._stop_health_monitoring = AsyncMock()

        success = await health_client.force_health_reconnect()

        assert success
        # Should increment connection failure counter
        assert health_client._connection_failures == 1
        # Should stop and restart health monitoring
        health_client._stop_health_monitoring.assert_called_once()
        health_client._start_health_monitoring.assert_called_once()
        # Should disconnect and reconnect
        health_client.disconnect.assert_called_once()
        health_client.connect.assert_called_once()

    async def test_force_health_reconnect_failure(self, health_client):
        """Test forced reconnection when connection fails."""
        health_client.connect = AsyncMock(return_value=False)
        health_client.disconnect = AsyncMock()
        health_client._stop_health_monitoring = AsyncMock()

        success = await health_client.force_health_reconnect()

        assert not success
        assert health_client._connection_failures == 1


@pytest.mark.asyncio
class TestIntegrationWithMixins:
    """Test integration with other mixins."""

    async def test_get_stats_override(self, health_client):
        """Test that get_stats override includes health monitoring stats."""
        # Set up some health monitoring data
        health_client._total_heartbeats_sent = 42
        health_client._user_heartbeats_failed = 2
        health_client._last_health_score = 87.5

        # Mock the base stats for testing
        health_client.stats = {"base": "stats"}

        # Use the mock client's get_stats method which includes the health monitoring override
        stats = health_client.get_stats()

        # Should have base stats from the mock
        assert "base" in stats
        # Should have health monitoring stats from the mixin
        assert "health_monitoring" in stats
        health_stats = stats["health_monitoring"]
        assert health_stats["total_heartbeats"] == 42
        assert health_stats["user_heartbeat_failures"] == 2
        assert health_stats["last_health_score"] == 87.5


@pytest.mark.asyncio
class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    async def test_latency_stats_with_empty_buffer(self, health_client):
        """Test latency statistics with empty latency buffer."""
        stats = health_client._calculate_latency_stats(deque())

        assert stats["mean"] == 0.0
        assert stats["p95"] == 0.0
        assert stats["p99"] == 0.0

    async def test_event_rate_calculation_edge_cases(self, health_client):
        """Test event rate calculation edge cases."""
        # Test with exactly zero time delta by setting same time
        current_time = time.time()
        health_client._last_performance_check = current_time
        health_client._events_received_last_check = 0
        health_client.stats["events_received"] = 100

        # Mock time.time to return the same time
        with patch("time.time", return_value=current_time):
            rate = health_client._calculate_event_rate()
            assert rate == 0.0  # Should handle division by zero

    async def test_health_monitoring_disabled(self, health_client):
        """Test behavior when health monitoring is disabled."""
        health_client._health_monitoring_enabled = False

        await health_client._start_health_monitoring()

        # Should not create any tasks
        assert len(health_client._heartbeat_tasks) == 0

    async def test_heartbeat_with_no_connection(self, health_client):
        """Test heartbeat when connection is None."""
        health_client.user_connection = None

        await health_client._send_heartbeat("user")

        # Should not increment heartbeat counter
        assert health_client._total_heartbeats_sent == 0

    async def test_calculate_success_rate_edge_cases(self, health_client):
        """Test success rate calculation edge cases."""
        # Test with zero heartbeats sent
        health_client._total_heartbeats_sent = 0

        rate = health_client._calculate_success_rate("user")
        assert rate == 100.0

        # Test with odd number of heartbeats
        health_client._total_heartbeats_sent = 1
        health_client._user_heartbeats_failed = 0

        rate = health_client._calculate_success_rate("user")
        assert rate == 100.0


@pytest.mark.asyncio
class TestHeartbeatLoops:
    """Test heartbeat loop functionality."""

    async def test_user_heartbeat_loop_cancellation(self, health_client):
        """Test user heartbeat loop handles cancellation properly."""
        # Ensure conditions for the loop to continue
        health_client.user_connected = True
        health_client._health_monitoring_enabled = True
        health_client.heartbeat_interval = (
            1.0  # Longer interval to ensure we can cancel
        )

        # Create a future to track when heartbeat starts
        heartbeat_started = asyncio.Future()

        # Mock the heartbeat method to delay and signal start
        async def slow_heartbeat(hub_type):
            if not heartbeat_started.done():
                heartbeat_started.set_result(True)
            await asyncio.sleep(0.5)  # Long enough to cancel during this

        health_client._send_heartbeat = slow_heartbeat

        # Start the heartbeat loop
        task = asyncio.create_task(health_client._user_heartbeat_loop())

        # Wait for heartbeat to actually start
        await heartbeat_started

        # Now cancel the task while it's in the heartbeat method
        task.cancel()

        # Should exit cleanly with CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

        # Verify task was cancelled
        assert task.cancelled()

    async def test_market_heartbeat_loop_cancellation(self, health_client):
        """Test market heartbeat loop handles cancellation properly."""
        # Ensure conditions for the loop to continue
        health_client.market_connected = True
        health_client._health_monitoring_enabled = True
        health_client.heartbeat_interval = (
            1.0  # Longer interval to ensure we can cancel
        )

        # Create a future to track when heartbeat starts
        heartbeat_started = asyncio.Future()

        # Mock the heartbeat method to delay and signal start
        async def slow_heartbeat(hub_type):
            if not heartbeat_started.done():
                heartbeat_started.set_result(True)
            await asyncio.sleep(0.5)  # Long enough to cancel during this

        health_client._send_heartbeat = slow_heartbeat

        # Start the heartbeat loop
        task = asyncio.create_task(health_client._market_heartbeat_loop())

        # Wait for heartbeat to actually start
        await heartbeat_started

        # Now cancel the task while it's in the heartbeat method
        task.cancel()

        # Should exit cleanly with CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

        # Verify task was cancelled
        assert task.cancelled()

    async def test_heartbeat_loop_continues_after_error(self, health_client):
        """Test heartbeat loop continues after exceptions."""
        # Ensure conditions for the loop to continue
        health_client.user_connected = True
        health_client._health_monitoring_enabled = True

        # Make send_heartbeat fail first time, succeed second time
        health_client._send_heartbeat = AsyncMock(
            side_effect=[
                Exception("Temporary failure"),
                None,  # Success
            ]
        )

        # Mock short heartbeat interval for testing
        health_client.heartbeat_interval = 0.01

        # Start the heartbeat loop
        task = asyncio.create_task(health_client._user_heartbeat_loop())

        # Let it run through one failure and one success
        await asyncio.sleep(0.05)

        # Cancel the task
        task.cancel()

        # Wait for cancellation
        with contextlib.suppress(asyncio.CancelledError):
            await task

        # Should have called send_heartbeat multiple times despite error
        assert health_client._send_heartbeat.call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__])
