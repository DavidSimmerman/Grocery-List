import os
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox
import sqlite3


# Added to make it easy to change colors
bg_color = "lightgray"

class ParentWindow(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Edit Database")
        
        
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        mp = MainPage(parent=container, controller=self)
        mp.grid(row=0, column=0, sticky='nsew')


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self,parent)

        con = sqlite3.connect('db_groceryList.db')
        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE if not exists tbl_foodList( \
                ID INTEGER PRIMARY KEY AUTOINCREMENT, \
                food_name TEXT, \
                food_image TEXT, \
                food_isle TEXT, \
                food_order INT, \
                food_selected BIT, \
                food_autoadd BIT \
                );")
            con.commit()
        con.close()

        lbl_food_name = tk.Label(self, text="Food Name:")
        lbl_food_name.grid(row=0,column=0,padx=(27,0),pady=(10,0),sticky='nw')
        self.txt_food_name = tk.Entry(self, text='')
        self.txt_food_name.grid(row=1,column=0,rowspan=1,columnspan=2,padx=(30,40),pady=(0,0),sticky='new')

        lbl_image = tk.Label(self, text="Image:")
        lbl_image.grid(row=2,column=0,padx=(27,0),pady=(10,0),sticky='nw')
        self.txt_image = tk.Entry(self, text='')
        self.txt_image.grid(row=3,column=0,rowspan=1,columnspan=2,padx=(30,40),pady=(0,0),sticky='new')

        lbl_isle = tk.Label(self, text="Isle:")
        lbl_isle.grid(row=4,column=0,padx=(27,0),pady=(10,0),sticky='nw')
        self.txt_isle = tk.Entry(self, text='')
        self.txt_isle.grid(row=5,column=0,rowspan=1,columnspan=2,padx=(30,40),pady=(0,0),sticky='new')

        lbl_order = tk.Label(self, text="Order:")
        lbl_order.grid(row=6,column=0,padx=(27,0),pady=(10,0),sticky='nw')
        self.txt_order = tk.Entry(self, text='')
        self.txt_order.grid(row=7,column=0,rowspan=1,columnspan=2,padx=(30,40),pady=(0,0),sticky='new')

        lbl_autoadd = tk.Label(self, text="Auto add: ")
        lbl_autoadd.grid(row=8,column=0,padx=(27,0),pady=(10,0),sticky='nw')
        self.var_autoadd = tk.IntVar()
        self.tick_autoadd = tk.Checkbutton(self, variable=self.var_autoadd)
        self.tick_autoadd.grid(row=8,column=1,rowspan=1,columnspan=1,padx=(0,0),pady=(10,0),sticky='sw')

        scrollbar1 = tk.Scrollbar(self,orient='v')
        self.lstList1 = tk.Listbox(self,exportselection=0,yscrollcommand=scrollbar1.set)
        self.lstList1.bind('<<ListboxSelect>>',lambda event: self.select_food(event))
        scrollbar1.config(command=self.lstList1.yview)
        scrollbar1.grid(row=1,column=5,rowspan=7,columnspan=1,padx=(0,0),pady=(0,0),sticky='nse')
        self.lstList1.grid(row=1,column=2,rowspan=7,columnspan=3,padx=(0,0),pady=(0,0),sticky='nsew')

        btn_add = tk.Button(self,width=12,height=2,text='Add',command=lambda: self.add_to_list())
        btn_add.grid(row=9,column=0,padx=(25,0),pady=(45,10),sticky='w')
        btn_update = tk.Button(self,width=12,height=2,text='Update',command=lambda: self.update_food())
        btn_update.grid(row=9,column=1,padx=(15,0),pady=(45,10),sticky='w')
        btn_delete = tk.Button(self,width=12,height=2,text='Delete',command=lambda: self.delete_food())
        btn_delete.grid(row=9,column=2,padx=(15,0),pady=(45,10),sticky='w')
        btn_close = tk.Button(self,width=12,height=2,text='Close',command=lambda:os._exit(0))
        btn_close.grid(row=9,column=4,columnspan=1,padx=(15,0),pady=(45,10),sticky='e')

        self.refresh()

    def refresh(self):
        self.lstList1.delete(0,'end')
        con = sqlite3.connect('db_groceryList.db')
        with con:
            cursor = con.cursor()
            cursor.execute("""SELECT COUNT(*) FROM tbl_foodList""")
            count = cursor.fetchone()[0]
            i = 0
            while i < count:
                cursor.execute("""SELECT food_name FROM tbl_foodList ORDER BY food_name DESC""")
                var_list = cursor.fetchall()[i]
                for item in var_list:
                    self.lstList1.insert(0, str(item))
                    i+=1
        con.close()

    def select_food(self, event):
        sel_list = event.widget
        select = sel_list.curselection()[0]
        food_name = sel_list.get(select)
        con = sqlite3.connect('db_groceryList.db')
        with con:
            cursor = con.cursor()
            cursor.execute("""SELECT food_name,food_image,food_isle,food_order,food_autoadd FROM tbl_foodList WHERE food_name = (?)""",
                           [food_name])
            food_values = cursor.fetchall()
            for data in food_values:
                self.txt_food_name.delete(0,'end')
                self.txt_food_name.insert(0,data[0])
                self.txt_image.delete(0,'end')
                self.txt_image.insert(0,data[1])
                self.txt_isle.delete(0,'end')
                self.txt_isle.insert(0,data[2])
                self.txt_order.delete(0,'end')
                self.txt_order.insert(0,data[3])
                self.var_autoadd.set(data[4])

    def add_to_list(self):
        food_name = self.txt_food_name.get().strip()
        food_image = self.txt_image.get().strip()
        food_isle = self.txt_isle.get().strip()
        food_order = self.txt_order.get().strip()
        food_autoadd = self.var_autoadd.get()
        if (len(food_name) > 0) and (len(food_image) > 0) and (len(food_isle) > 0) and(len(food_order) > 0):
            con = sqlite3.connect('db_groceryList.db')
            with con:
                cursor = con.cursor()
                cursor.execute("""SELECT COUNT(food_name) FROM tbl_foodList WHERE food_name = '{}'""".format(food_name))
                count = cursor.fetchone()[0]
                chkName = count
                if chkName == 0:
                    self.update_order(food_isle, food_order, False)
                    cursor.execute("""INSERT INTO tbl_foodList (food_name,food_image,food_isle,food_order,food_selected,food_autoadd) VALUES (?,?,?,?,?,?)""",
                                   (food_name,food_image,food_isle,food_order,food_autoadd,food_autoadd))
                    self.clear_entries()
                else:
                    messagebox.showerror("Name Error","That name already exists! Please choose a different name.")
            con.commit()
            con.close()
        else:
            messagebox.showerror("Missing entry","Please fill in all entries")
        self.refresh()

    def clear_entries(self):
        self.txt_food_name.delete(0,'end')
        self.txt_image.delete(0,'end')
        self.txt_isle.delete(0,'end')
        self.txt_order.delete(0,'end')
        self.var_autoadd.set(0)

    def update_food(self):
        try:
            selected_item = self.lstList1.curselection()[0]
            selected_food = self.lstList1.get(selected_item)
        except:
            messagebox.showinfo("Missing selection", "Select the item you want to update")
            return
        new_food_name = self.txt_food_name.get().strip()
        new_food_image = self.txt_image.get().strip()
        new_food_isle = self.txt_isle.get().strip()
        new_food_order = self.txt_order.get().strip()
        new_food_autoadd = self.var_autoadd.get()
        if (len(new_food_name) > 0) and (len(new_food_image) > 0) and (len(new_food_isle) > 0) and(len(new_food_order) > 0):
            con = sqlite3.connect('db_groceryList.db')
            response = messagebox.askokcancel("Update:", "Ok to update {} as {}".format(selected_food, new_food_name))
            if response:
                with con:
                    cursor = con.cursor()
                    cursor.execute("""SELECT COUNT(food_name) FROM tbl_foodList WHERE food_name = '{}'""".format(new_food_name))
                    count = cursor.fetchone()[0]
                    chkName = count
                    if (chkName == 0 or selected_food == new_food_name):
                        with con:
                            self.update_order(new_food_isle, new_food_order, False)
                            cursor.execute("""UPDATE tbl_foodList SET food_name = '{0}', food_image = '{1}', food_isle = '{2}', food_order = {3}, food_selected = {4}, food_autoadd = {5} WHERE food_name = '{6}'"""
                                           .format(new_food_name,new_food_image,new_food_isle,new_food_order,new_food_autoadd,new_food_autoadd,selected_food))
                            self.clear_entries()
                            self.refresh()
                            con.commit()
                    else:
                        messagebox.showerror("Name Error","That name already exists! Please choose a different name.")
                con.close()
                
                
        else:
            messagebox.showerror("Missing entry","Please fill in all entries")
        self.refresh()
        
    def delete_food(self):
        selected_food = self.lstList1.get(self.lstList1.curselection())
        con = sqlite3.connect('db_groceryList.db')
        with con:
            cursor = con.cursor()
            cursor.execute("""SELECT COUNT(*) FROM tbl_foodList""")
            count = cursor.fetchone()[0]
            if count > 1:
                confirm = messagebox.askokcancel("Delete Confirmation", "Are you sure you want to permenately delete {}".format(selected_food))
                if confirm:
                    with con:
                        cursor.execute("""SELECT food_isle,food_order FROM tbl_foodList WHERE food_name = '{}'""".format(selected_food))
                        food_info = cursor.fetchall()
                        for data in food_info:
                            old_food_isle = data[0]
                            old_food_order = data[1]
                        self.update_order(old_food_isle, old_food_order, True)
                        cursor.execute("""DELETE FROM tbl_foodList WHERE food_name = '{}'""".format(selected_food))
                        self.clear_entries()
                        con.commit()
            else:
                messagebox.showerror("Last Item", "You cannot delete the last item. Add another item before deleting this one")
        self.refresh()
        con.close()

    def update_order(self, isle, order, removed):
        con = sqlite3.connect('db_groceryList.db')
        with con:
            cursor = con.cursor()
            cursor.execute("""SELECT food_name FROM tbl_foodList WHERE food_isle = '{0}' AND food_order >= {1}""".format(isle,order))
            food_order_list = cursor.fetchall()
            if len(food_order_list) < 2 and removed:
                return
            if len(food_order_list) > 0:
                continue_order = messagebox.askokcancel("Change Order", "Do you want to change order? \nCancel will still complete action but \nthe order will not be changed")
                if not continue_order:
                    return
            else:
                return
            for returned_food in food_order_list:
                cursor.execute("""SELECT food_order FROM tbl_foodList WHERE food_name = '{}'""".format(returned_food[0]))
                returned_food_order = cursor.fetchone()[0]
                if removed and order == returned_food_order:
                    continue
                if removed:
                    new_food_order = returned_food_order - 1
                else:
                    new_food_order = returned_food_order + 1
                cursor.execute("""UPDATE tbl_foodList SET food_order = {0} WHERE food_name = '{1}'""".format(new_food_order,returned_food[0]))
                print("{0} order updated from {1} to {2}".format(returned_food[0],returned_food_order,new_food_order))
                con.commit()
        con.close()
                    
                

                
            
        





if __name__ == "__main__":
    app = ParentWindow()
    app.mainloop()
