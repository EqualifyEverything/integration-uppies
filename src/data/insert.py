import time
import json
import traceback
from data.access import connection
from utils.watch import logger
from psycopg2.pool import SimpleConnectionPool

# Set use_pooling to True to enable connection pooling
use_pooling = True

# Connection pool
pool = None

if use_pooling:
    conn_params = connection().get_connection_params()
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        **conn_params
    )


def connection_pooling():
    return pool.getconn()


def release_pooling(conn):
    pool.putconn(conn)

# Normal Insert


def execute_insert(query, params):
    # Connect to the database
    if use_pooling:
        conn = connection_pooling()
    else:
        conn = connection()
        conn.open()
        logger.debug("🗄️✏️ Database connection opened")

    # Create a cursor
    cur = conn.cursor()
    rows_affected = 0
    try:
        # Execute the query
        with conn:
            cur.execute(query, params)
            rows_affected = cur.rowcount  # Get the number of rows affected
            logger.debug("🗄️✏️🟢 Query executed and committed")
    except Exception as e:
        logger.error(f'🗄️✏️ Error executing insert query: {e}\n{traceback.format_exc()}')
        logger.error(f'🗄️✏️ Failed query: {query}')
        logger.error(f'🗄️✏️ Failed query parameters: {params}')

    # Close the cursor and connection
    cur.close()
    if use_pooling:
        release_pooling(conn)
    else:
        conn.close()
        logger.debug("🗄️✏️ Cursor and connection closed")

    return rows_affected


# # # # # # # # # #

# Bulk Inserts


def execute_bulk_insert(query, params_list):
    # Connect to the database
    if use_pooling:
        conn = connection_pooling()
    else:
        conn = connection()
        conn.open()

    # Create a cursor
    cur = conn.cursor()
    rows_affected = 0
    try:
        # Execute the query
        with conn:
            cur.executemany(query, params_list)
            rows_affected = cur.rowcount  # Get the number of rows affected
            logger.debug("🗄️✏️🟢 Query executed and committed")
    except Exception as e:
        logger.error(f"🗄️✏️ Error executing bulk insert query: {e}\n{traceback.format_exc()}")
        logger.error(f"🗄️✏️ Failed query: {query}")
        logger.error(f"🗄️✏️ Failed query parameters: {params_list}")

    # Close the cursor and connection
    cur.close()
    if use_pooling:
        release_pooling(conn)
    else:
        conn.close()

    return rows_affected


# # # # # # # # # #
# Queries

# Record Uppies Header Responses
def record_uppies(uppies_responses):
    url_id, data = uppies_responses
    status_code = data['status_code']
    content_type = data['content_type']
    response_time = data['response_time']
    charset = data['charset'] if data['charset'] else None
    page_last_modified = data['page_last_modified'] if data['page_last_modified'] else None
    content_length = data['content_length'] if data['content_length'] else None
    server = data['server'] if data['server'] else None
    x_powered_by = data['x_powered_by'] if data['x_powered_by'] else None
    x_content_type_options = data['x_content_type_options'] if data['x_content_type_options'] else None
    x_frame_options = data['x_frame_options'] if data['x_frame_options'] else None
    x_xss_protection = data['x_xss_protection'] if data['x_xss_protection'] else None
    content_security_policy = data['content_security_policy'] if data['content_security_policy'] else None
    strict_transport_security = data['strict_transport_security'] if data['strict_transport_security'] else None
    etag = data['etag'] if data['etag'] else None

    query = """
        INSERT INTO results.scan_uppies (
            url_id, status_code, content_type, response_time, charset,
            page_last_modified, content_length, server, x_powered_by,
            x_content_type_options, x_frame_options, x_xss_protection,
            content_security_policy, strict_transport_security, etag
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        url_id, status_code, content_type, response_time, charset,
        page_last_modified, content_length, server, x_powered_by,
        x_content_type_options, x_frame_options, x_xss_protection,
        content_security_policy, strict_transport_security, etag
    )

    rows_affected = execute_insert(query, params)

    if rows_affected == 1:
        logger.debug(f'Insert: 🟢 New Record Added for {url_id}')
    else:
        logger.error(f'Insert: Problem adding record. Values: {params}')
        time.sleep(5)

# End Uppies Header Responses
