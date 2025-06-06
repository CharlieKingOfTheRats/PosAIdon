# ======= In Terminal: Step 1 - Install SQLite =======
sudo apt update
sudo apt install sqlite3

# Verify installation:
sqlite3 --version


# ======= In Terminal: Step 2 - Create a New SQLite Database =======
sqlite3 ~/mydatabase.db

# This opens the SQLite prompt:
# SQLite version 3.31.1 ...
# Enter ".help" for usage hints.
# sqlite>

# ======= In SQLite prompt: Step 3 - Create a Table =======
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    content TEXT,
    page INTEGER,
    title TEXT,
    chapter TEXT
);

# Verify tables:
.tables


# ======= In SQLite prompt: Step 4 - Insert Sample Data =======
INSERT INTO chunks (content, page, title, chapter)
VALUES ('This is a test chunk of text.', 1, 'My Book', 'Intro');

# Check inserted data:
SELECT * FROM chunks;

# To exit SQLite prompt:
.quit


# ======= In Terminal: Step 5 - Check SQLite Python Library =======
python3 -c "import sqlite3; print('SQLite is ready!')"


# ======= In Python script or interactive shell: Step 5 - Use SQLite DB with Python =======
import sqlite3

# Connect to the database (change path if needed)
conn = sqlite3.connect('mydatabase.db')

cursor = conn.cursor()

# Fetch all rows from the chunks table
rows = cursor.execute("SELECT * FROM chunks").fetchall()

for row in rows:
    print(row)

conn.close()


# ======= Notes on using a USB drive for the database file =======
# Example of opening the database file on a USB drive:
# In terminal:
sqlite3 /media/yourname/FLASHDRIVE/mydatabase.db

# In Python:
conn = sqlite3.connect('/media/yourname/FLASHDRIVE/mydatabase.db')