from server.app import async_session as session


class BasicModel:

    async def _commit(self):
        async with session() as s:
            try:
                await s.commit()
            except Exception as e:
                await s.rollback()
                print(e)
                return False

        return True

    async def add(self):
        async with session() as s:
            s.add(self)

        return await self._commit()

    async def delete(self):
        async with session() as s:
            await s.delete(self)

        return await self._commit()
