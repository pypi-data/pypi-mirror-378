from __future__ import annotations
import asyncio, time
from dataclasses import dataclass, field  # ### NEW (field)
from typing import Any, Callable, Dict, Optional, List  # ### NEW (Optional, List)


# ---- request envelope --------------------------------------------------------
@dataclass
class _Req:
    payload: Any
    fut: asyncio.Future
    enq_ts: float = 0.0  # ### NEW (enqueue timestamp)
    ticket: int = 0  # ### NEW (monotonic queue ticket)
    meta: Dict[str, Any] = field(
        default_factory=dict
    )  # ### NEW (optional user/tenant info)


class AsyncMicroBatcher:
    def __init__(
        self,
        forward_fn: Callable[[list[Any]], "Any"],
        *,
        max_queue: int = 1024,
        max_batch: int = 8,
        max_latency_ms: int = 5,
        name: str = "default",  # ### NEW (for telemetry/UI)
    ) -> None:
        self.name = name  # ### NEW
        self._q: asyncio.Queue[_Req] = asyncio.Queue(maxsize=max_queue)
        self._forward = forward_fn
        self._max_batch = max_batch
        self._window = max_latency_ms / 1000.0
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

        # --- Telemetry fields ---
        self._total_requests = 0
        self._total_batches = 0
        self._last_batch_size: int | None = None
        self._last_flush_latency: float | None = None
        self._last_flush_time: float | None = None
        self._start_time = time.perf_counter()  # ### NEW (uptime)
        self._ticket_ctr = 0  # ### NEW
        self._last_avg_queue_wait: float | None = None  # ### NEW

    async def start(self) -> None:
        """Start the internal batching task."""
        if not self._task:
            self._task = asyncio.create_task(self._run())

    async def close(self) -> None:
        """Gracefully stop the batching loop."""
        self._stop.set()
        if self._task:
            await self._task

    async def submit(  # signature stays compatible
        self,
        payload: Any,
        *,
        timeout: float | None = None,
        meta: Optional[Dict[str, Any]] = None,  # ### NEW (optional)
    ) -> Any:
        """Submit a request payload and wait for the batched output."""
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._ticket_ctr += 1  # ### NEW
        req = _Req(  # ### NEW (enrich envelope)
            payload=payload,
            fut=fut,
            enq_ts=time.perf_counter(),
            ticket=self._ticket_ctr,
            meta=meta or {},
        )
        self._q.put_nowait(req)
        return await asyncio.wait_for(fut, timeout=timeout)

    # --- Lightweight queue snapshot for UI -----------------------------------
    def pending_snapshot(self, limit: int = 200) -> List[Dict[str, Any]]:  # ### NEW
        """
        Non-blocking view of the waiting items (position, age, meta).
        Uses the queue's internal deque for a read-only snapshot.
        """
        raw = list(getattr(self._q, "_queue", []))[:limit]
        now = time.perf_counter()
        out: List[Dict[str, Any]] = []
        for pos, r in enumerate(raw, start=1):
            out.append(
                {
                    "ticket": r.ticket,
                    "position": pos,
                    "age_sec": round(now - r.enq_ts, 6),
                    "meta": r.meta,
                }
            )
        return out

    async def _run(self) -> None:
        """Internal batching loop."""
        while not self._stop.is_set():
            try:
                first = await asyncio.wait_for(self._q.get(), timeout=0.01)
            except asyncio.TimeoutError:
                continue

            batch = [first]
            deadline = time.perf_counter() + self._window

            while len(batch) < self._max_batch:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    break
                try:
                    nxt = await asyncio.wait_for(self._q.get(), timeout=remaining)
                    batch.append(nxt)
                except asyncio.TimeoutError:
                    break

            t0 = time.perf_counter()
            try:
                outs = self._forward([r.payload for r in batch])
                if asyncio.iscoroutine(outs):
                    outs = await outs
                assert len(outs) == len(batch), "forward returned mismatched outputs"
            except Exception as e:
                for r in batch:
                    if not r.fut.done():
                        r.fut.set_exception(e)
            else:
                for r, out in zip(batch, outs):
                    if not r.fut.done():
                        r.fut.set_result(out)
            t1 = time.perf_counter()

            # --- Update telemetry ---
            self._total_batches += 1
            self._total_requests += len(batch)
            self._last_batch_size = len(batch)
            self._last_flush_latency = round(t1 - t0, 6)
            self._last_flush_time = t1
            waits = [t0 - r.enq_ts for r in batch]  # ### NEW
            if waits:
                self._last_avg_queue_wait = round(sum(waits) / len(waits), 6)  # ### NEW

    # --- Telemetry API ---
    def stats(self) -> Dict[str, Any]:
        """Return current telemetry stats as a dict."""
        return {
            "name": self.name,  # ### NEW
            "uptime_sec": round(time.perf_counter() - self._start_time, 3),  # ### NEW
            "total_requests": self._total_requests,
            "total_batches": self._total_batches,
            "last_batch_size": self._last_batch_size,
            "last_flush_latency_sec": self._last_flush_latency,
            "last_avg_queue_wait_sec": self._last_avg_queue_wait,  # ### NEW
            "last_flush_time": self._last_flush_time,
            "pending": self._q.qsize(),
            "max_batch": self._max_batch,
            "max_latency_ms": int(self._window * 1000),
        }
