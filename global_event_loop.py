import asyncio


def push_async_task(callback_func, run_func, *args, **kwargs) -> asyncio.Task:
    if not run_func:
        raise ValueError("Don't set run function correctly!")
    task: asyncio.Task = asyncio.ensure_future(
        run_func(*args, **kwargs),
        loop=global_ev_loop
    )
    if callback_func:
        task.add_done_callback(callback_func)
    return task


global_ev_loop = asyncio.get_event_loop()


if __name__ == '__main__':
    def callback_test(future: asyncio.Future):
        print(str(future.result()))


    async def coro_test(msg):
        print("coro_test begin: {}".format(msg))
        await asyncio.sleep(5)
        print("coro_test end")
        return msg + " done"


    async def coro_test1(msg):
        print("coro_test1 begin: {}".format(msg))
        await asyncio.sleep(1)
        print("coro_test1 end")
        return msg + " done"

    push_async_task(callback_test, coro_test, " i am test")
    push_async_task(callback_test, coro_test1, " i am test1")
    push_async_task(None, coro_test1, " i am test2")
    push_async_task(None, None, " i am test2")
    push_async_task(None, None, None)
    global_ev_loop.run_forever()
