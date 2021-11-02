import asyncio
import math
import moteus
import signal


# define a function on how to exit safely:
# mainly needed to run await c.set_stop() to stop the motor when Ctrl-C is pressed
async def shutdown(signal, loop, c):

        print("SIGNAL DETECTED: " + signal.name)

        await c.set_stop()

        # prevent other tasks from respawning
        tasks = [task for task in asyncio.all_tasks() if task is not
             asyncio.current_task()]
        [t.cancel() for t in tasks]

        await asyncio.gather(*tasks, return_exceptions=True)

        loop.stop()


# this is the main function, as per simple.py
# just needed to pass in the moteus.Controller() object
async def main(c):
    # see simple.py documentation on how this function works
    await c.set_stop()

    while True:
        state = await c.set_position(position=math.nan, query=True)
        print(state)

        print("Position: ", state.values[moteus.Register.POSITION])

        print()

        await asyncio.sleep(0.02)

if __name__ == '__main__':

    # create the controller
    c = moteus.Controller()

    # start an event loop
    loop = asyncio.get_event_loop()

    # specify which signals we want to handle
    signals = (signal.SIGINT, )

    # create a shutdown task for each of these signals
    for s in signals:
        loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(s, loop,c)))
    

    # start the main loop
    # it runs `finally` if any of the signals were detected
    try:
        loop.create_task(main(c))
        loop.run_forever()
    finally:
        loop.close()
        print("DONE")

