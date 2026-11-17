import sqlite3
import datetime
from dotenv import load_dotenv


class Task:
     def __init__(self,name,state,deadline,id=None):
          
          self.name=name
          self.state=state
          self.deadline=deadline
          self.id=id

class TaskRepository:
     def __init__(self,db_name):
         self.conn = sqlite3.connect(db_name,check_same_thread=False)
         self.cursor = self.conn.cursor()

         self.cursor.execute ("""
            CREATE TABLE IF NOT EXISTS task_table(
                id integer primary key autoincrement,
                name text,
                state text,
                deadline text
             )
         """)
         #print("動作確認")
     def close(self):
          self.conn.close()

     def add(self,task):
         sql='insert into task_table (name,state,deadline) values(?,?,?)'
         self.cursor.execute(sql,(task.name,task.state,task.deadline))
         self.conn.commit()

         new_task_id=self.cursor.lastrowid
         return new_task_id  

     def get_all(self):       
            
         self.cursor.execute('select*from task_table')
         return self._rows_to_tasks()
         

     def delete(self,delete_num):
          sql='delete from task_table where id=?'
          self.cursor.execute(sql,(delete_num,))
          self.conn.commit()
          return self.cursor.rowcount

     def get_incomplete(self):        
          self.cursor.execute('select* from task_table where state="未完了"')
          return self._rows_to_tasks()

     def get_overdue(self):
                 
          sql=("""select*from task_table
                    where deadline!=''
                    and deadline<date('now','localtime')
                    """)
          self.cursor.execute(sql)
          return self._rows_to_tasks()

     def _rows_to_tasks(self):
           task_line = self.cursor.fetchall()
           task_list=[]
           for line in task_line:
                    task_id,task_name,task_state,task_deadline=line
                    task=Task(task_name,task_state,task_deadline,task_id)
                    task_list.append(task)
           return task_list

     def get_by_id(self,task_id):
           sql =('select*from task_table where id =?')
           self.cursor.execute(sql,(task_id,)) 
           
           task=self._rows_to_tasks()

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

          self.cursor.execute(sql,(task_name,task_state,task_deadline,task_id))
          self.conn.commit()

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
          self.cursor.execute(sql)
          return self._rows_to_tasks()
     
     def get_due_today_incomplete(self,utc_day):
          sql=('''select *from task_table
                    where deadline!=''
                    and deadline=?
                    and state='未完了'
               ''')                  
          self.cursor.execute(sql,(utc_day,))
          return self._rows_to_tasks()
               



