import json
import uuid
from typing import Any, Dict, List, Set

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import (
    Artifact,
    DataPart,
    Message,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TextPart,
)
from a2a.utils import (
    new_agent_text_message,
    new_artifact,
    new_task,
)
from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot
from loguru import logger

from a2anet.types.langgraph import Artifact as A2ANetArtifact
from a2anet.types.langgraph import StructuredResponse


class LangGraphAgentExecutor(AgentExecutor):
    """An A2A AgentExecutor for LangGraph's `CompiledStateGraph`."""

    def __init__(self, graph: CompiledStateGraph, input_data: Dict[str, Any] | None = None):
        """Initializes the LangGraphAgentExecutor.

        Args:
            graph: A compiled LangGraph state graph.
            input_data: The initial input data for the graph.
        """
        self.graph: CompiledStateGraph = graph
        self.input_data: Dict[str, Any] | None = input_data

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Executes the agent graph for a given request.

        This method streams events from the LangGraph, handling AI messages, tool calls,
        and tool results. It communicates progress and results back to the A2A server
        through the event queue.

        Args:
            context: The request context containing the user's message and current task.
            event_queue: The event queue for sending updates to the A2A server.

        Raises:
            Exception: If the context does not contain a message.
        """
        if not context.message:
            raise Exception("No message in context")

        query: str = context.get_user_input()
        task: Task | None = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # A2A
        task_updater: TaskUpdater = TaskUpdater(event_queue, task.id, task.context_id)

        # LangGraph
        config: RunnableConfig = {"configurable": {"thread_id": task.context_id}}
        state: StateSnapshot = await self.graph.aget_state(config)
        input_data: Dict[str, Any] | None = None

        if "configurable" not in state.config:
            raise ValueError("`state` is not a valid state snapshot!")

        if "checkpoint_id" not in state.config["configurable"]:
            logger.info("No checkpoint found.")
            input_data = {
                **{self.input_data if self.input_data else {}},
                "messages": [{"role": "user", "content": query}],
            }
        else:
            logger.info("Checkpoint found.")
            input_data = {"messages": [{"role": "user", "content": query}]}

        message_ids: Set[str] = set()

        async for event in self.graph.astream(input_data, config, stream_mode="values"):
            message: AnyMessage = event["messages"][-1]

            if message.id in message_ids:
                continue

            logger.info(f"Message: {message.model_dump_json(indent=4)}")
            message_ids.add(message.id)

            if isinstance(message, AIMessage):
                await self._handle_ai_message(message, task, task_updater)
            elif isinstance(message, ToolMessage):
                await self._handle_tool_message(message, task, task_updater)

        await self._handle_structured_response(config, event_queue, task, task_updater)

    async def _handle_ai_message(
        self, message: AIMessage, task: Task, task_updater: TaskUpdater
    ) -> None:
        """Handles AIMessage from the graph stream.

        Sends text content as agent messages and processes any tool calls.

        Args:
            message: The AIMessage from the LangGraph stream.
            task: The current task.
            task_updater: The TaskUpdater for sending updates.
        """
        content: str | List[str | Dict] = message.content

        if isinstance(content, str) and content:
            await task_updater.update_status(
                TaskState.working, new_agent_text_message(content, task.context_id, task.id)
            )
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    await task_updater.update_status(
                        TaskState.working,
                        new_agent_text_message(item, task.context_id, task.id),
                    )
                elif isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                    await task_updater.update_status(
                        TaskState.working,
                        new_agent_text_message(item["text"], task.context_id, task.id),
                    )

        if message.tool_calls:
            for tool_call in message.tool_calls:
                await self._handle_tool_call(tool_call, task, task_updater)

    async def _handle_tool_call(
        self, tool_call: ToolCall, task: Task, task_updater: TaskUpdater
    ) -> None:
        """Handles a ToolCall from an AIMessage.

        Creates and sends a 'tool-call' message.

        Args:
            tool_call: The ToolCall object.
            task: The current task.
            task_updater: The TaskUpdater for sending updates.
        """
        message: Message = Message(
            context_id=task.context_id,
            message_id=str(uuid.uuid4()),
            parts=[DataPart(data=tool_call["args"])],
            metadata={
                "type": "tool-call",
                "toolCallId": tool_call["id"],
                "toolCallName": tool_call["name"],
            },
            role=Role.agent,
            task_id=task.id,
        )

        await task_updater.update_status(TaskState.working, message)

    async def _handle_tool_message(
        self, message: ToolMessage, task: Task, task_updater: TaskUpdater
    ) -> None:
        """Handles a ToolMessage from the graph stream.

        This message contains the result of a tool execution. It creates and sends
        a 'tool-call-result' message.

        Args:
            message: The ToolMessage from the LangGraph stream.
            task: The current task.
            task_updater: The TaskUpdater for sending updates.
        """
        tool_call_result_content: str | List[str | Dict] = message.content

        try:
            tool_call_result: str | Dict | List[str | Dict] = json.loads(tool_call_result_content)
            part: DataPart = DataPart(data=tool_call_result)
        except (json.JSONDecodeError, TypeError):
            tool_call_result: str = tool_call_result_content
            part: TextPart = TextPart(text=tool_call_result)

        message_2: Message = Message(
            context_id=task.context_id,
            message_id=str(uuid.uuid4()),
            parts=[part],
            metadata={
                "type": "tool-call-result",
                "toolCallId": message.tool_call_id,
                "toolCallName": message.name,
                **{"toolCallArtifact": message.artifact if message.artifact else None},
            },
            role=Role.agent,
            task_id=task.id,
        )

        await task_updater.update_status(TaskState.working, message_2)

    async def _handle_structured_response(
        self, config: RunnableConfig, event_queue: EventQueue, task: Task, task_updater: TaskUpdater
    ) -> None:
        """Handles the final structured response from the graph's state.

        After the graph has finished execution, this method extracts the final
        structured response, updates the task status, and may create an artifact.

        Args:
            config: The RunnableConfig used for the graph execution.
            event_queue: The event queue for sending updates.
            task: The current task.
            task_updater: The TaskUpdater for sending updates.

        Raises:
            Exception: If the graph state does not contain a 'structured_response'.
        """
        current_state: StateSnapshot = await self.graph.aget_state(config)
        structured_response: StructuredResponse | None = current_state.values.get(
            "structured_response"
        )

        if not structured_response:
            raise Exception(
                "No structured response. `graph` must have a `structured_response` state."
            )

        task_state: TaskState = TaskState(structured_response.task_state)

        if task_state != TaskState.completed:
            await task_updater.update_status(
                task_state,
                final=True,
            )
        else:
            await self._handle_structured_response_artifacts(
                structured_response.artifacts, event_queue, task
            )

            await task_updater.update_status(
                TaskState.completed,
                final=True,
            )

    async def _handle_structured_response_artifacts(
        self, artifacts: List[A2ANetArtifact], event_queue: EventQueue, task: Task
    ) -> None:
        """Creates and enqueues artifacts from the structured response.

        The artifacts can be either text or data artifacts.

        Args:
            artifacts: The artifacts from the structured response.
            event_queue: The event queue for sending updates.
            task: The current task.
        """
        for artifact in artifacts:
            artifact_2: Artifact = new_artifact(
                name=artifact.name,
                description=artifact.description,
                parts=[artifact.part],
            )

            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    artifact=artifact_2,
                    context_id=task.context_id,
                    task_id=task.id,
                )
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancels the agent execution.

        Note: This is not currently supported and will raise an exception.

        Args:
            context: The request context.
            event_queue: The event queue.

        Raises:
            Exception: Always, as this feature is not implemented.
        """
        raise Exception("Cancel not supported")
