import psycopg2
import uuid

def create_pgconnection():
    conn = psycopg2.connect(
        dbname = 'chatbot_db',
        user = 'admin',
        password = 'admin',
        # host = 'main_database',
        host = '52.36.218.103',
        port = '5432'
    )

    return conn

def init_db(conn):
    cur = conn.cursor()
    cur.execute("""
              CREATE TABLE IF NOT EXISTS chats (
                  chat_id TEXT PRIMARY KEY,
                  name TEXT
              )
          """)

    cur.execute("""
              CREATE TABLE IF NOT EXISTS messages (
                  message_id TEXT PRIMARY KEY,
                  chat_id TEXT,
                  sender TEXT,
                  content TEXT
              )
          """)
    conn.commit()

def create_new_chat(conn, chat_id, name, message_id,  first_message, sender):
    cur = conn.cursor()

    create_new_chat_query = """
        INSERT INTO chats (chat_id, name) Values (%s, %s)
    """

    create_first_message_query = """
        INSERT INTO messages (message_id, chat_id, sender, content) Values (%s,%s,%s,%s)
    """

    new_chat_data = (chat_id, name)
    first_message_data = (message_id, chat_id, sender, first_message)

    try:
        cur.execute(create_new_chat_query, new_chat_data)
        cur.execute(create_first_message_query, first_message_data)
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")



def insert_new_message(conn, message_id, chat_id, sender, content):
    cur = conn.cursor()

    create_new_message_query = """
            INSERT INTO messages (message_id, chat_id, sender, content) Values (%s,%s,%s,%s)
        """

    new_message_data = (message_id, chat_id, sender, content)

    try:
        cur.execute(create_new_message_query, new_message_data)
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

def update_chat_name(conn, chat_id, new_name):
    cur = conn.cursor()
    cur.execute("UPDATE chats SET name=%s WHERE chat_id=%s", (new_name, chat_id))
    conn.commit()

def retrieve_all_chats(conn):
    cur = conn.cursor()

    retrieve_all_chats_query = """
        SELECT * FROM chats
    """

    cur.execute(retrieve_all_chats_query)
    rows = cur.fetchall()
    all_chats = {}
    for chat_id, name in rows:
        cur.execute(
            "SELECT sender, content FROM messages WHERE chat_id= %s", (chat_id,)
        )
        message_rows = cur.fetchall()

        chat_history = []
        for sender, content in message_rows:
            chat_history.append({"role" : sender, "content" : content})

        all_chats[chat_id] = {"name": name, "chat_history": chat_history}

    return all_chats

def retrieve_all_messages(conn):
    cur = conn.cursor()

    retrieve_all_messages_query = """
           SELECT * FROM messages
       """

    cur.execute(retrieve_all_messages_query)
    rows = cur.fetchall()
    return rows



if __name__ == '__main__':
    # conn = create_pgconnection()
    # init_db(conn)
    pass