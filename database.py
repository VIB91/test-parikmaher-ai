import aiosqlite
from datetime import datetime, timedelta

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
            time TEXT,
            reminded INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS deleted_bookings (
            id INTEGER,
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
            "SELECT id, master, service, date, time FROM bookings WHERE user_id = ? ORDER BY date, time",
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
        SELECT id, user_id, master, service, date, time
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
        SELECT id, user_id, master, service, date, time
        FROM bookings
        WHERE date = ?
        ORDER BY time
        """, (date,))
        return await cursor.fetchall()

async def admin_delete_booking(booking_id):
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись
        cursor = await db.execute(
            "SELECT * FROM bookings WHERE id = ?",
            (booking_id,)
        )
        booking = await cursor.fetchone()

        if booking:
            # Сохраняем в deleted_bookings
            await db.execute("""
            INSERT INTO deleted_bookings (id, user_id, master, service, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
            """, booking[:6])

            # Удаляем из основной таблицы
            await db.execute(
                "DELETE FROM bookings WHERE id = ?",
                (booking_id,)
            )

            await db.commit()

async def save_deleted_booking(booking):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO deleted_bookings (id, user_id, master, service, date, time)
        VALUES (?, ?, ?, ?, ?, ?)
        """, booking[:6])
        await db.commit()

async def restore_booking(booking_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM deleted_bookings WHERE id = ?",
            (booking_id,)
        )
        booking = await cursor.fetchone()

        if booking:
            await db.execute("""
            INSERT INTO bookings (id, user_id, master, service, date, time, reminded)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """, booking)

            await db.execute(
                "DELETE FROM deleted_bookings WHERE id = ?",
                (booking_id,)
            )

            await db.commit()

async def get_deleted_bookings():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT id, user_id, master, service, date, time
        FROM deleted_bookings
        ORDER BY date, time
        """)
        return await cursor.fetchall()

# async def mark_notified(booking_id):
#     async with aiosqlite.connect(DB_NAME) as db:
#         await db.execute(
#             "UPDATE bookings SET notified = 1 WHERE id = ?",
#             (booking_id,)
#         )
#         await db.commit()

async def get_upcoming_bookings(days=3):
    """Берем все записи на ближайшие days дней, у которых reminded = 0"""
    now = datetime.now().date()
    max_date = now + timedelta(days=days)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, user_id, master, service, date, time FROM bookings "
            "WHERE reminded = 0 AND date BETWEEN ? AND ?",
            (now.strftime("%Y-%m-%d"), max_date.strftime("%Y-%m-%d"))
        )
        rows = await cursor.fetchall()
        return [
            {"id": r[0], "user_id": r[1], "master": r[2], "service": r[3], "date": r[4], "time": r[5]}
            for r in rows
        ]

async def mark_as_reminded(booking_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE bookings SET reminded = 1 WHERE id = ?", (booking_id,))
        await db.commit()