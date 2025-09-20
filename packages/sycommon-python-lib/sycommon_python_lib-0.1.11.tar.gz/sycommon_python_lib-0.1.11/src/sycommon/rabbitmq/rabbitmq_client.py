import asyncio
import logging
import json
from typing import Callable, Coroutine, Optional, Dict, Any, Union, Set, List
from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType
from aio_pika.abc import (
    AbstractConnection,
    AbstractChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractIncomingMessage,
    ConsumerTag
)
from aiormq.exceptions import ChannelInvalidStateError, ConnectionClosed

from sycommon.models.mqmsg_model import MQMsgModel

# 最大重试次数限制
MAX_RETRY_COUNT = 3

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """
    RabbitMQ客户端，支持集群多节点配置，基于aio-pika实现
    提供自动故障转移、连接恢复和消息可靠性保障
    """

    def __init__(
        self,
        hosts: List[str],
        port: int,
        username: str,
        password: str,
        virtualhost: str = "/",
        exchange_name: str = "system.topic.exchange",
        exchange_type: str = "topic",
        queue_name: Optional[str] = None,
        routing_key: str = "#",
        durable: bool = True,
        auto_delete: bool = False,
        auto_parse_json: bool = True,
        create_if_not_exists: bool = True,
        connection_timeout: int = 10,
        rpc_timeout: int = 10,
        app_name: str = "",
        reconnection_delay: int = 1,
        max_reconnection_attempts: int = 5,
        heartbeat: int = 60,
        prefetch_count: int = 2,
        message_process_timeout: int = 30,
        consumption_stall_threshold: int = 120
    ):
        """
        初始化RabbitMQ客户端，支持集群多节点配置

        :param hosts: RabbitMQ主机地址列表（集群节点）
        :param port: RabbitMQ端口
        :param username: 用户名
        :param password: 密码
        :param virtualhost: 虚拟主机
        :param exchange_name: 交换机名称
        :param exchange_type: 交换机类型
        :param queue_name: 队列名称
        :param routing_key: 路由键
        :param durable: 是否持久化
        :param auto_delete: 是否自动删除
        :param auto_parse_json: 是否自动解析JSON消息
        :param create_if_not_exists: 如果资源不存在是否创建
        :param connection_timeout: 连接超时时间(秒)
        :param rpc_timeout: RPC操作超时时间(秒)
        :param app_name: 应用名称，用于标识连接
        :param reconnection_delay: 重连延迟(秒)
        :param max_reconnection_attempts: 最大重连尝试次数
        :param heartbeat: 心跳间隔(秒)
        :param prefetch_count: 预取消息数量
        :param message_process_timeout: 消息处理超时时间(秒)
        :param consumption_stall_threshold: 消费停滞检测阈值(秒)
        """
        # 连接参数 - 支持多主机
        self.hosts = [host.strip() for host in hosts if host.strip()]
        if not self.hosts:
            raise ValueError("至少需要提供一个RabbitMQ主机地址")
        self.port = port
        self.username = username
        self.password = password
        self.virtualhost = virtualhost
        self.app_name = app_name or "rabbitmq-client"

        # 交换器和队列参数
        self.exchange_name = exchange_name
        self.exchange_type = ExchangeType(exchange_type)
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.durable = durable
        self.auto_delete = auto_delete

        # 行为控制参数
        self.auto_parse_json = auto_parse_json
        self.create_if_not_exists = create_if_not_exists
        self.connection_timeout = connection_timeout
        self.rpc_timeout = rpc_timeout
        self.prefetch_count = prefetch_count

        # 重连和保活参数
        self.reconnection_delay = reconnection_delay
        self.max_reconnection_attempts = max_reconnection_attempts
        self.heartbeat = heartbeat

        # 消息处理参数
        self.message_process_timeout = message_process_timeout
        self.consumption_stall_threshold = consumption_stall_threshold

        # 连接和通道对象
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange: Optional[AbstractExchange] = None
        self.queue: Optional[AbstractQueue] = None

        # 当前活跃连接的主机
        self._active_host: Optional[str] = None

        # 状态跟踪
        self.actual_queue_name: Optional[str] = None
        self._exchange_exists = False
        self._queue_exists = False
        self._queue_bound = False
        self._is_consuming = False
        self._closed = False
        self._consumer_tag: Optional[ConsumerTag] = None
        self._last_activity_timestamp = asyncio.get_event_loop().time()
        self._last_message_processed = asyncio.get_event_loop().time()

        # 任务和处理器
        self.message_handler: Optional[Callable[
            [Union[Dict[str, Any], str], AbstractIncomingMessage],
            Coroutine[Any, Any, None]
        ]] = None
        self._consuming_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._keepalive_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None

        # 消息处理跟踪
        self._processing_message_ids: Set[str] = set()

    @property
    def is_connected(self) -> bool:
        """检查连接是否有效"""
        return (not self._closed and
                self.connection is not None and
                not self.connection.is_closed and
                self.channel is not None and
                not self.channel.is_closed and
                self.exchange is not None)

    def _update_activity_timestamp(self) -> None:
        """更新最后活动时间戳"""
        self._last_activity_timestamp = asyncio.get_event_loop().time()

    def _update_message_processed_timestamp(self) -> None:
        """更新最后消息处理时间戳"""
        self._last_message_processed = asyncio.get_event_loop().time()

    async def _check_exchange_exists(self) -> bool:
        """检查交换机是否存在"""
        if not self.channel:
            return False

        try:
            # 使用被动模式检查交换机是否存在
            await asyncio.wait_for(
                self.channel.declare_exchange(
                    name=self.exchange_name,
                    type=self.exchange_type,
                    passive=True
                ),
                timeout=self.rpc_timeout
            )
            self._exchange_exists = True
            self._update_activity_timestamp()
            return True
        except asyncio.TimeoutError:
            logger.error(
                f"检查交换机 '{self.exchange_name}' 超时 (主机: {self._active_host})")
            return False
        except Exception as e:
            logger.debug(
                f"交换机 '{self.exchange_name}' 不存在: {str(e)} (主机: {self._active_host})")
            return False

    async def _check_queue_exists(self) -> bool:
        """检查队列是否存在"""
        if not self.channel or not self.queue_name:
            return False

        try:
            # 使用被动模式检查队列是否存在
            await asyncio.wait_for(
                self.channel.declare_queue(
                    name=self.queue_name,
                    passive=True
                ),
                timeout=self.rpc_timeout
            )
            self._queue_exists = True
            self._update_activity_timestamp()
            return True
        except asyncio.TimeoutError:
            logger.error(
                f"检查队列 '{self.queue_name}' 超时 (主机: {self._active_host})")
            return False
        except Exception as e:
            logger.debug(
                f"队列 '{self.queue_name}' 不存在: {str(e)} (主机: {self._active_host})")
            return False

    async def _bind_queue(self) -> bool:
        """将队列绑定到交换机"""
        if not self.channel or not self.queue or not self.exchange:
            return False

        retries = 2
        bind_routing_key = self.routing_key if self.routing_key else '#'

        for attempt in range(retries + 1):
            try:
                await asyncio.wait_for(
                    self.queue.bind(
                        self.exchange,
                        routing_key=bind_routing_key
                    ),
                    timeout=self.rpc_timeout
                )
                self._queue_bound = True
                self._update_activity_timestamp()
                logger.info(
                    f"队列 '{self.queue_name}' 已绑定到交换机 '{self.exchange_name}'，路由键: {bind_routing_key} (主机: {self._active_host})")
                return True
            except asyncio.TimeoutError:
                logger.warning(
                    f"队列 '{self.queue_name}' 绑定超时（第{attempt+1}次尝试）(主机: {self._active_host})")
            except Exception as e:
                logger.error(
                    f"队列绑定失败（第{attempt+1}次尝试）: {str(e)} (主机: {self._active_host})")

            if attempt < retries:
                await asyncio.sleep(1)

        self._queue_bound = False
        return False

    async def _try_connect_host(self, host: str) -> AbstractConnection:
        """尝试连接单个主机"""
        try:
            logger.debug(f"尝试连接主机: {host}:{self.port}")
            return await asyncio.wait_for(
                connect_robust(
                    host=host,
                    port=self.port,
                    login=self.username,
                    password=self.password,
                    virtualhost=self.virtualhost,
                    heartbeat=self.heartbeat,
                    client_properties={
                        "connection_name": f"{self.app_name}@{host}"
                    }
                ),
                timeout=self.connection_timeout
            )
        except Exception as e:
            logger.warning(f"连接主机 {host}:{self.port} 失败: {str(e)}")
            raise

    async def connect(self, force_reconnect: bool = False, declare_queue: bool = True) -> None:
        """
        建立与RabbitMQ集群的连接（支持多节点故障转移）并初始化所需资源

        :param force_reconnect: 是否强制重新连接
        :param declare_queue: 是否声明队列
        """
        logger.debug(
            f"连接参数 - force_reconnect={force_reconnect}, "
            f"declare_queue={declare_queue}, create_if_not_exists={self.create_if_not_exists}, "
            f"主机列表: {self.hosts}"
        )

        # 如果已连接且不强制重连，则直接返回
        if self.is_connected and not force_reconnect:
            return

        # 取消正在进行的重连任务
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()

        logger.debug(
            f"尝试连接RabbitMQ集群 - 主机数量: {len(self.hosts)}, "
            f"虚拟主机: {self.virtualhost}, 队列: {self.queue_name}"
        )

        # 重置状态
        self._exchange_exists = False
        self._queue_exists = False
        self._queue_bound = False
        self._active_host = None

        retries = 0
        last_exception = None

        while retries < self.max_reconnection_attempts:
            # 遍历所有主机尝试连接（故障转移）
            for host in self.hosts:
                try:
                    # 关闭现有连接
                    if self.connection and not self.connection.is_closed:
                        await self.connection.close()

                    # 尝试连接当前主机
                    self.connection = await self._try_connect_host(host)
                    self._active_host = host

                    # 创建通道
                    self.channel = await asyncio.wait_for(
                        self.connection.channel(),
                        timeout=self.rpc_timeout
                    )

                    # 设置预取计数，控制消息公平分发
                    await self.channel.set_qos(prefetch_count=self.prefetch_count)

                    # 处理交换机
                    exchange_exists = await self._check_exchange_exists()
                    if not exchange_exists:
                        if self.create_if_not_exists:
                            # 创建交换机
                            self.exchange = await asyncio.wait_for(
                                self.channel.declare_exchange(
                                    name=self.exchange_name,
                                    type=self.exchange_type,
                                    durable=self.durable,
                                    auto_delete=self.auto_delete
                                ),
                                timeout=self.rpc_timeout
                            )
                            self._exchange_exists = True
                            logger.info(
                                f"已创建交换机 '{self.exchange_name}' (主机: {self._active_host})")
                        else:
                            raise Exception(
                                f"交换机 '{self.exchange_name}' 不存在且不允许自动创建 (主机: {self._active_host})")
                    else:
                        # 获取已有交换机
                        self.exchange = await asyncio.wait_for(
                            self.channel.get_exchange(self.exchange_name),
                            timeout=self.rpc_timeout
                        )
                        logger.info(
                            f"使用已存在的交换机 '{self.exchange_name}' (主机: {self._active_host})")

                    # 处理队列
                    if declare_queue and self.queue_name:
                        queue_exists = await self._check_queue_exists()

                        if not queue_exists:
                            if not self.create_if_not_exists:
                                raise Exception(
                                    f"队列 '{self.queue_name}' 不存在且不允许自动创建 (主机: {self._active_host})")

                            # 创建队列
                            self.queue = await asyncio.wait_for(
                                self.channel.declare_queue(
                                    name=self.queue_name,
                                    durable=self.durable,
                                    auto_delete=self.auto_delete,
                                    exclusive=False
                                ),
                                timeout=self.rpc_timeout
                            )
                            self._queue_exists = True
                            self.actual_queue_name = self.queue_name
                            logger.info(
                                f"已创建队列 '{self.queue_name}' (主机: {self._active_host})")
                        else:
                            # 获取已有队列
                            self.queue = await asyncio.wait_for(
                                self.channel.get_queue(self.queue_name),
                                timeout=self.rpc_timeout
                            )
                            self.actual_queue_name = self.queue_name
                            logger.info(
                                f"使用已存在的队列 '{self.queue_name}' (主机: {self._active_host})")

                        # 绑定队列到交换机
                        if self.queue and self.exchange:
                            bound = await self._bind_queue()
                            if not bound:
                                raise Exception(
                                    f"队列 '{self.queue_name}' 绑定到交换机 '{self.exchange_name}' 失败 (主机: {self._active_host})")
                        else:
                            raise Exception(
                                "队列或交换机未正确初始化 (主机: {self._active_host})")
                    else:
                        # 不声明队列时的状态处理
                        self.queue = None
                        self.actual_queue_name = None
                        self._queue_exists = False
                        self._queue_bound = False
                        logger.debug(
                            f"跳过队列 '{self.queue_name}' 的声明和绑定 (主机: {self._active_host})")

                    # 验证连接状态
                    if not self.is_connected:
                        raise Exception(
                            f"连接验证失败，状态异常 (主机: {self._active_host})")

                    # 如果之前在消费，重新开始消费
                    if self._is_consuming and self.message_handler:
                        await self.start_consuming()

                    # 启动连接监控和保活任务
                    self._start_monitoring()
                    self._start_keepalive()

                    self._update_activity_timestamp()
                    logger.info(
                        f"RabbitMQ客户端连接成功 (主机: {self._active_host}, 队列: {self.actual_queue_name})")
                    return

                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"主机 {host} 连接处理失败: {str(e)}，尝试下一个主机...")
                    # 清理当前失败的连接资源
                    if self.connection and not self.connection.is_closed:
                        await self.connection.close()
                    self.connection = None
                    self.channel = None
                    self.exchange = None
                    self.queue = None

            # 所有主机都尝试失败，进行重试
            retries += 1
            logger.warning(
                f"集群连接失败（{retries}/{self.max_reconnection_attempts}），所有主机均无法连接，重试中...")

            if retries < self.max_reconnection_attempts:
                await asyncio.sleep(self.reconnection_delay)

        logger.error(f"最终连接失败: {str(last_exception)}")
        raise Exception(
            f"经过{self.max_reconnection_attempts}次重试后仍无法连接到RabbitMQ集群。最后错误: {str(last_exception)}")

    def _start_monitoring(self) -> None:
        """启动连接和消费监控任务，支持集群节点故障检测"""
        if self._closed or (self._monitor_task and not self._monitor_task.done()):
            return

        async def monitor():
            while not self._closed and self.connection:
                try:
                    # 检查连接状态
                    if self.connection.is_closed:
                        logger.warning(
                            f"检测到RabbitMQ连接已关闭 (主机: {self._active_host})，将尝试重连到集群其他节点")
                        await self._schedule_reconnect()
                        return

                    # 检查通道状态
                    if self.channel and self.channel.is_closed:
                        logger.warning(
                            f"检测到RabbitMQ通道已关闭 (主机: {self._active_host})，将尝试重建")
                        await self._recreate_channel()
                        continue

                    # 检查消费停滞
                    if self._is_consuming:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - self._last_message_processed > self.consumption_stall_threshold:
                            logger.warning(
                                f"检测到消费停滞超过 {self.consumption_stall_threshold} 秒 (主机: {self._active_host})，将重启消费者")
                            if self._is_consuming and self.message_handler:
                                await self.stop_consuming()
                                await self.start_consuming()
                                logger.info("消费者已重启以恢复消费")
                except Exception as e:
                    logger.error(f"监控任务出错: {str(e)}")
                    await asyncio.sleep(1)

                await asyncio.sleep(5)  # 每5秒检查一次

        self._monitor_task = asyncio.create_task(monitor())

    async def _recreate_channel(self) -> None:
        """重建通道并恢复绑定和消费，支持当前节点故障时的快速恢复"""
        try:
            # 连接已关闭时触发完整重连（尝试其他节点）
            if not self.connection or self.connection.is_closed:
                logger.warning("连接已关闭，触发集群重连")
                await self._schedule_reconnect()
                return

            # 重新创建通道
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=self.prefetch_count)

            # 重新获取交换机
            self.exchange = await self.channel.get_exchange(self.exchange_name)

            # 重新绑定队列和交换机
            if self.queue_name:
                self.queue = await self.channel.get_queue(self.queue_name)
                if self.queue and self.exchange:
                    await self._bind_queue()

            # 重新开始消费
            if self._is_consuming and self.message_handler:
                await self.start_consuming()

            logger.info(f"通道已重新创建并恢复服务 (主机: {self._active_host})")
            self._update_activity_timestamp()
        except Exception as e:
            logger.error(f"通道重建失败，触发集群重连: {str(e)} (主机: {self._active_host})")
            await self._schedule_reconnect()

    def _start_keepalive(self) -> None:
        """启动连接保活任务，维护集群连接心跳"""
        if self._closed or (self._keepalive_task and not self._keepalive_task.done()):
            return

        async def keepalive():
            while not self._closed and self.is_connected:
                current_time = asyncio.get_event_loop().time()
                # 检查是否超过指定时间无活动
                if current_time - self._last_activity_timestamp > self.heartbeat * 1.5:
                    logger.debug(
                        f"连接 {self.heartbeat*1.5}s 无活动，执行保活检查 (主机: {self._active_host})")
                    try:
                        if self.connection and self.connection.is_closed:
                            logger.warning("连接已关闭，触发集群重连")
                            await self._schedule_reconnect()
                            return

                        # 执行轻量级操作保持连接活跃
                        if self.channel:
                            await asyncio.wait_for(
                                self.channel.declare_exchange(
                                    name=self.exchange_name,
                                    type=self.exchange_type,
                                    passive=True  # 仅检查存在性
                                ),
                                timeout=5
                            )

                        self._update_activity_timestamp()
                    except asyncio.TimeoutError:
                        logger.warning(
                            f"保活检查超时，触发集群重连 (主机: {self._active_host})")
                        await self._schedule_reconnect()
                    except Exception as e:
                        logger.warning(
                            f"保活检查失败: {str(e)}，触发集群重连 (主机: {self._active_host})")
                        await self._schedule_reconnect()

                await asyncio.sleep(self.heartbeat / 2)  # 每心跳间隔的一半检查一次

        self._keepalive_task = asyncio.create_task(keepalive())

    async def _schedule_reconnect(self) -> None:
        """安排重新连接（尝试集群中的所有节点）"""
        if self._reconnect_task and not self._reconnect_task.done():
            return

        logger.info(f"将在 {self.reconnection_delay} 秒后尝试重新连接到RabbitMQ集群...")

        async def reconnect():
            try:
                await asyncio.sleep(self.reconnection_delay)
                if not self._closed:
                    # 重连时尝试所有节点
                    await self.connect(force_reconnect=True)
            except Exception as e:
                logger.error(f"重连任务失败: {str(e)}")
                if not self._closed:
                    await self._schedule_reconnect()

        self._reconnect_task = asyncio.create_task(reconnect())

    async def close(self) -> None:
        """关闭连接并清理资源"""
        self._closed = True
        self._is_consuming = False

        # 取消所有任务
        for task in [self._keepalive_task, self._reconnect_task,
                     self._consuming_task, self._monitor_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # 关闭连接
        if self.connection and not self.connection.is_closed:
            try:
                await asyncio.wait_for(self.connection.close(), timeout=5)
            except Exception as e:
                logger.warning(f"关闭连接时出错 (主机: {self._active_host}): {str(e)}")

        # 重置状态
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self._exchange_exists = False
        self._queue_exists = False
        self._queue_bound = False
        self._consumer_tag = None
        self._processing_message_ids.clear()
        self._active_host = None

        logger.info("RabbitMQ客户端已关闭")

    async def publish(
        self,
        message_body: Union[str, Dict[str, Any]],
        routing_key: Optional[str] = None,
        content_type: str = "application/json",
        headers: Optional[Dict[str, Any]] = None,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    ) -> None:
        """
        发布消息到交换机（自动处理连接故障并重试）

        :param message_body: 消息体，可以是字符串或字典
        :param routing_key: 路由键，如未指定则使用实例的routing_key
        :param content_type: 内容类型
        :param headers: 消息头
        :param delivery_mode: 投递模式，持久化或非持久化
        """
        if not self.is_connected:
            logger.warning("连接已关闭，尝试重连后发布消息")
            await self.connect(force_reconnect=True)

        if not self.channel or not self.exchange:
            raise Exception("RabbitMQ连接未初始化")

        # 处理消息体
        if isinstance(message_body, dict):
            message_body_str = json.dumps(message_body, ensure_ascii=False)
            if content_type == "text/plain":
                content_type = "application/json"
        else:
            message_body_str = str(message_body)

        # 创建消息对象
        message = Message(
            body=message_body_str.encode(),
            content_type=content_type,
            headers=headers or {},
            delivery_mode=delivery_mode
        )

        # 发布消息（带重试机制）
        retry_count = 0
        while retry_count < 2:  # 最多重试2次
            try:
                await self.exchange.publish(
                    message,
                    routing_key=routing_key or self.routing_key or '#'
                )
                self._update_activity_timestamp()
                logger.debug(
                    f"消息已发布到交换机 '{self.exchange_name}' (主机: {self._active_host})")
                return
            except (ConnectionClosed, ChannelInvalidStateError):
                retry_count += 1
                logger.warning(f"连接已关闭，尝试重连后重新发布 (重试次数: {retry_count})")
                await self.connect(force_reconnect=True)
            except Exception as e:
                retry_count += 1
                logger.error(f"消息发布失败 (重试次数: {retry_count}): {str(e)}")
                if retry_count < 2:
                    await asyncio.sleep(1)

        raise Exception(f"消息发布失败，经过{retry_count}次重试仍未成功")

    def set_message_handler(
        self,
        handler: Callable[
            [Union[Dict[str, Any], str], AbstractIncomingMessage],
            Coroutine[Any, Any, None]
        ]
    ) -> None:
        """
        设置消息处理函数

        :param handler: 消息处理函数，接收解析后的消息和原始消息对象
        """
        self.message_handler = handler

    async def start_consuming(self) -> ConsumerTag:
        """
        开始消费消息

        :return: 消费者标签
        """
        if self._is_consuming:
            logger.debug("已经在消费中，返回现有consumer_tag")
            if self._consumer_tag:
                return self._consumer_tag
            raise Exception("消费已启动但未获取到consumer_tag")

        # 确保连接和队列已准备好
        if not self.is_connected:
            await self.connect()

        if not self.queue:
            raise Exception("队列未初始化，无法开始消费")

        if not self.message_handler:
            raise Exception("未设置消息处理函数")

        self._is_consuming = True
        logger.info(
            f"开始消费队列: {self.actual_queue_name} (主机: {self._active_host})")

        try:
            # 开始消费，使用aio-pika的队列消费方法
            self._consumer_tag = await self.queue.consume(
                self._message_wrapper,
                no_ack=False  # 手动确认消息
            )

            logger.info(
                f"消费者已启动，队列: {self.actual_queue_name}, tag: {self._consumer_tag}, 主机: {self._active_host}")
            return self._consumer_tag
        except Exception as e:
            self._is_consuming = False
            logger.error(
                f"启动消费失败: {str(e)} (主机: {self._active_host})", exc_info=True)
            raise

    async def _safe_cancel_consumer(self) -> bool:
        """安全取消消费者"""
        if not self._consumer_tag or not self.queue or not self.channel:
            return True

        try:
            await asyncio.wait_for(
                self.queue.cancel(self._consumer_tag),
                timeout=self.rpc_timeout
            )
            logger.info(
                f"消费者 {self._consumer_tag} 已取消 (主机: {self._active_host})")
            return True
        except (ChannelInvalidStateError, ConnectionClosed):
            logger.warning(f"取消消费者失败：通道或连接已关闭 (主机: {self._active_host})")
            return False
        except asyncio.TimeoutError:
            logger.warning(f"取消消费者超时 (主机: {self._active_host})")
            return False
        except Exception as e:
            logger.error(f"取消消费者异常: {str(e)} (主机: {self._active_host})")
            return False

    async def stop_consuming(self) -> None:
        """停止消费消息，等待正在处理的消息完成"""
        if not self._is_consuming:
            return

        self._is_consuming = False

        # 取消消费者，停止接收新消息
        if self._consumer_tag and self.queue:
            await self._safe_cancel_consumer()

        # 等待所有正在处理的消息完成
        if self._processing_message_ids:
            logger.info(
                f"等待 {len(self._processing_message_ids)} 个正在处理的消息完成... (主机: {self._active_host})"
            )
            # 循环等待直到所有消息处理完成
            while self._processing_message_ids and not self._closed:
                await asyncio.sleep(0.1)

        # 清理状态
        self._consumer_tag = None
        self._processing_message_ids.clear()

        logger.info(
            f"已停止消费队列: {self.actual_queue_name} (主机: {self._active_host})")

    async def _parse_message(self, message: AbstractIncomingMessage) -> Union[Dict[str, Any], str]:
        """解析消息体"""
        try:
            body_str = message.body.decode('utf-8')
            self._update_activity_timestamp()

            if self.auto_parse_json:
                return json.loads(body_str)
            return body_str
        except json.JSONDecodeError:
            logger.warning(f"消息解析JSON失败，返回原始字符串 (主机: {self._active_host})")
            return body_str
        except Exception as e:
            logger.error(f"消息解析出错: {str(e)} (主机: {self._active_host})")
            return message.body.decode('utf-8')

    async def _message_wrapper(self, message: AbstractIncomingMessage) -> None:
        """消息处理包装器，处理消息接收、解析、分发和确认"""
        if not self.message_handler or not self._is_consuming:
            logger.warning("未设置消息处理器或已停止消费，确认消息")
            await message.ack()
            return

        # 跟踪消息ID，防止重复处理
        message_id = message.message_id or str(id(message))
        if message_id in self._processing_message_ids:
            logger.warning(
                f"检测到重复处理的消息ID: {message_id}，直接确认 (主机: {self._active_host})")
            await message.ack()
            return

        self._processing_message_ids.add(message_id)

        try:
            logger.debug(
                f"收到队列 {self.actual_queue_name} 的消息: {message_id} (主机: {self._active_host})")

            # 解析消息
            parsed_data = await self._parse_message(message)

            # 消息处理超时控制
            # try:
            #     await asyncio.wait_for(
            #         self.message_handler(MQMsgModel(**parsed_data), message),
            #         timeout=self.message_process_timeout
            #     )
            # except asyncio.TimeoutError:
            #     logger.error(
            #         f"消息 {message_id} 处理超时（超过 {self.message_process_timeout} 秒）(主机: {self._active_host})")
            #     await message.ack()  # 超时也确认，避免无限重试
            #     return
            await self.message_handler(MQMsgModel(**parsed_data), message)

            # 处理成功，确认消息
            await message.ack()
            self._update_activity_timestamp()
            self._update_message_processed_timestamp()
            logger.debug(f"消息 {message_id} 处理完成并确认 (主机: {self._active_host})")

        except Exception as e:
            # 处理失败，根据重试次数决定是否重新发布
            current_headers = message.headers or {}
            retry_count = current_headers.get('x-retry-count', 0)
            retry_count += 1

            logger.error(
                f"消息 {message_id} 处理出错（第{retry_count}次重试）: {str(e)} (主机: {self._active_host})",
                exc_info=True
            )

            if retry_count >= MAX_RETRY_COUNT:
                logger.error(
                    f"消息 {message_id} 已达到最大重试次数({MAX_RETRY_COUNT}次)，标记为失败 (主机: {self._active_host})")
                await message.ack()
                self._update_activity_timestamp()
                return

            # 准备重新发布的消息
            new_headers = current_headers.copy()
            new_headers['x-retry-count'] = retry_count

            new_message = Message(
                body=message.body,
                content_type=message.content_type,
                headers=new_headers,
                delivery_mode=message.delivery_mode
            )

            # 拒绝原消息（不重新入队）
            await message.reject(requeue=False)

            # 重新发布消息
            if self.exchange:
                await self.exchange.publish(
                    new_message,
                    routing_key=self.routing_key or '#'
                )
                self._update_activity_timestamp()
                logger.info(
                    f"消息 {message_id} 已重新发布，当前重试次数: {retry_count} (主机: {self._active_host})")
        finally:
            # 移除消息ID跟踪
            if message_id in self._processing_message_ids:
                self._processing_message_ids.remove(message_id)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
