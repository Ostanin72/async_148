import asyncio
import datetime
import json
from itertools import batched

from aiohttp import ClientSession

from db import DbSession, Swapi, close_orm, create_orm

MAX_CONCURRENCY = 5


async def get_people(http_session: ClientSession, person_id: int):
    response = await http_session.get(
        f"https://swapi-node.vercel.app/api/people/{person_id}/"
    )
    json_data = await response.json()
    return json_data


async def insert_people(people_jons: list[dict]):
    async with DbSession() as db_session:
        # for person in people_jons:
        #     swapi = Swapi(json=person)
        #     db_session.add(swapi)
        people_orm = [Swapi(json=person) for person in people_jons]
        db_session.add_all(people_orm)
        await db_session.commit()


async def main():
    await create_orm()
    async with ClientSession() as http_session:

        for i_batch in batched(range(1, 101), MAX_CONCURRENCY):
            # coros = []
            # for i in i_batch:
            #     coro = get_people(http_session, i)
            #     coros.append(coro)
            coros = [get_people(http_session, i) for i in i_batch]
            result = await asyncio.gather(*coros)
            insert_people_coro = insert_people(result)
            insert_people_task = asyncio.create_task(insert_people_coro)
    tasks = asyncio.all_tasks()
    current_task = asyncio.current_task()
    tasks.remove(current_task)
    for task in tasks:
        await task
    await close_orm()


start = datetime.datetime.now()
coro_main = main()
asyncio.run(coro_main)
end = datetime.datetime.now()
print(end - start)
