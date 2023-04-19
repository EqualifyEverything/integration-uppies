import psycopg2
import json
import traceback
from data.access import connection
from utils.watch import logger
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime, timezone

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

# Singular Updates

def execute_update(query, params=None, fetchone=True):
 #  logger.debug(f'🗄️   🔧 Executing query: {query}')
 #  logger.debug(f'🗄️   🔧 Query parameters: {params}... ')

   # Connect to the database
   conn = connection()
   conn.open()
   logger.debug(f'🗄️   🔧 Database connection opened')

   # Create a cursor
   cur = conn.conn.cursor()

   try:
      # Execute the query
      cur.execute(query, params)
      conn.conn.commit()
      logger.info(f'🗄️   🔧 Query executed and committed')

      # Fetch the results if requested
      result = None
      if fetchone:
            result = cur.fetchone() or ()  # return an empty tuple if None is returned
      else:
            result = cur.fetchall() or []  # return an empty list if None is returned
            logger.debug(f'🗄️   🔧 Fetched results: {result}')
   except Exception as e:
      #  logger.error(f'🗄️   🔧 Error executing update query: {e}')
        result = None

   # Close the cursor and connection
   cur.close()
   conn.close()
   logger.debug(f'🗄️   🔧 Cursor and connection closed')

   return result


# # # # # # # # # #

# Bulk Updates

def execute_bulk_update(query, params_list):
   # Connect to the database
   if use_pooling:
      conn = connection_pooling()
   else:
      conn = connection()
      conn.open()

   # Create a cursor
   cur = conn.cursor()

   try:
      # Execute the query
      with conn:
          cur.executemany(query, params_list)
          logger.info("🗄️✏️🟢 Query executed and committed")
   except Exception as e:
      logger.error(f"🗄️✏️ Error executing bulk insert query: {e}\n{traceback.format_exc()}")

   # Close the cursor and connection
   cur.close()
   if use_pooling:
      release_pooling(conn)
   else:
      conn.close()


   #########################################################
   ## Queries




def update_status_code(url_id, status_code):
       query = """
           UPDATE targets.urls
           SET uppies_code = %s, uppies_at = %s
           WHERE id = %s;
       """
       now = datetime.now(timezone.utc)
       params_list = [(status_code, now, url_id) for url_id, status_code in url_status_list]

       try:
           execute_update(query, params_list)
           for url_id, status_code in url_status_list:
               logger.debug(f'🗄️🔧 Updated status code for URL ID {url_id} to {status_code}')
       except Exception as e:
           logger.error(f'🗄️🔧 Failed to update status codes in bulk - Error: {e}')
