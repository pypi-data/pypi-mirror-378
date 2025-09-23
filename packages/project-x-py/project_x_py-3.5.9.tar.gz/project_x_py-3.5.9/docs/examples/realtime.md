# Real-time Data Processing Examples

This page demonstrates how to work with real-time market data streams using the ProjectX Python SDK v3.5.7. Learn to handle WebSocket data, process multiple timeframes, and build real-time trading systems with the enhanced event system.

## Prerequisites

- ProjectX API credentials with real-time data access
- Active market during testing (futures trading hours)
- Understanding of async/await patterns
- Basic knowledge of market data structures

## 1. Basic Real-time Data Streaming

Start with simple real-time data consumption:

```python
#!/usr/bin/env python
"""
Basic real-time data streaming example.

This example demonstrates:
- Connecting to real-time data feeds
- Handling tick (quote) updates
- Processing new bar events
- Monitoring connection health
- Displaying streaming statistics
"""

import asyncio
from datetime import datetime

from project_x_py import EventType, TradingSuite
from project_x_py.event_bus import Event


async def main():
    """Main function to run real-time data streaming."""
    # Create suite with real-time capabilities
    suite = await TradingSuite.create(
        ["MNQ"],
        timeframes=["15sec", "1min"],
        initial_days=1,  # Minimal historical data
    )
    mnq_context = suite["MNQ"]

    print(f"Real-time streaming started for {mnq_context.symbol}")
    print(f"Connected: {suite.is_connected}")

    # Track statistics
    tick_count = 0
    bar_count = 0
    last_price = None

    async def on_tick(event: Event):
        """Handle tick updates."""
        nonlocal tick_count, last_price
        tick_data = event.data

        tick_count += 1
        last_price = tick_data.get("last") or last_price

        # Display every 10th tick to avoid spam
        if tick_count % 10 == 0:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Tick #{tick_count}: ${last_price:.2f}")

    async def on_new_bar(event: Event):
        """Handle new bar events."""
        nonlocal bar_count
        bar_count += 1

        timestamp = datetime.now().strftime("%H:%M:%S")

        # The event.data contains timeframe and nested data
        event_data = event.data
        timeframe = event_data.get("timeframe", "unknown")

        # Get the bar data directly from the event
        bar_data = event_data.get("data", {})

        if bar_data:
            print(f"[{timestamp}] New {timeframe} bar #{bar_count}:")

            # Access the bar data fields directly
            open_price = bar_data.get("open", 0)
            high_price = bar_data.get("high", 0)
            low_price = bar_data.get("low", 0)
            close_price = bar_data.get("close", 0)
            volume = bar_data.get("volume", 0)
            bar_timestamp = bar_data.get("timestamp", "")

            print(
                f"  OHLC: ${open_price:.2f} / ${high_price:.2f} / "
                f"${low_price:.2f} / ${close_price:.2f}"
            )
            print(f"  Volume: {volume}")
            print(f"  Timestamp: {bar_timestamp}")

    async def on_connection_status(event: Event):
        """Handle connection status changes."""
        status = event.data.get("connected", False)
        print(f"Connection Status Changed: {status}")
        if status:
            print("✅ Real-time feed connected")
        else:
            print("❌ Real-time feed disconnected")

    # Register event handlers
    await mnq_context.on(EventType.QUOTE_UPDATE, on_tick)
    await mnq_context.on(EventType.NEW_BAR, on_new_bar)
    await mnq_context.on(EventType.CONNECTED, on_connection_status)
    await mnq_context.on(EventType.DISCONNECTED, on_connection_status)

    print("Listening for real-time data... Press Ctrl+C to exit")

    try:
        while True:
            await asyncio.sleep(10)

            # Display periodic status
            current_price = await mnq_context.data.get_current_price()
            connection_health = await mnq_context.data.get_health_score()

            print(
                f"Status - Price: ${current_price:.2f} | "
                f"Ticks: {tick_count} | Bars: {bar_count} | "
                f"Health: {connection_health}"
            )

    except KeyboardInterrupt:
        print("\nShutting down real-time stream...")
    finally:
        # Ensure proper cleanup
        await suite.disconnect()
        print("Disconnected from real-time feeds")


if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Multi-Timeframe Data Synchronization

Handle multiple timeframes with proper synchronization:

```python
#!/usr/bin/env python
"""
Multi-timeframe real-time data synchronization
"""

import asyncio
from collections import defaultdict
from datetime import datetime

from project_x_py import EventType, TradingSuite
from project_x_py.indicators import RSI, SMA


class MultiTimeframeDataProcessor:
    def __init__(self, suite: TradingSuite):
        self.suite = suite
        self.timeframes = ["1min", "5min", "15min"]
        self.data_cache = defaultdict(list)
        self.last_analysis = defaultdict(dict)
        self.analysis_count = 0

    async def process_new_bar(self, event):
        """Process incoming bar data for all timeframes."""
        bar_data = event.data.get("data", event.data)
        timeframe = event.data.get("timeframe", "unknown")

        if timeframe not in self.timeframes:
            return

        # Store the bar
        self.data_cache[timeframe].append(bar_data)

        # Keep only recent bars (memory management)
        if len(self.data_cache[timeframe]) > 200:
            self.data_cache[timeframe] = self.data_cache[timeframe][-100:]

        print(
            f"New {timeframe} bar: ${bar_data['close']:.2f} @ {bar_data.get('timestamp')}"
        )

        # Perform analysis on this timeframe
        await self.analyze_timeframe(timeframe)

        # Check for multi-timeframe confluence
        if timeframe == "1min":  # Trigger confluence check on fastest timeframe
            await self.check_confluence()

    async def analyze_timeframe(self, timeframe: str):
        """Analyze a specific timeframe with technical indicators."""
        try:
            # Get fresh data from suite
            bars = await self.suite["MNQ"].data.get_data(timeframe)

            if bars is None:
                return

            if len(bars) < 50:  # Need enough data for indicators
                return

            # Calculate indicators
            bars = bars.pipe(SMA, period=20).pipe(RSI, period=14)

            current_price = bars["close"][-1]
            current_sma = bars["sma_20"][-1]
            current_rsi = bars["rsi_14"][-1]

            # Determine trend and momentum
            trend = "bullish" if current_price > current_sma else "bearish"
            momentum = (
                "strong"
                if (trend == "bullish" and current_rsi > 50)
                or (trend == "bearish" and current_rsi < 50)
                else "weak"
            )

            # Store analysis
            self.last_analysis[timeframe] = {
                "price": current_price,
                "sma_20": current_sma,
                "rsi": current_rsi,
                "trend": trend,
                "momentum": momentum,
                "timestamp": datetime.now(),
            }

            print(
                f"  {timeframe} Analysis - Trend: {trend}, RSI: {current_rsi:.1f}, Momentum: {momentum}"
            )

        except Exception as e:
            print(f"Error analyzing {timeframe}: {e}")

    async def check_confluence(self):
        """Check for confluence across all timeframes."""
        self.analysis_count += 1

        # Only check confluence every 5th analysis to avoid spam
        if self.analysis_count % 5 != 0:
            return

        if len(self.last_analysis) < len(self.timeframes):
            return

        # Count bullish/bearish signals
        bullish_count = sum(
            1
            for analysis in self.last_analysis.values()
            if analysis.get("trend") == "bullish"
        )
        bearish_count = sum(
            1
            for analysis in self.last_analysis.values()
            if analysis.get("trend") == "bearish"
        )

        # Check for strong confluence
        total_timeframes = len(self.last_analysis)

        if bullish_count >= total_timeframes * 0.8:  # 80% agreement
            print(
                f"\n= BULLISH CONFLUENCE DETECTED ({bullish_count}/{total_timeframes})"
            )
            await self.display_confluence_analysis("BULLISH")
        elif bearish_count >= total_timeframes * 0.8:
            print(
                f"\n=4 BEARISH CONFLUENCE DETECTED ({bearish_count}/{total_timeframes})"
            )
            await self.display_confluence_analysis("BEARISH")

    async def display_confluence_analysis(self, signal_type: str):
        """Display detailed confluence analysis."""
        print(f"{signal_type} CONFLUENCE ANALYSIS:")
        print("-" * 40)

        for tf, analysis in self.last_analysis.items():
            trend_emoji = "=" if analysis["trend"] == "bullish" else "="
            momentum_emoji = "=" if analysis["momentum"] == "strong" else "="

            print(
                f"  {tf:>5} {trend_emoji} {analysis['trend']:>8} | RSI: {analysis['rsi']:>5.1f} | {momentum_emoji} {analysis['momentum']}"
            )

        print("-" * 40)

        # Get current market data
        current_price = await self.suite["MNQ"].data.get_current_price()
        print(f"Current Price: ${current_price:.2f}")
        print()


async def main():
    # Create suite with multiple timeframes
    suite = await TradingSuite.create(
        "MNQ",
        timeframes=["1min", "5min", "15min"],
        initial_days=3,  # Enough data for indicators
    )

    processor = MultiTimeframeDataProcessor(suite)

    # Register event handler
    await suite.on(EventType.NEW_BAR, processor.process_new_bar)

    print("Multi-Timeframe Data Processor Active")
    print("Monitoring 1min, 5min, and 15min timeframes...")
    print("Press Ctrl+C to exit")

    try:
        while True:
            await asyncio.sleep(15)

            # Display periodic status
            print(f"\nStatus Update - {datetime.now().strftime('%H:%M:%S')}")
            for tf in processor.timeframes:
                cached_bars = len(processor.data_cache[tf])
                analysis = processor.last_analysis.get(tf, {})
                trend = analysis.get("trend", "unknown")
                rsi = analysis.get("rsi", 0)
                print(
                    f"  {tf}: {cached_bars} bars cached, {trend} trend, RSI: {rsi:.1f}"
                )

    except KeyboardInterrupt:
        print("\nShutting down multi-timeframe processor...")


if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Real-time Data Export and Visualization

Export real-time data and create visualizations:

```python
#!/usr/bin/env python
"""
Real-time data export with CSV logging and Plotly visualization
"""

import asyncio
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

from project_x_py import EventType, TradingSuite


class RealTimeDataExporter:
    def __init__(self, suite: TradingSuite, export_dir: str = "data_exports"):
        self.suite = suite
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)

        # Data storage
        self.tick_data = []
        self.bar_data = []
        self.trade_data = []

        # File handles
        self.csv_files = {}
        self.export_interval = 60  # Export every 60 seconds

    async def initialize_export_files(self):
        """Initialize CSV files for data export."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Bar data CSV
        bar_file = self.export_dir / f"bars_{timestamp}.csv"
        bar_csv = open(bar_file, "w", newline="")
        bar_writer = csv.writer(bar_csv)
        bar_writer.writerow(
            ["timestamp", "timeframe", "open", "high", "low", "close", "volume"]
        )
        self.csv_files["bars"] = {"file": bar_csv, "writer": bar_writer}

        print(f"Export files initialized in {self.export_dir}")

    async def process_bar(self, event):
        """Process and export bar data."""
        timestamp = datetime.now().isoformat()

        # Get the real data for the timeframe
        # Data from the event is from the new bar that was just started, so we need to get the previous bar
        real_data = await self.suite["MNQ"].data.get_data(
            event.data.get("timeframe", "unknown")
        )

        if real_data is None:
            return

        # Store in memory
        bar_record = {
            "timestamp": timestamp,
            "bar_timestamp": real_data["timestamp"][-2],
            "timeframe": event.data.get("timeframe", "unknown"),
            "open": real_data["open"][-2],
            "high": real_data["high"][-2],
            "low": real_data["low"][-2],
            "close": real_data["close"][-2],
            "volume": real_data["volume"][-2],
        }

        self.bar_data.append(bar_record)

        # Write to CSV
        if "bars" in self.csv_files:
            writer = self.csv_files["bars"]["writer"]
            writer.writerow(
                [
                    bar_record["bar_timestamp"] or timestamp,
                    bar_record["timeframe"],
                    bar_record["open"],
                    bar_record["high"],
                    bar_record["low"],
                    bar_record["close"],
                    bar_record["volume"],
                ]
            )
            self.csv_files["bars"]["file"].flush()

        print(f"Exported {bar_record['timeframe']} bar: ${bar_record['close']:.2f}")

    async def export_json_snapshot(self):
        """Export current data snapshot as JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        snapshot = {
            "export_timestamp": datetime.now().isoformat(),
            "data_summary": {
                "bar_count": len(self.bar_data),
            },
            "recent_data": {
                "bars": self.bar_data[-5:],  # Last 5 bars
            },
        }

        json_file = self.export_dir / f"snapshot_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(snapshot, f, indent=2)

        print(f"JSON snapshot exported: {json_file}")
        return json_file

    def close_files(self):
        """Close all open CSV files."""
        for file_info in self.csv_files.values():
            file_info["file"].close()
        print("Export files closed")


async def main():
    # Create suite for data export
    suite = await TradingSuite.create(
        "MNQ", timeframes=["15sec", "1min", "5min"], initial_days=1
    )

    mnq_context = suite["MNQ"]

    exporter = RealTimeDataExporter(suite)
    await exporter.initialize_export_files()

    # Event handlers
    await suite.on(EventType.NEW_BAR, exporter.process_bar)

    print("Real-time Data Exporter Active")
    print(f"Exporting to: {exporter.export_dir}")
    print("Streaming data...")

    try:
        export_timer = 0

        while True:
            await asyncio.sleep(10)
            export_timer += 10

            # Periodic status
            current_price = await mnq_context.data.get_current_price()
            if current_price is None:
                continue

            print(f"Price: ${current_price:.2f} | Bars: {len(exporter.bar_data)}")

            # Auto-export JSON snapshot every 5 minutes
            if export_timer >= 300:  # 5 minutes
                await exporter.export_json_snapshot()
                export_timer = 0

    except KeyboardInterrupt:
        print("\nShutting down data exporter...")

        # Final exports
        print("Creating final exports...")
        await exporter.export_json_snapshot()

        # Close files
        exporter.close_files()

        print("Data export complete!")


if __name__ == "__main__":
    asyncio.run(main())
```

## Key Real-time Data Concepts

### WebSocket Connection Management

- **Automatic Reconnection**: SDK handles connection drops automatically
- **Heartbeat Monitoring**: Built-in connection health checks
- **Circuit Breaker**: Prevents cascading failures during connectivity issues
- **Backpressure Handling**: Manages high-frequency data flows efficiently

### Data Processing Patterns

1. **Event-Driven Architecture**: Use events for decoupled real-time processing
2. **Buffering**: Store recent data for analysis and comparison
3. **Memory Management**: Implement sliding windows to prevent memory leaks
4. **Synchronization**: Handle multiple timeframes with proper timing

### Performance Optimization

- **Async Processing**: All data handling is fully asynchronous
- **Batch Operations**: Group related operations for better performance
- **Caching**: Cache frequently accessed data and calculations
- **Resource Limits**: Set appropriate limits for data storage

## Common Patterns

### Data Storage
```python
# Use deque for efficient FIFO operations
from collections import deque
tick_buffer = deque(maxlen=1000)

# Use defaultdict for organized multi-timeframe data
from collections import defaultdict
timeframe_data = defaultdict(list)
```

### Event Handling
```python
# Always use async event handlers
async def handle_event(event):
    try:
        # Process event data
        data = event.data
        # Your processing logic here
    except Exception as e:
        logger.error(f"Event handling error: {e}")

# Register handlers properly
await suite.on(EventType.NEW_BAR, handle_event)
```

### Error Recovery
```python
# Implement proper error handling
async def robust_data_processor(event):
    try:
        await process_data(event.data)
    except ConnectionError:
        logger.warning("Connection issue, retrying...")
        await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Processing error: {e}")
        # Continue processing other events
```

## Next Steps

For building production real-time systems:

1. **Implement Backtesting**: Test strategies on historical data first
2. **Add Monitoring**: Comprehensive logging and alerting
3. **Scale Architecture**: Handle multiple instruments and strategies
4. **Optimize Performance**: Profile and optimize critical paths
5. **Deploy Infrastructure**: Use proper deployment and monitoring tools

See also:
- [Advanced Trading Examples](advanced.md) for complex strategies
- [Backtesting Examples](backtesting.md) for historical testing
- [Basic Usage Examples](basic.md) for fundamentals
