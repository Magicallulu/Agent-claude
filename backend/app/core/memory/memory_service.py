import logging
import time

from app.core.memory.short_term import ShortTermMemory, TurnEntry
from app.core.memory.long_term import LongTermMemory
from app.core.memory.event_extractor import EventExtractor
from app.core.memory.memory_reader import MemoryReader, MemoryContext

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.event_extractor = EventExtractor()
        self.reader = MemoryReader()

    async def get_context(self, user_id: int, session_id: str, current_query: str) -> MemoryContext:
        return await self.reader.read(user_id, session_id, current_query)

    async def save_turn(
        self,
        user_id: int,
        session_id: str,
        user_message: str,
        assistant_response: str,
        intent: str,
    ) -> None:
        # event_extractor and long_term are used by the API layer via BackgroundTasks (Task 9)
        try:
            ts = time.time()
            entry = TurnEntry(role="user", content=user_message, intent=intent, timestamp=ts)
            await self.short_term.save(session_id, entry)
            entry_assistant = TurnEntry(role="assistant", content=assistant_response, intent=intent, timestamp=ts)
            await self.short_term.save(session_id, entry_assistant)
        except Exception:
            logger.warning("Failed to save turn", exc_info=True)
