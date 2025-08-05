# import mysql.connector
# import streamlit as st

# class DBManager:
#     def __init__(self):
#         config = {
#             "host": st.secrets["mysql"]["host"],
#             "user": st.secrets["mysql"]["user"],
#             "password": st.secrets["mysql"]["password"],
#             "database": st.secrets["mysql"]["database"],
#             "port": int(st.secrets["mysql"].get("port", 3306)),
#         }
#         self.conn = mysql.connector.connect(**config)
#         self.cur = self.conn.cursor(dictionary=True)

#     def query(self, sql, params=None):
#         self.cur.execute(sql, params or ())
#         return self.cur.fetchall()

#     def execute(self, sql, params=None):
#         self.cur.execute(sql, params or ())
#         self.conn.commit()

#     def close(self):
#         self.cur.close()
#         self.conn.close()
