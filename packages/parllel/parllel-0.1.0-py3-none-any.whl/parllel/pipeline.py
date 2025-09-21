from __future__ import annotations

import asyncio
from asyncio import Queue, shield
from typing import Any, Iterator

from .async_util import SENTINEL
from .stage import Stage
from .util import Err, Result, is_err, unwrap

class Pipeline:
    
    '''
    async pipeline
    '''

    def __init__(self, gen: Iterator[Any], log: bool = False) -> None:
        self.log = log
        self.generator: Iterator[Any] | None = None
        self.stages: list[Stage] = []
        self.result: Result = "ok"
        self.gen(gen)

    def gen(self, gen: Iterator[Any]) -> "Pipeline":
        self.generator = gen
        return self
    
    def stage(self, st: Stage) -> "Pipeline":
        if len(st.functions) > 0:
            self.stages.append(st)
        return self
    
    def __rshift__(self, other: Stage) -> "Pipeline":
        self.stage(other)
        return self

    def __generate(self, gen: Iterator[Any]) -> asyncio.Queue[Any]:
        outbound: asyncio.Queue[Any] = asyncio.Queue(maxsize=1)

        async def run() -> None:
            try:
                for result in gen:
                    if is_err(result):
                        self.__handle_err(str(result))
                        self.__handle_log(result)
                        return                        # sentinel sent in finally
                    await outbound.put(unwrap(result))
            except asyncio.CancelledError:
                # allow task cancellation to propagate; finally still runs
                raise
            except Exception as e:
                # real error from iterator or unwrap()
                self.__handle_err(str(e))
                self.__handle_log(e)
            finally:
                # guarantee exactly-once termination signal
                try:
                    await shield(outbound.put(SENTINEL))
                except Exception:
                    pass

        asyncio.create_task(run())
        return outbound
    
    def __handle_log(self, val: Any) -> None:
        if self.log:
            print(val)
    
    def __handle_err(self, err: str) -> None:
        self.result = Err(err)

    async def __drain(self, q: Queue[Any]) -> None:
        while True:
            val = await q.get()
            if val is SENTINEL:
                break
            self.__handle_log(val)
            
    async def run(self) -> Result:

        if not self.generator:
            err = Err("no generator")
            self.__handle_err(err.message)
            self.__handle_log(err.message)
            return err
        
        stream = self.__generate(self.generator)
        for stage in self.stages:
            stream = stage.run(stream)
        await self.__drain(stream)
        return self.result
