import asyncio
from dataclasses import dataclass
from typing import Any, List, Optional

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    OpenAILLMContextAssistantTimestampFrame,
    FunctionCallsStartedFrame,
    FunctionCallInProgressFrame,
    FunctionCallResultFrame,
    FunctionCallResultProperties,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.services.llm_service import LLMService
from pipecat.services.llm_service import FunctionCallFromLLM


@dataclass
class SimulatedToolConfig:
    function_name: str
    tool_call_id_1: str
    tool_call_id_2: Optional[str] = None  # If provided, remains in-progress to simulate stall
    arguments_1: Optional[dict] = None
    arguments_2: Optional[dict] = None


class SimulatedLLMService(LLMService):
    """
    A deterministic LLM simulator to reproduce the failed flow:
    - Emits FunctionCallsStarted with two tool calls (id1, id2)
    - Emits InProgress for id1
    - Emits Result only for id1
    - Leaves id2 pending so assistant aggregator does NOT auto re-prompt

    Toggle `force_run_llm_after_result=True` to show the fixed behavior
    (i.e., properties.run_llm=True makes the aggregator re-prompt anyway).
    """

    def __init__(
        self,
        *,
        tool: SimulatedToolConfig,
        force_run_llm_after_result: bool = False,
        delay_s: float = 0.05,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._tool = tool
        self._force_run_llm = force_run_llm_after_result
        self._delay_s = delay_s
        self._has_run = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        context: Optional[OpenAILLMContext] = None
        if isinstance(frame, OpenAILLMContextFrame):
            context = frame.context

        if not context or self._has_run:
            # Pass-through any other frames
            await self.push_frame(frame, direction)
            return

        self._has_run = True
        logger.debug("SimulatedLLMService: starting simulated response")

        # Start of LLM response
        await self.push_frame(LLMFullResponseStartFrame())

        # Construct two function calls (second left in-progress to simulate stall)
        func_calls: List[FunctionCallFromLLM] = []

        func_calls.append(
            FunctionCallFromLLM(
                context=context,
                tool_call_id=self._tool.tool_call_id_1,
                function_name=self._tool.function_name,
                arguments=self._tool.arguments_1 or {},
            )
        )

        if self._tool.tool_call_id_2:
            func_calls.append(
                FunctionCallFromLLM(
                    context=context,
                    tool_call_id=self._tool.tool_call_id_2,
                    function_name=self._tool.function_name,
                    arguments=self._tool.arguments_2 or {},
                )
            )

        # Announce function calls started (downstream and upstream)
        started_down = FunctionCallsStartedFrame(function_calls=func_calls)
        started_up = FunctionCallsStartedFrame(function_calls=func_calls)
        await self.push_frame(started_down)
        await self.push_frame(started_up, FrameDirection.UPSTREAM)

        # Mark id1 as in-progress
        inprog_down = FunctionCallInProgressFrame(
            function_name=self._tool.function_name,
            tool_call_id=self._tool.tool_call_id_1,
            arguments=self._tool.arguments_1 or {},
            cancel_on_interruption=True,
        )
        inprog_up = FunctionCallInProgressFrame(
            function_name=self._tool.function_name,
            tool_call_id=self._tool.tool_call_id_1,
            arguments=self._tool.arguments_1 or {},
            cancel_on_interruption=True,
        )
        await self.push_frame(inprog_down)
        await self.push_frame(inprog_up, FrameDirection.UPSTREAM)

        # Simulate API latency
        await asyncio.sleep(self._delay_s)

        # Return result for id1 only
        properties = None
        if self._force_run_llm:
            properties = FunctionCallResultProperties(run_llm=True)

        result_payload: Any = {
            "status": "success",
            "data": "| date | available_slot | day |\n|:-----|:--------------|:----|\n| 4 Sep | two | Thu |\n| 4 Sep | three | Thu |",
        }

        res_down = FunctionCallResultFrame(
            function_name=self._tool.function_name,
            tool_call_id=self._tool.tool_call_id_1,
            arguments=self._tool.arguments_1 or {},
            result=result_payload,
            run_llm=None,  # leave None to rely on aggregator behavior
            properties=properties,
        )
        res_up = FunctionCallResultFrame(
            function_name=self._tool.function_name,
            tool_call_id=self._tool.tool_call_id_1,
            arguments=self._tool.arguments_1 or {},
            result=result_payload,
            run_llm=None,
            properties=properties,
        )

        await self.push_frame(res_down)
        await self.push_frame(res_up, FrameDirection.UPSTREAM)

        # End of LLM response chunk
        await self.push_frame(LLMFullResponseEndFrame())

        # Timestamp (mimic assistant timestamp frames)
        await self.push_frame(OpenAILLMContextAssistantTimestampFrame(), FrameDirection.UPSTREAM)
