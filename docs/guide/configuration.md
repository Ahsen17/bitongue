# 配置说明

Bitongue 的运行行为由 `BitongueConfig` 集中描述，在创建编排器时传入：

```python
from bitongue.client import BitongueConfig

config = BitongueConfig(
    flowing_size=16,
    flowing_timeout=30,
    handle_timeout=5.0,
    handle_concurrency=1,
)
```

`BitongueConfig` 本身是 msgspec 结构体（继承 `BaseStruct`），四个字段均为必填。

## 字段一览

| 字段 | 类型 | 单位 | 语义 |
|-|-|-|-|
| `flowing_size` | `int` | 条 | 流窗口的有界缓冲容量；窗口满时 `send()` 等待，形成背压 |
| `flowing_timeout` | `int \| None` | 秒 | 消息在窗口内的存活时间；消费时剔除入库后超时的条目；`None` 表示永不过期 |
| `handle_timeout` | `float` | 秒 | 单条消息允许的最大处理耗时；超时消息被跳过（不产出结果，不中断消费） |
| `handle_concurrency` | `int` | — | 处理并发配置；**当前版本该字段已定义但尚未参与调度逻辑，属预留字段**，写入任意值不改变行为 |

## 各字段的行为细节

### `flowing_size`

容量作用于 anyio 内存流的最大缓冲长度。消息从 `send()` 进入缓冲，到 `result()` 取出为止都占用一个槽位。取值建议：

- 值过小：突发流量下生产者频繁等待；
- 值过大：突发流量被全量缓存，消费侧的过期剔除压力与内存占用随之上升。

### `flowing_timeout`

存活计时从消息**入库**（`send()`）时刻开始，等待缓冲的时间也计入。过期条目在**消费侧**被剔除：不产出结果、不报错，对生产者完全透明。设为 `None` 可关闭该层超时，让消息无限期等待消费。

两层超时的分工：`flowing_timeout` 管「消息值得被处理多久」，`handle_timeout` 管「处理一条消息最多花多久」。

### `handle_timeout`

以 anyio 取消作用域实现：超时会**真正取消**处理器内的执行（而不仅是放弃等待），随后该消息被跳过，消费继续下一条。处理器内部的清理逻辑（`try/finally`、`async with` 等）会正常执行。

### `handle_concurrency`

预留字段，见上表说明；后续版本引入并发处理调度时，语义将在此页更新。

## 生命周期约束

配置只在创建 `Bitongue` 时读取一次，`start()` 时用于构建内部流窗口：

- 未 `start()` 就调用 `send()` 或 `result()` 会抛出 `RuntimeError`；
- `shutdown()` 之后窗口关闭，复用同一编排器需重新 `start()`。

## 一个超时组合的例子

```python
config = BitongueConfig(
    flowing_size=64,      # 允许突发 64 条排队
    flowing_timeout=10,   # 排队超过 10 秒的消息到期作废
    handle_timeout=2.0,   # 单条处理最多 2 秒，超时跳过
    handle_concurrency=1,
)
```

该组合的含义：最坏情况下，一条消息从入库到被处理完成不会超过约 12 秒；过期或超时的消息都不会阻塞后续消息的消费。
