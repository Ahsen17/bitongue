# Core concepts

Bitongue splits message handling into five independent, single-purpose concepts. This page explains each one's responsibility, how they cooperate, and their boundary behavior.

## Messages and entries (`BaseMessage` / `MessageEntry`)

`BaseMessage` is the message base class (itself a subclass of `BaseStruct`, the msgspec struct wrapper shared by all data structures). It currently defines the fields of a text message: `type` (fixed to `"text"`) and `text` (optional text content). The inherited `BaseStruct` provides `to_dict` / `from_dict` / `to_json` / `from_json`, so every message converts between dicts, JSON, and objects out of the box.

A message does not enter the buffer directly when sent; it is first wrapped into a `MessageEntry` that, besides the message itself, records `enter_time` (the moment of entry) and `timeout` (the lifetime in seconds) for the flowing window's expiry checks.

## The flowing window (`Flowing`)

`Flowing[T]` is the in-memory message flowing window — the holder of the bounded buffer:

- **Capacity**: `size` bounds the buffer (built on an anyio memory stream); when the window is full, the sender waits, which acts as natural backpressure.
- **Lifetime**: `timeout` is how many seconds a message may stay in the window; if unset, messages never expire.
- **Lifecycle**: `start()` creates the buffer and marks the window running; `shutdown()` closes it. Calling `draw()` (produce) or `flow()` (consume) while not running raises `FlowingNotInitializedError`.
- **Expiry is enforced on the consumer side**: `flow()` yields only unexpired messages; entries older than their lifetime are skipped without producing anything or raising.

You normally do not operate `Flowing` directly — use the `Bitongue` orchestrator instead.

## Filters (`BaseFilter`)

`BaseFilter[T]` is a Protocol (a structural interface); implementing it takes one async method:

```python
async def filter(self, message: T) -> bool:
```

Return `True` to release the message, `False` to reject it. Key points:

- A message proceeds to handling only when **every filter in the chain returns `True`**; a single `False` drops the message silently.
- The filter chain **does not short-circuit**: even if the first filter already rejected the message, the remaining filters still run. Filters should therefore be read-only, side-effect-free predicates.
- With no filters configured, every message passes.

## Handlers and results (`BaseHandler` / `BaseResult`)

`BaseHandler[T, R]` is the business-logic extension point, also a Protocol, with one async method:

```python
async def handle(self, message: T) -> R:
```

`R` must be a subclass of `BaseResult` — results are msgspec structs just like messages, with the same serialization abilities. Declaring the result type as a generic parameter (`BaseHandler[BaseMessage, UpperResult]`) gives you type checking across the whole path from send to result.

Any exception a handler raises is wrapped into `MessageHandleError` and propagates to the consumer; if handling exceeds the configured `handle_timeout`, that message is skipped (no result is produced, and consumption continues).

## The orchestrator (`Bitongue` / `BitongueConfig`)

`Bitongue[T, R]` assembles the parts above into one pipeline:

- **Construction**: takes a `BitongueConfig`, a handler (required), and an optional collection of filters;
- **Lifecycle**: `start()` creates and starts the flowing window internally; `shutdown()` closes it in reverse order;
- **Production side**: `send(message)` submits a message, wrapping and timing it internally;
- **Consumption side**: `result()` is an async generator that runs "expiry removal → filter chain → handler" in order and yields results one at a time.

Two boundary behaviors to note: calling `send()` or `result()` before `start()` raises a `RuntimeError`, and `result()` should be iterated by exactly one consumer at a time (the underlying buffer is a single-consumer memory stream).

For the full semantics of the configuration fields, see [Configuration](configuration.md); for a structural view of the whole path, see [Architecture and data flow](architecture.md).
