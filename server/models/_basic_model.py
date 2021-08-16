from server.app import async_session as session

class BasicModel:

    async def _commit(self, session):
        try:
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            return False

    async def add(self):
        async with session() as s:
            s.add(self)
            return await self._commit(s)

    async def delete(self):
        async with session() as s:
            await s.delete(self)
            return await self._commit(s)
