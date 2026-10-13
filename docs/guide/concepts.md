# 核心概念

Bitongue 把消息处理拆成五个各自独立、职责单一的概念。本页逐一说明它们的职责、协作方式与边界行为。

## 消息与条目（`BaseMessage` / `MessageEntry`）

`BaseMessage` 是消息的基类（同时是所有数据结构共用的 `BaseStruct` msgspec 结构体的子类），当前定义了文本消息的字段：`type`（固定为 `"text"`）与 `text`（可选文本内容）。它继承的 `BaseStruct` 提供 `to_dict` / `from_dict` / `to_json` / `from_json` 序列化能力，因此每条消息天然可以在字典、JSON 与对象之间互转。

消息被发送时并不会直接进入缓冲，而是先被包装成 `MessageEntry`：除消息本体之外，还记录 `enter_time`（入库时刻）与 `timeout`（存活秒数），供流窗口做过期剔除。

## 流窗口（`Flowing`）

`Flowing[T]` 是内存中的消息流窗口，是有界缓冲的持有者：

- **容量**：`size` 决定缓冲上限（基于 anyio 内存流实现）；窗口满时发送方等待，形成天然背压。
- **存活时间**：`timeout` 是消息在窗口内的存活秒数；不设置则永不过期。
- **生命周期**：`start()` 创建缓冲并开始运行，`shutdown()` 关闭缓冲；未运行时调用 `draw()`（投递）或 `flow()`（消费）会抛出 `FlowingNotInitializedError`。
- **过期剔除发生在消费侧**：`flow()` 逐条产出未过期消息，入库后超过存活秒数的条目被直接跳过，不产出、不报错。

一般情况下不直接操作 `Flowing`，而是通过编排器 `Bitongue` 使用它。

## 过滤器（`BaseFilter`）

`BaseFilter[T]` 是一个 Protocol（结构化接口），实现它只需要一个异步方法：

```python
async def filter(self, message: T) -> bool:
```

返回 `True` 表示放行，`False` 表示拒绝。要点：

- 过滤器链中**全部过滤器都返回 `True`** 消息才会进入处理；任何一个返回 `False`，该消息被静默丢弃。
- 过滤器链**不做短路**：即使第一个过滤器已拒绝，后续过滤器仍会执行。因此过滤器应当是只读的、无副作用的判断。
- 不配置任何过滤器时，全部消息直接放行。

## 处理器与结果（`BaseHandler` / `BaseResult`）

`BaseHandler[T, R]` 是业务处理的扩展点，同样是 Protocol，实现一个异步方法：

```python
async def handle(self, message: T) -> R:
```

`R` 必须是 `BaseResult` 的子类 —— 处理结果与消息一样是 msgspec 结构体，具备序列化能力。把结果类型作为泛型参数显式声明（`BaseHandler[BaseMessage, UpperResult]`），可以从发送到取结果的整个链路都获得类型检查。

处理器抛出的任何异常会被包装成 `MessageHandleError` 向消费者传播；处理耗时超过配置的 `handle_timeout` 则该条消息被跳过（不产出结果，也不中断后续消费）。

## 编排器（`Bitongue` / `BitongueConfig`）

`Bitongue[T, R]` 把上述部件组装成一条完整流水线：

- **构造**：传入 `BitongueConfig` 与处理器（必选）、过滤器集合（可选）；
- **生命周期**：`start()` 内部创建并启动流窗口；`shutdown()` 反向关闭；
- **生产侧**：`send(message)` 投递消息，内部完成条目包装与计时；
- **消费侧**：`result()` 是异步生成器，按序执行「过期剔除 → 过滤链 → 处理器」，逐条产出结果。

注意两个边界行为：未 `start()` 就调用 `send()` 或 `result()` 会抛出 `RuntimeError`；`result()` 同一时刻只应被一个消费者迭代（底层缓冲是单消费者内存流）。

配置项的完整语义见[配置说明](configuration.md)；整条链路的结构视图见[架构与数据流](architecture.md)。
