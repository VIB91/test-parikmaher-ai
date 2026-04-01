from database import get_booked_times

WORK_HOURS = range(10, 20)


async def get_free_slots(date, master):
    booked = await get_booked_times(date, master)

    slots = []
    for h in WORK_HOURS:
        t = f"{h}:00"
        if t not in booked:
            slots.append(t)

    return slots