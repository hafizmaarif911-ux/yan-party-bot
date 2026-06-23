import aiosqlite

DB_NAME = "guild.db"

async def init_db():
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute("""
    CREATE TABLE IF NOT EXISTS contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_name TEXT,
        caller TEXT,
        leader_id INTEGER,
        total_members INTEGER,
        silver_bag INTEGER,
        item_value INTEGER,
        total_loot INTEGER,
        split_value INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id INTEGER,
        user_id INTEGER,
        username TEXT,
        role_name TEXT
    )
    """)

    await db.commit()
```

async def save_content(
content_name,
caller,
leader_id,
total_members,
silver_bag,
item_value,
total_loot,
split_value
):
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute("""
    INSERT INTO contents (
        content_name,
        caller,
        leader_id,
        total_members,
        silver_bag,
        item_value,
        total_loot,
        split_value
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        content_name,
        caller,
        leader_id,
        total_members,
        silver_bag,
        item_value,
        total_loot,
        split_value
    ))

    await db.commit()

    return cursor.lastrowid
```

async def save_attendance(
content_id,
user_id,
username,
role_name
):
async with aiosqlite.connect(DB_NAME) as db:

```
    await db.execute("""
    INSERT INTO attendance (
        content_id,
        user_id,
        username,
        role_name
    )
    VALUES (?, ?, ?, ?)
    """, (
        content_id,
        user_id,
        username,
        role_name
    ))

    await db.commit()
```

async def get_history(limit=10):
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute("""
    SELECT *
    FROM contents
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    return await cursor.fetchall()
```

async def get_content(content_id):
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute("""
    SELECT *
    FROM contents
    WHERE id = ?
    """, (content_id,))

    return await cursor.fetchone()
```

async def get_stats():
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute("""
    SELECT
        COUNT(*),
        COALESCE(SUM(total_loot), 0),
        COALESCE(SUM(silver_bag), 0),
        COALESCE(SUM(item_value), 0)
    FROM contents
    """)

    return await cursor.fetchone()
```

async def get_top_attendance(limit=10):
async with aiosqlite.connect(DB_NAME) as db:

```
    cursor = await db.execute("""
    SELECT
        username,
        COUNT(*) as total
    FROM attendance
    GROUP BY username
    ORDER BY total DESC
    LIMIT ?
    """, (limit,))

    return await cursor.fetchall()
```
