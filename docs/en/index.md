# Bitongue

An async message flowing library built on [anyio](https://anyio.readthedocs.io/) and [msgspec](https://jcristharif.com/msgspec/).

Bitongue splits "receiving, filtering, and processing" into three independently evolving stages: producers put messages into an in-memory flowing window that owns buffering and lifetime control; a filter chain decides which messages pass; a handler carries out the business logic and produces typed results.

## Features

- **In-memory flowing window**: a bounded buffer on anyio memory streams with a configurable capacity and message lifetime; expired messages are dropped automatically at consumption time — see [Quick start](guide/quickstart.md)
- **Filter-chain admission**: a message is released only when every filter accepts it; rejected messages are dropped silently — semantics in [Core concepts](guide/concepts.md)
- **Handler extension point**: implement one async `handle(message) -> result` method to plug in your business; a handling timeout only affects the current message, never blocking the rest
- **Two layers of timeout protection**: window lifetime plus per-message handling timeout — details in [Configuration](guide/configuration.md)
- **Type safe**: messages and results are msgspec structs with built-in dict / JSON serialization, and generic parameters flow through from send to result
- **Minimal dependencies**: only anyio and msgspec at runtime

Requires Python ≥ 3.12.

```{toctree}
:hidden:

guide/quickstart
guide/concepts
guide/architecture
guide/configuration
api
```
