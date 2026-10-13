# Configuration

Bitongue's runtime behavior is described centrally by `BitongueConfig`, passed when the orchestrator is created:

```python
from bitongue.client import BitongueConfig

config = BitongueConfig(
    flowing_size=16,
    flowing_timeout=30,
    handle_timeout=5.0,
    handle_concurrency=1,
)
```

`BitongueConfig` is itself a msgspec struct (inheriting `BaseStruct`); all four fields are required.

## Field overview

| Field | Type | Unit | Meaning |
|-|-|-|-|
| `flowing_size` | `int` | messages | Capacity of the flowing window's bounded buffer; when full, `send()` waits, creating backpressure |
| `flowing_timeout` | `int \| None` | seconds | How long a message may live in the window; entries older than this are dropped at consumption time; `None` means never expire |
| `handle_timeout` | `float` | seconds | Maximum processing time allowed per message; timed-out messages are skipped (no result, consumption continues) |
| `handle_concurrency` | `int` | — | Handling concurrency; **in the current version this field is declared but not yet used by any scheduling logic — it is reserved**, and any value leaves behavior unchanged |

## Field behavior in detail

### `flowing_size`

The capacity maps to the maximum buffer length of the anyio memory stream. A message occupies one slot from `send()` until `result()` draws it out. Choosing a value:

- Too small: producers wait frequently under bursty traffic;
- Too large: bursts are buffered in full, raising memory usage and the expiry-removal load on the consumer side.

### `flowing_timeout`

The lifetime clock starts when the message **enters the buffer** (`send()`), so time spent waiting counts. Expired entries are removed **on the consumer side**: no result, no error, and completely transparent to the producer. Set it to `None` to disable this timeout layer and let messages wait indefinitely for consumption.

Division of labor between the two timeout layers: `flowing_timeout` governs "how long a message is worth processing at all", while `handle_timeout` governs "how long processing one message may take".

### `handle_timeout`

Implemented with an anyio cancel scope: a timeout **actually cancels** the execution inside the handler (it does not merely stop waiting), then skips that message and continues with the next one. Cleanup logic inside the handler (`try/finally`, `async with`, and so on) runs normally.

### `handle_concurrency`

A reserved field — see the table above; this page will be updated when a later version introduces concurrent handling.

## Lifecycle constraints

The configuration is read once when the `Bitongue` orchestrator is created, and used to build the internal flowing window at `start()`:

- Calling `send()` or `result()` before `start()` raises a `RuntimeError`;
- After `shutdown()` the window is closed; reuse the orchestrator by calling `start()` again.

## One timeout-combination example

```python
config = BitongueConfig(
    flowing_size=64,      # allow bursts of up to 64 queued messages
    flowing_timeout=10,   # messages queued longer than 10 seconds expire
    handle_timeout=2.0,   # at most 2 seconds per message, timed-out ones are skipped
    handle_concurrency=1,
)
```

The meaning of this combination: in the worst case, a message takes no more than about 12 seconds from entering the buffer to finishing processing; expired or timed-out messages never block the consumption of later ones.
