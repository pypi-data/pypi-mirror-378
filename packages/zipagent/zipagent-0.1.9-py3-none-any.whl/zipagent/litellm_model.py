"""LiteLLM 模型实现"""

import os
from collections.abc import Generator
from typing import Any

import litellm

from .model import Model, ModelResponse, StreamDelta, Usage


class LiteLLMModel(Model):
    """基于 LiteLLM 的模型实现，支持多种 LLM 提供商"""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        """
        初始化 LiteLLM 模型

        Args:
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
            **kwargs: 其他参数
        """
        self.model_name = model
        self.api_key = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL")
        self.kwargs = kwargs.copy()

        # 设置 LiteLLM 配置
        if self.api_key:
            litellm.api_key = self.api_key
        if self.base_url:
            litellm.api_base = self.base_url

        # 从环境变量或参数获取 temperature 和 max_tokens
        env_temp = os.getenv("TEMPERATURE")
        self.temperature = (
            float(env_temp) if env_temp else kwargs.get("temperature", 0.7)
        )

        env_max_tokens = os.getenv("MAX_TOKENS")
        self.max_tokens = (
            int(env_max_tokens) if env_max_tokens else kwargs.get("max_tokens")
        )

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        """调用 LiteLLM 生成响应"""
        try:
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
                call_kwargs["max_tokens"] = self.max_tokens

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
