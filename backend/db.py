import sqlite3

conn = sqlite3.connect("video_srts.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS video_transcripts (
        video_hash TEXT PRIMARY KEY,
        srt_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)  # Execute the CREATE TABLE statement
conn.commit()


def store_srt(video_hash, srt_data):
    cursor.execute(
        "INSERT INTO video_transcripts (video_hash, srt_data) VALUES (?, ?)",
        (video_hash, srt_data),
    )
    conn.commit()


def get_srt_by_hash(video_hash):
    cursor.execute(
        "SELECT srt_data FROM video_transcripts WHERE video_hash = ?", (video_hash,)
    )
    result = cursor.fetchone()  # Fetch the first (and hopefully only) matching row
    if result:
        return result[0]  # Return the SRT data if found
    else:
        return None  # if no matching hash found


# Example code

video_hash = "example_video_12345"  # placeholder val for hash
with open("example.srt", "r") as srt_file:
    srt_data = srt_file.read()

store_srt(video_hash, srt_data)

retrieved_srt = get_srt_by_hash(video_hash)

if retrieved_srt == srt_data:
    print("Database storage and retrieval successful!")
else:
    print("Error: Stored and retrieved SRT data do not match.")

# Close the database
conn.close()
