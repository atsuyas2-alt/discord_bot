import sqlite3
import datetime
from dotenv import load_dotenv
import os
import libsql_client

load_dotenv()
db_url = os.getenv("TURSO_DATABASE_URL")
db_token = os.getenv("TURSO_AUTH_TOKEN")


class Task:
     def __init__(self,name,state,deadline,id=None):
          
          self.name=name
          self.state=state
          self.deadline=deadline
          self.id=id

class TaskRepository:
     def __init__(self,db_name):
     #     self.conn = sqlite3.connect(db_name,check_same_thread=False)
     #     self.client = self.conn.client()
          self.client = libsql_client.create_client_sync(
          url=db_url,
          auth_token=db_token
          )

          self.client.execute ("""
               CREATE TABLE IF NOT EXISTS task_table(
                    id integer primary key autoincrement,
                    name text,
                    state text,
                    deadline text
               )
          """)
         #print("動作確認")
     def close(self):
          self.client.close()

     def add(self,task):
         sql='insert into task_table (name,state,deadline) values(?,?,?)'
         result=self.client.execute(sql,[task.name,task.state,task.deadline])

         return result.last_insert_rowid 

     def get_all(self):       
            
         result=self.client.execute('select*from task_table')
         return self._fetch_tasks(result.rows)
         

     def delete(self,delete_num):
          sql='delete from task_table where id=?'
          result=self.client.execute(sql,[delete_num,])
          return result.rows_affected

     def get_incomplete(self):        
          
          return self._fetch_tasks(('select* from task_table where state="未完了"'))

     def get_overdue(self):
                 
          sql=("""select*from task_table
                    where deadline!=''
                    and deadline<date('now','localtime')
                    """)
          self.client.execute(sql)
          return self._fetch_tasks(sql)

     def _rows_to_tasks(self,task_line):
           
           task_list=[]
           for line in task_line:
                    task_id,task_name,task_state,task_deadline=line
                    task=Task(task_name,task_state,task_deadline,task_id)
                    task_list.append(task)
           return task_list

     def _fetch_tasks(self,sql,params=None):
          result=self.client.execute(sql,params or [])
          return self._rows_to_tasks(result.rows)

     def get_by_id(self,task_id):
           sql =('select*from task_table where id =?')
        
           task=self._fetch_tasks(sql,[task_id])

           if task:
               return task[0]
           else:
               return 

     def update(self,task):
          task_name=task.name
          task_state=task.state
          task_deadline=task.deadline
          task_id=task.id

          sql=('''update task_table
               set name=?,state=?,deadline=?
               where id =?''')

          self.client.execute(sql,[task_name,task_state,task_deadline,task_id])
          

     def _check_date(self,task_deadline):
          task_deadline_date=task_deadline

          task_deadline_datetime=datetime.datetime.strptime(task_deadline,'%Y-%m-%d')
          task_deadline_date=task_deadline_datetime.strftime('%Y-%m-%d')  

          return task_deadline_date

     def get_overdue_incomplete(self):
          sql=('''select *from task_table
                    where deadline!=''
                    and deadline<date('now','localtime')
                    and state='未完了'
               ''')                  
          
          return self._fetch_tasks(sql)
     
     def get_due_today_incomplete(self,utc_day):
          sql=('''select *from task_table
                    where deadline!=''
                    and deadline=?
                    and state='未完了'
               ''')                  
          
          return self._fetch_tasks(sql,(utc_day,))




