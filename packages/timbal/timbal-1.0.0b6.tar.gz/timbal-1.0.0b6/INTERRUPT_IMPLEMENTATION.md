# External Interrupt Implementation for Timbal Collectors

## Overview
This document outlines the design for implementing external interrupt capability for Timbal collectors, allowing graceful interruption of running processes while preserving partial results.

## Problem Statement
Currently, `bail()` only works from inside a running handler. We need a mechanism to interrupt Timbal collectors from external code (like audio_streamer.py) while retrieving whatever results have been produced up to the interruption point.

## Proposed Solution: Interrupt Checkpoints + Collector Awareness

### 1. RunContext Enhancement
**File**: `python/timbal/state/context.py`

Add interrupt mechanism to the RunContext class:

```python
import asyncio

class RunContext(BaseModel):
    # ... existing fields ...
    _interrupt_requested: asyncio.Event = PrivateAttr(default_factory=asyncio.Event)

    def request_interrupt(self):
        """Request interrupt for all active runnables in this context."""
        self._interrupt_requested.set()

    def is_interrupt_requested(self) -> bool:
        """Check if interrupt has been requested."""
        return self._interrupt_requested.is_set()
```

### 2. BaseCollector Enhancement
**File**: `python/timbal/collectors/base.py`

Add external interrupt support to collectors:

```python
class BaseCollector(ABC):
    def __init__(self, async_gen: AsyncGenerator[Any, None], **kwargs: Any):
        self._async_gen = async_gen
        self._collected = False
        self._interrupt_requested = asyncio.Event()  # NEW
        self._partial_result = None  # NEW

    def request_interrupt(self):
        """Request interrupt from outside the collector."""
        self._interrupt_requested.set()

    def is_interrupt_requested(self) -> bool:
        """Check if interrupt has been requested."""
        return self._interrupt_requested.is_set()

    async def __anext__(self):
        # Check for interrupt before processing next event
        if self._interrupt_requested.is_set():
            self._collected = True
            raise StopAsyncIteration

        try:
            event = await self._async_gen.__anext__()
            processed_event = self.process(event)
            if asyncio.iscoroutine(processed_event):
                processed_event = await processed_event
            return processed_event
        except StopAsyncIteration:
            self._collected = True
            raise
```

### 3. Runnable Interrupt Checkpoints
**File**: `python/timbal/core/runnable.py`

Add interrupt checkpoints at strategic locations in `Runnable.__call__()`:

#### Checkpoint 1: Before Handler Execution (~line 540)
```python
# Check for interrupt before starting handler
if run_context._interrupt_requested.is_set():
    output_event = OutputEvent(
        # ... standard fields ...
        status=RunStatus(code="interrupted", reason="external_interrupt"),
        output=None,
    )
    yield output_event
    return
```

#### Checkpoint 2: During Collector Creation (~line 563)
```python
if async_gen:
    collector = collector_type(async_gen=async_gen, start=handler_start)

    # Store collector reference for external access
    trace.collector = collector

    # Enhanced event processing with interrupt awareness
    try:
        async for event in collector:
            # Check for interrupt during collection
            if (run_context._interrupt_requested.is_set() or
                collector._interrupt_requested.is_set()):
                # Interrupt detected - preserve partial results
                output = collector.result()
                trace.status = RunStatus(
                    code="interrupted",
                    reason="external_interrupt",
                    message="Execution interrupted with partial results"
                )
                break
            yield emit_event(event)

        # Get final result if not interrupted
        if not (run_context._interrupt_requested.is_set() or
                collector._interrupt_requested.is_set()):
            output = collector.result()

    except StopAsyncIteration:
        # Normal completion or interrupt-induced completion
        output = collector.result()
```

#### Checkpoint 3: Enhanced Trace Storage
```python
# In Trace class (python/timbal/state/tracing/trace.py)
class Trace:
    # ... existing fields ...
    collector: BaseCollector | None = None  # NEW: Store collector reference
```

### 4. Usage Pattern

#### In audio_streamer.py:
```python
class SuperAgent(Agent):
    async def _handle_openai_transcribe_event(self, event: dict) -> None:
        if event_type == "conversation.item.input_audio_transcription.completed":
            # Start agent call and store collector reference
            collector = self(prompt=event["transcript"])
            self._agent_call_task = asyncio.create_task(collector.collect())
            self._current_collector = collector  # Store for interruption

    def interrupt_current_agent_call(self):
        """Interrupt the current agent call and get partial results."""
        if hasattr(self, '_current_collector') and self._current_collector:
            self._current_collector.request_interrupt()

    async def get_partial_results(self):
        """Get results from interrupted agent call."""
        if self._agent_call_task:
            return await self._agent_call_task  # Will contain partial results
```

#### External Interrupt Usage:
```python
# From outside the SuperAgent
superagent.interrupt_current_agent_call()
partial_result = await superagent.get_partial_results()
```

## Benefits

1. **Non-destructive**: Unlike task cancellation, partial results are preserved
2. **Multiple interrupt levels**: Can interrupt at context level or individual collector level
3. **Graceful degradation**: System continues to work normally when not interrupted
4. **Minimal invasive**: Uses existing event streaming architecture
5. **Real-time capable**: Suitable for audio streaming and other real-time scenarios

## Implementation Order

1. Enhance `RunContext` with interrupt mechanism
2. Add interrupt support to `BaseCollector`
3. Add checkpoints to `Runnable.__call__()`
4. Update `Trace` to store collector references
5. Modify `audio_streamer.py` to use interrupt mechanism
6. Add tests for interrupt scenarios

## Edge Cases & Considerations

- **Race conditions**: Interrupt requests during critical sections
- **Multiple interrupts**: Handling multiple interrupt requests
- **Cleanup**: Ensuring proper resource cleanup on interrupt
- **Nested collectors**: How interrupts propagate through nested execution
- **Result consistency**: Ensuring partial results are meaningful

## Testing Strategy

- Unit tests for interrupt mechanisms
- Integration tests with audio streaming
- Race condition testing
- Performance impact assessment
- Graceful degradation verification