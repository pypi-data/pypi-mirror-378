"""Model - LLM交互接口模块"""

import os
from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from .context import Usage

# 尝试加载环境变量
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv不是必需的依赖


@dataclass
class ModelResponse:
    """模型响应结果"""

    content: str | None
    tool_calls: list[dict[str, Any]] | None
    usage: Usage
    finish_reason: str


@dataclass
class StreamDelta:
    """流式响应增量"""

    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str | None = None


class Model(ABC):
    """LLM模型抽象基类"""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        """生成模型响应"""
        pass

    def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Generator[StreamDelta | ModelResponse, None, None]:
        """生成流式响应（可选实现）"""
        # 默认实现：调用普通生成，然后逐字符yield
        response = self.generate(messages, tools)
        if response.content:
            for char in response.content:
                yield StreamDelta(content=char)
        # 最后yield完整的响应
        yield response


class OpenAIModel(Model):
    """基于原生OpenAI的模型实现"""

    def __init__(
        self,
        model: str | None = None,  # 统一参数名
        model_name: str | None = None,  # 兼容旧版本
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ):
        """
        初始化OpenAI模型

        Args:
            model_name: 模型名称，如果不指定会从环境变量MODEL读取
            api_key: API密钥，如果不指定会从环境变量API_KEY读取
            base_url: API基础URL，如果不指定会从环境变量BASE_URL读取
            **kwargs: 其他参数
        """
        try:
            from openai import OpenAI

            # 从环境变量或参数获取配置，支持两种参数名，优先使用model
            self.model_name = (
                model or model_name or os.getenv("MODEL", "gpt-3.5-turbo")
            )
            self.api_key = api_key or os.getenv("API_KEY")
            self.base_url = base_url or os.getenv("BASE_URL")

            # 构建客户端参数
            client_kwargs = {}
            if self.api_key:
                client_kwargs["api_key"] = self.api_key
            if self.base_url:
                client_kwargs["base_url"] = self.base_url

            # 创建OpenAI客户端
            self.client = OpenAI(**client_kwargs)

            # 其他参数
            self.kwargs = kwargs.copy()
            # 从环境变量或参数获取 temperature 和 max_tokens
            env_temp = os.getenv("TEMPERATURE")
            self.temperature = (
                float(env_temp) if env_temp else kwargs.get("temperature", 0.7)
            )

            env_max_tokens = os.getenv("MAX_TOKENS")
            self.max_tokens = (
                int(env_max_tokens)
                if env_max_tokens
                else kwargs.get("max_tokens")
            )

        except ImportError as e:
            raise ImportError("需要安装openai包: pip install openai") from e

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        """调用OpenAI生成响应"""
        # 准备API调用参数
        call_kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            **self.kwargs,
        }

        # 只有当 max_tokens 有值时才添加
        if self.max_tokens is not None:
            call_kwargs["max_tokens"] = self.max_tokens

        # 如果有工具，添加到请求中
        if tools:
            call_kwargs["tools"] = tools
            call_kwargs["tool_choice"] = "auto"

        # 调用OpenAI API
        response = self.client.chat.completions.create(**call_kwargs)

        # 解析响应
        message = response.choices[0].message
        content = message.content
        tool_calls: list[dict[str, Any]] | None = None

        # 处理工具调用
        if message.tool_calls:
            tool_calls = []
            for call in message.tool_calls:
                tool_call = {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                tool_calls.append(tool_call)

        # 解析使用量
        usage = Usage()
        if response.usage:
            usage.input_tokens = response.usage.prompt_tokens or 0
            usage.output_tokens = response.usage.completion_tokens or 0
            usage.total_tokens = response.usage.total_tokens or 0

        return ModelResponse(
            content=content,
            tool_calls=tool_calls,
            usage=usage,
            finish_reason=response.choices[0].finish_reason or "stop",
        )

    def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Generator[StreamDelta | ModelResponse, None, None]:
        """调用OpenAI流式生成响应"""
        try:
            # 准备API调用参数
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,  # 使用实例变量
                "stream": True,  # 启用流式
                **self.kwargs,
            }

            # 只有当 max_tokens 有值时才添加
            if self.max_tokens is not None:
                call_kwargs["max_tokens"] = self.max_tokens

            # 如果有工具，添加到请求中
            if tools:
                call_kwargs["tools"] = tools
                call_kwargs["tool_choice"] = "auto"

            # 调用OpenAI流式API
            stream = self.client.chat.completions.create(**call_kwargs)

            # 收集完整响用于最终返回
            full_content = ""
            tool_calls: list[dict[str, Any]] = []
            finish_reason = "stop"
            usage = Usage()

            # 处理流式响应
            last_chunk = None
            try:
                for chunk in stream:
                    last_chunk = chunk

                    # 确保choices存在且不为空
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta

                        # 处理内容增量
                        if hasattr(delta, "content") and delta.content:
                            full_content += delta.content
                            yield StreamDelta(content=delta.content)

                        # 处理工具调用（流式累积）
                        if hasattr(delta, "tool_calls") and delta.tool_calls:
                            # 流式工具调用处理
                            for tool_call_delta in delta.tool_calls:
                                index = tool_call_delta.index

                                # 确保tool_calls列表足够长
                                while len(tool_calls) <= index:
                                    tool_calls.append(
                                        {
                                            "id": "",
                                            "type": "function",
                                            "function": {
                                                "name": "",
                                                "arguments": "",
                                            },
                                        }
                                    )

                                # 累积工具调用信息
                                if (
                                    hasattr(tool_call_delta, "id")
                                    and tool_call_delta.id
                                ):
                                    tool_calls[index]["id"] = (
                                        tool_call_delta.id
                                    )

                                if (
                                    hasattr(tool_call_delta, "function")
                                    and tool_call_delta.function
                                ):
                                    if (
                                        hasattr(
                                            tool_call_delta.function, "name"
                                        )
                                        and tool_call_delta.function.name
                                    ):
                                        tool_calls[index]["function"][
                                            "name"
                                        ] = tool_call_delta.function.name

                                    if (
                                        hasattr(
                                            tool_call_delta.function,
                                            "arguments",
                                        )
                                        and tool_call_delta.function.arguments
                                    ):
                                        tool_calls[index]["function"][
                                            "arguments"
                                        ] += tool_call_delta.function.arguments

                        # 处理结束原因
                        if (
                            hasattr(chunk.choices[0], "finish_reason")
                            and chunk.choices[0].finish_reason
                        ):
                            finish_reason = chunk.choices[0].finish_reason
            except Exception as stream_error:
                # 流式解析错误，但保留已经获得的内容和工具调用
                # 这通常是由于API服务器返回格式不正确的SSE数据导致的
                # 我们优雅地处理这个错误，保留已经成功解析的内容
                print(f"流式解析错误: {stream_error}")
                print(f"错误类型: {type(stream_error).__name__}")
                import traceback

                print(f"错误堆栈: {traceback.format_exc()}")

            # 解析使用量（在流式响应的最后一个chunk中）
            if (
                last_chunk
                and hasattr(last_chunk, "usage")
                and last_chunk.usage
            ):
                usage.input_tokens = last_chunk.usage.prompt_tokens or 0
                usage.output_tokens = last_chunk.usage.completion_tokens or 0
                usage.total_tokens = last_chunk.usage.total_tokens or 0

            # 最后yield完整的响应
            yield ModelResponse(
                content=full_content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            # 错误处理 - 返回错误增量
            error_msg = f"模型流式调用出错: {e!s}"
            yield StreamDelta(content=error_msg)
            yield ModelResponse(
                content=error_msg,
                tool_calls=[],
                usage=Usage(),
                finish_reason="error",
            )


class LiteLLMModel(Model):
    """基于 LiteLLM 的模型实现，支持多种 LLM 提供商"""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ):
        """
        初始化 LiteLLM 模型

        Args:
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
            **kwargs: 其他参数
        """
        try:
            import litellm

            # litellm._turn_on_debug()

        except ImportError as e:
            raise ImportError("需要安装litellm包: pip install litellm") from e

        self.model_name = model
        self.api_key = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL")
        self.kwargs = kwargs.copy()

        # 设置 LiteLLM 配置
        if self.api_key:
            litellm.api_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url

        # 配置自定义模型映射（支持 OneAPI 等自定义端点）
        if self.base_url:
            # 对于自定义端点，LiteLLM需要明确的provider前缀
            # OneAPI等OpenAI兼容端点应该使用openai/前缀
            if model.lower().startswith("oneapi-"):
                # 保留完整的oneapi-前缀模型名，但告诉LiteLLM这是openai兼容的
                self.model_name = f"openai/{model}"
            else:
                # 其他自定义端点也默认使用openai兼容格式
                self.model_name = f"openai/{model}"
        elif "oneapi" in model.lower():
            # 如果模型名包含oneapi但没有自定义base_url，使用openai兼容格式
            if model.lower().startswith("oneapi-"):
                clean_model = model[7:]  # 去掉 "oneapi-" 前缀
                self.model_name = f"openai/{clean_model}"
            else:
                self.model_name = f"openai/{model}"

        # 从环境变量或参数获取 temperature 和 max_tokens
        env_temp = os.getenv("TEMPERATURE")
        self.temperature = (
            float(env_temp) if env_temp else kwargs.get("temperature", 0.7)
        )

        env_max_tokens = 300000
        self.max_tokens = (
            int(env_max_tokens) if env_max_tokens else kwargs.get("max_tokens")
        )

        # 调试日志
        import litellm

        litellm.set_verbose = True
        print(
            f"[LiteLLMModel] 初始化: model={self.model_name}, max_tokens={self.max_tokens}"
        )

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        """调用 LiteLLM 生成响应"""
        try:
            import litellm

            # 准备 API 调用参数
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                **self.kwargs,
            }

            # 只有当 max_tokens 有值时才添加
            if self.max_tokens is not None:
                call_kwargs["max_tokens"] = self.max_tokens

            # 如果有工具，添加到请求中
            if tools:
                call_kwargs["tools"] = tools
                call_kwargs["tool_choice"] = "auto"

            # 调用 LiteLLM API
            # 为 OneAPI 等自定义端点设置参数
            if self.base_url:
                call_kwargs["api_base"] = self.base_url
                call_kwargs["base_url"] = self.base_url  # 某些版本需要这个参数
            if self.api_key:
                call_kwargs["api_key"] = self.api_key

            response = litellm.completion(**call_kwargs)

            # 解析响应
            message = response.choices[0].message
            content = message.content
            tool_calls: list[dict[str, Any]] | None = None

            # 处理工具调用
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = []
                for call in message.tool_calls:
                    tool_call = {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    tool_calls.append(tool_call)

            # 解析使用量
            usage = Usage()
            if hasattr(response, "usage") and response.usage:
                usage.input_tokens = (
                    getattr(response.usage, "prompt_tokens", 0) or 0
                )
                usage.output_tokens = (
                    getattr(response.usage, "completion_tokens", 0) or 0
                )
                usage.total_tokens = (
                    getattr(response.usage, "total_tokens", 0) or 0
                )

            return ModelResponse(
                content=content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=getattr(
                    response.choices[0], "finish_reason", "stop"
                )
                or "stop",
            )

        except Exception as e:
            error_msg = f"LiteLLM 调用出错: {e!s}"
            return ModelResponse(
                content=error_msg,
                tool_calls=[],
                usage=Usage(),
                finish_reason="error",
            )

    def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Generator[StreamDelta | ModelResponse, None, None]:
        """调用 LiteLLM 流式生成响应"""
        try:
            import litellm

            # 准备 API 调用参数
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "stream": True,  # 启用流式
                **self.kwargs,
            }

            # 只有当 max_tokens 有值时才添加
            if self.max_tokens is not None:
                call_kwargs["max_tokens"] = 100000

            # 如果有工具，添加到请求中
            if tools:
                call_kwargs["tools"] = tools
                call_kwargs["tool_choice"] = "auto"

            # 调用 LiteLLM 流式 API
            # 为 OneAPI 等自定义端点设置参数
            if self.base_url:
                call_kwargs["api_base"] = self.base_url
                call_kwargs["base_url"] = self.base_url  # 某些版本需要这个参数
            if self.api_key:
                call_kwargs["api_key"] = self.api_key

            stream = litellm.completion(**call_kwargs)

            # 收集完整响应用于最终返回
            full_content = ""
            tool_calls: list[dict[str, Any]] = []
            finish_reason = "stop"
            usage = Usage()

            # 处理流式响应
            last_chunk = None
            try:
                for chunk in stream:
                    last_chunk = chunk

                    # 确保 choices 存在且不为空
                    if (
                        hasattr(chunk, "choices")
                        and chunk.choices
                        and len(chunk.choices) > 0
                    ):
                        delta = chunk.choices[0].delta

                        # 处理内容增量
                        if hasattr(delta, "content") and delta.content:
                            full_content += delta.content
                            yield StreamDelta(content=delta.content)

                        # 处理工具调用（流式累积）
                        if hasattr(delta, "tool_calls") and delta.tool_calls:
                            # 流式工具调用处理
                            for tool_call_delta in delta.tool_calls:
                                index = tool_call_delta.index

                                # 确保 tool_calls 列表足够长
                                while len(tool_calls) <= index:
                                    tool_calls.append(
                                        {
                                            "id": "",
                                            "type": "function",
                                            "function": {
                                                "name": "",
                                                "arguments": "",
                                            },
                                        }
                                    )

                                # 累积工具调用信息
                                if (
                                    hasattr(tool_call_delta, "id")
                                    and tool_call_delta.id
                                ):
                                    tool_calls[index]["id"] = (
                                        tool_call_delta.id
                                    )

                                if (
                                    hasattr(tool_call_delta, "function")
                                    and tool_call_delta.function
                                ):
                                    if (
                                        hasattr(
                                            tool_call_delta.function, "name"
                                        )
                                        and tool_call_delta.function.name
                                    ):
                                        tool_calls[index]["function"][
                                            "name"
                                        ] = tool_call_delta.function.name

                                    if (
                                        hasattr(
                                            tool_call_delta.function,
                                            "arguments",
                                        )
                                        and tool_call_delta.function.arguments
                                    ):
                                        tool_calls[index]["function"][
                                            "arguments"
                                        ] += tool_call_delta.function.arguments

                        # 处理结束原因
                        if (
                            hasattr(chunk.choices[0], "finish_reason")
                            and chunk.choices[0].finish_reason
                        ):
                            finish_reason = chunk.choices[0].finish_reason

            except Exception:
                # 流式解析错误，但保留已经获得的内容和工具调用
                pass

            # 解析使用量（在流式响应的最后一个 chunk 中）
            if (
                last_chunk
                and hasattr(last_chunk, "usage")
                and last_chunk.usage
            ):
                usage.input_tokens = (
                    getattr(last_chunk.usage, "prompt_tokens", 0) or 0
                )
                usage.output_tokens = (
                    getattr(last_chunk.usage, "completion_tokens", 0) or 0
                )
                usage.total_tokens = (
                    getattr(last_chunk.usage, "total_tokens", 0) or 0
                )

            # 最后 yield 完整的响应
            yield ModelResponse(
                content=full_content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=finish_reason,
            )

        except Exception as e:
            # 错误处理 - 返回错误增量
            error_msg = f"LiteLLM 流式调用出错: {e!s}"
            yield StreamDelta(content=error_msg)
            yield ModelResponse(
                content=error_msg,
                tool_calls=[],
                usage=Usage(),
                finish_reason="error",
            )
