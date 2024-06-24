from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector as mysql

################BACKEND######################

#creating treeview refresh

def refresh_treeview():
    for item in tree.get_children():    #to prevent duplicate entry if refresh_treeview is added twice in code [not mandatory]
        tree.delete(item)
    records=run_query("select * from students;")    #this is student's rows
    for record in records:
        tree.insert('',END,values=record)

def run_query(query,parameter=()):#parameter=() because when we pass command of sql, we use 'name=%s',(name,)[this name, is tuple]
    conn=mysql.connect(db="learn",user="root",host='localhost', password='root')
    cur=conn.cursor()
    query_result=None#as no query passes
    try:        #using try except block so that even if query fails, program don't crash
        cur.execute(query,parameter)
        if query.lower().startswith("select"):  #query.lower() converts string to lowercase and .startswith() is a function to check for with what string word/object start
            query_result=cur.fetchall()
        conn.commit()
    except mysql.Error as e:    #.Error as e: This exception is the base class for all other exceptions in the errors module.
        messagebox.showerror("Database Error",str(e))
    finally:        #finally block is always executed after leaving the try statement
        cur.close()
        conn.close()
    return query_result     #returning query which is being executed
        
def insert_data():
    query="insert into students(name,address,age,number) values(%s,%s,%s,%s);"
    parameters=(name_entry.get(),address_entry.get(),age_entry.get(),number_entry.get())
    run_query(query,parameters)
    messagebox.showinfo("Information", "Data has been added successfully!")
    refresh_treeview()  #for getting recently added data into treeview

def delete_data():
    selection_item=tree.selection()[0]  #getting selection item of treeview
    student_id=tree.item(selection_item)["values"][0]     #selecting id of student, id of student which is being selected by user in treeview
    query="delete from students where student_id=%s"
    parameters=(student_id,)
    run_query(query,parameters)
    messagebox.showinfo("Information","Data Deleted successfully!")
    refresh_treeview()

def update_data():
    selection_item=tree.selection()[0]
    student_id=tree.item(selection_item)["values"][0]
    query="update students set name=%s,address=%s,age=%s,number=%s where student_id=%s"
    parameters=(name_entry.get(),address_entry.get(),age_entry.get(),number_entry.get(),student_id)
    run_query(query,parameters)
    messagebox.showinfo("Information","Data updated successfully!")
    refresh_treeview()

def create_table():
    query="create table if not exists students(student_id serial primary key,name char(100),address char(100),age int, number ints);"
    run_query(query)
    messagebox.showinfo("Information","Table Created successfully!")
    refresh_treeview()

############Backend- Finished#########################


###############FRONT-END###############################
root=Tk()
root.title("Student Management System")
frame=LabelFrame(root,text="Student Data")
frame.grid(row=0,column=0, padx=10, pady=10, sticky="ew")#sticky sets alignment of text and ew means eastwest, means the text will be stretched from left to right

Label(frame, text="Student Name: ").grid(row=0, column=0,padx=2, pady=2,sticky='w')#why not root, because we have already added a frame on root window, so we will now add widgets onto that frame.
name_entry= Entry(frame)
name_entry.grid(row=0, column=1,padx=2,pady=2,sticky="ew")#column=1 as we want entry be at side of label

Label(frame, text="Address: ").grid(row=1, column=0,padx=2, pady=2,sticky='w')
address_entry= Entry(frame)
address_entry.grid(row=1, column=1,padx=2,pady=2,sticky="ew")

Label(frame, text="Age: ").grid(row=2, column=0,padx=2, pady=2,sticky='w')
age_entry= Entry(frame)
age_entry.grid(row=2, column=1,padx=2,pady=2,sticky="ew")

Label(frame, text="Phone Number: ").grid(row=3, column=0,padx=2, pady=2,sticky='w')
number_entry= Entry(frame)
number_entry.grid(row=3, column=1,padx=2,pady=2,sticky="ew")
#creating buttons
#first creating frame for button
button_frame=Frame(root)
button_frame.grid(row=1,column=0,pady=5,sticky="ew")

#adding button

Button(button_frame,text="Add Data",command=insert_data).grid(row=0,column=0,padx=5)
Button(button_frame,text="Delete Data",command=delete_data).grid(row=0,column=1,padx=5)
Button(button_frame,text="Update Data",command=update_data).grid(row=0,column=2,padx=5)
Button(button_frame,text="Create Table",command=create_table).grid(row=0,column=3,padx=5)

#creating tree-view
#tree view=Treeview. The ttk.Treeview widget displays a hierarchical collection of items. 
#Each item has a textual label, an optional image, and an optional list of data values. 
#The data values are displayed in successive columns after the tree label.
tree_frame=Frame(root)
tree_frame.grid(row=2,column=0,padx=10,sticky="nsew")#nsew=northsoutheastwest

#creating scrollbar
tree_scroll=Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT,fill=Y)#fill means, where that scroll bar has to span, side= specifying which side of window

#adding tree view
tree=ttk.Treeview(tree_frame,yscrollcommand=tree_scroll.set,selectmode="browse")#yscrollcommand, is used to connect scroll bar and tree_scroll is which scroll bar is being connected
#.set is used to get position on scroll bar with respect to tree view
#,selectmode="browse" lets you allows selecting one entry at a time


tree_scroll.config(command=tree.yview)#for updating tree view values after scrolling

#configuring column

tree["columns"]=('Student_id','Name','Address','Age','Number')
tree.column("#0",width=0,stretch=0)# column("#0",width=0,stretch=0) means column 0 is being made invisible
tree.column("Student_id",anchor=CENTER,width=80)
tree.column("Name",anchor=CENTER,width=120)
tree.column("Address",anchor=CENTER,width=120)
tree.column("Age",anchor=CENTER,width=50)
tree.column("Number",anchor=CENTER,width=120)

tree.heading('Student_id',text='ID',anchor=CENTER)
tree.heading('Name',text='Name',anchor=CENTER)
tree.heading('Address',text='Address',anchor=CENTER)
tree.heading('Age',text='Age',anchor=CENTER)
tree.heading('Number',text='Phone Number',anchor=CENTER)

tree.pack()

refresh_treeview()

root.mainloop()
###############FRONTEND-finished########################