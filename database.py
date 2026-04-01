import aiosqlite

DB_NAME = "barber.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            master TEXT,
            service TEXT,
            date TEXT,
            time TEXT
        )
        """)
        await db.commit()

async def get_user_bookings(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, master, service, date, time FROM bookings WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchall()

async def add_booking(user_id, master, service, date, time):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO bookings (user_id, master, service, date, time)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, master, service, date, time))
        await db.commit()

async def delete_booking_by_id(booking_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM bookings WHERE id = ?",
            (booking_id,)
        )
        await db.commit()


async def get_booked_times(date, master):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT time FROM bookings WHERE date = ? AND master = ?",
            (date, master)
        )
        return [r[0] for r in await cursor.fetchall()]


async def get_all_bookings():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT user_id, master, service, date, time
        FROM bookings
        ORDER BY date ASC, time ASC
        """)
        return await cursor.fetchall()

async def delete_booking(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM bookings WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_bookings_by_date(date):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT user_id, master, service, date, time
        FROM bookings
        WHERE date = ?
        ORDER BY time
        """, (date,))
        return await cursor.fetchall()