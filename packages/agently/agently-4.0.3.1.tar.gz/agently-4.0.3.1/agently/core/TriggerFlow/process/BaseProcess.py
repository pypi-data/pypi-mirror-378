# Copyright 2023-2025 AgentEra(Agently.Tech)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import uuid

from typing import Literal, TYPE_CHECKING


if TYPE_CHECKING:
    from agently.core.TriggerFlow import TriggerFlowBluePrint
    from agently.types.trigger_flow import TriggerFlowHandler, TriggerFlowEventData

from agently.core.TriggerFlow.Chunk import TriggerFlowChunk
from agently.types.data import EMPTY
from agently.types.trigger_flow import TriggerFlowBlockData


class TriggerFlowBaseProcess:
    def __init__(
        self,
        *,
        trigger_event: str,
        blue_print: "TriggerFlowBluePrint",
        block_data: "TriggerFlowBlockData",
        trigger_type: Literal["event", "runtime_data", "flow_data"] = "event",
        **options,
    ):
        self.trigger_event = trigger_event
        self.trigger_type: Literal["event", "runtime_data", "flow_data"] = trigger_type
        self._blue_print = blue_print
        self._block_data = block_data
        self._options = options

    def _new(
        self,
        trigger_event: str,
        blue_print: "TriggerFlowBluePrint",
        block_data: "TriggerFlowBlockData",
        trigger_type: Literal["event", "runtime_data", "flow_data"] = "event",
        **options,
    ):
        return type(self)(
            trigger_event=trigger_event,
            trigger_type=trigger_type,
            blue_print=blue_print,
            block_data=block_data,
            **options,
        )

    def when(
        self,
        target: str,
        *,
        type: Literal["event", "runtime_data", "flow_data"] = "event",
    ):
        return self._new(
            trigger_event=target,
            trigger_type=type,
            blue_print=self._blue_print,
            block_data=TriggerFlowBlockData(
                outer_block=None,
            ),
        )

    def when_event(self, event: str):
        return self.when(event, type="event")

    def when_runtime_data(self, key: str):
        return self.when(key, type="runtime_data")

    def when_flow_data(self, key: str):
        return self.when(key, type="flow_data")

    def to(self, chunk: "TriggerFlowChunk | TriggerFlowHandler | str", side_branch: bool = False):
        if isinstance(chunk, str):
            if chunk in self._blue_print.chunks:
                chunk = self._blue_print.chunks[chunk]
            else:
                raise NotImplementedError(f"Cannot find chunk named '{ chunk }'")
        chunk = TriggerFlowChunk(chunk) if callable(chunk) else chunk
        self._blue_print.add_handler(
            self.trigger_type,
            self.trigger_event,
            chunk.async_call,
        )
        return self._new(
            trigger_event=chunk.trigger if not side_branch else self.trigger_event,
            trigger_type=self.trigger_type,
            blue_print=self._blue_print,
            block_data=self._block_data,
            **self._options,
        )

    def side_branch(self, chunk: "TriggerFlowChunk | TriggerFlowHandler"):
        return self.to(chunk, side_branch=True)

    def batch(
        self,
        *chunks: "TriggerFlowChunk | TriggerFlowHandler",
        side_branch: bool = False,
    ):
        batch_trigger = f"Batch-{ uuid.uuid4().hex }"
        results = {}
        chunks_to_wait = {}

        async def wait_all_chunks(data: "TriggerFlowEventData"):
            if data.event in chunks_to_wait:
                results[data.event] = data.value
                chunks_to_wait[data.event] = True
            for done in chunks_to_wait.values():
                if done is False:
                    return
            await data.async_emit(batch_trigger, results)

        for chunk in chunks:
            chunk = TriggerFlowChunk(chunk) if callable(chunk) else chunk
            chunks_to_wait[chunk.name] = False
            self._blue_print.add_handler(
                self.trigger_type,
                self.trigger_event,
                chunk.async_call,
            )
            self._blue_print.add_event_handler(chunk.trigger, wait_all_chunks)

        return self._new(
            trigger_event=batch_trigger if not side_branch else self.trigger_event,
            blue_print=self._blue_print,
            block_data=self._block_data,
            **self._options,
        )

    def end(self):
        async def set_default_result(data: "TriggerFlowEventData"):
            result = data._system_runtime_data.get("$TF.result")
            if result is EMPTY:
                data._system_runtime_data.set("$TF.result", data.value)
            data._system_runtime_data.get("$TF.result_ready").set()

        return self.to(set_default_result)

    def ____(self, *args, **kwargs):
        """
        Separator for chain expression.
        Do nothing but return self.
        """
        return self
