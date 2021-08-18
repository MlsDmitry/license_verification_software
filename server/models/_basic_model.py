
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

    async def update(self, data):
        from server.models import User
        async with session() as s:
            user_copy = User(
                self.name,
                self.email,
                self.sid,
                self.salt,
                self.encrypted_license_key,
                self.suspended)
            user_copy.created_date = self.created_date
            
            await self.delete()
            
            for key in data:
                if key == 'suspended':
                    setattr(user_copy, key, data[key] == 'true')
                else:
                    setattr(user_copy, key, data[key])
            
            await user_copy.add()
            
            return await self._commit(s)
