import os
import io
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox
import sqlite3
import functools

import home

class GroceryListPage(tk.Frame):
    
    def __init__(self, parent, controller):

        conn = sqlite3.connect('db_groceryList.db')
        with conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE if not exists tbl_foodList( \
                ID INTEGER PRIMARY KEY AUTOINCREMENT, \
                food_name TEXT, \
                food_image TEXT, \
                food_isle TEXT, \
                food_order INT, \
                food_selected BIT, \
                food_autoadd BIT \
                );")
            conn.commit()
        conn.close()
        
        tk.Frame.__init__(self,parent)

        self.controller = controller
        self.config(bg=home.bg_color)

        self.just_moved = False

        self.back_icon = ImageTk.PhotoImage(Image.open("images/icons/back_icon.png"))
        back_button = tk.Button(self, image=self.back_icon, bg=home.bg_color, activebackground=home.bg_color, bd=0,
                                command=lambda: controller.show_frame("HomePage"))
        back_button.grid(column=0, row=0, padx=1)
        self.options_icon = ImageTk.PhotoImage(Image.open("images/icons/options_icon.png"))
        options_button = tk.Button(self, image=self.options_icon, bg=home.bg_color, activebackground=home.bg_color, bd=0,
                                   command=lambda: controller.show_frame("GroceryOptions"))
        options_button.grid(column=1, row=0)
        self.search_icon = ImageTk.PhotoImage(Image.open("images/icons/search_icon.png"))
        search_button = tk.Button(self, image=self.search_icon, bg=home.bg_color, activebackground=home.bg_color, bd=0,
                                command=lambda: controller.show_frame("HomePage")) # TODO Add function
        search_button.grid(column=2, row=0, padx=1)

        # create a canvas object and a vertical scrollbar for scrolling it

        frame_canvas = tk.Frame(self)
        frame_canvas.grid(row=1, column=0, columnspan=3)
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        frame_canvas.grid_propagate(False)

        canvas = tk.Canvas(frame_canvas, height=450, bd=0, highlightthickness=0,bg=home.bg_color)
        canvas.pack(side='left', fill='both', expand=True)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.canvasheight = 2000

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas,height=450,bg=home.bg_color)
        interior_id = canvas.create_window(0, 0, window=interior,anchor='nw')


        self.food_list = {}

        conn = sqlite3.connect('db_groceryList.db')
        with conn:
            cur = conn.cursor()
            cur.execute("""SELECT food_name FROM tbl_foodList ORDER BY food_name ASC""")
            returned_food_names = cur.fetchall()
            for food_name in returned_food_names:
                cur.execute("""SELECT food_image,food_selected FROM tbl_foodList WHERE food_name = '{}'""".format(food_name[0]))
                returned_data = cur.fetchall()
                for data in returned_data:
                    self.food_list[food_name] = [data[1], data[0]]

        conn.close()

        current_column = 0
        current_row = 0

        for food in self.food_list:
            self.food_list[food].append(ImageTk.PhotoImage(Image.open("images/food/food_s/" + self.food_list[food][1])))
            self.food_list[food].append(ImageTk.PhotoImage(Image.open("images/food/food_ns/" + self.food_list[food][1])))
            if self.food_list[food][0]:
                food_btn_image = self.food_list[food][2]
            else:
                food_btn_image = self.food_list[food][3]
            self.food_list[food].append(tk.Button(interior, image=food_btn_image, bg=home.bg_color,
                                                  activebackground=home.bg_color, bd=0,
                                                  command=functools.partial(self.select_food, food)))
            self.food_list[food][4].grid(column=current_column, row=current_row)

            current_column+=1
            if (current_column == 5):
                current_column = 0
                current_row+=1

        
        #interior.update_idletasks()
        frame_canvas.config(width=800, height=450)
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        self.offset_y = 0
        self.prevy = 0
        self.scrollposition = 1

        def on_press(event):
            self.just_moved = False
            self.offset_y = event.y_root
            if self.scrollposition < 1:
                self.scrollposition = 1
            elif self.scrollposition > self.canvasheight:
                self.scrollposition = self.canvasheight
            canvas.yview_moveto(self.scrollposition / self.canvasheight)

        def on_touch_scroll(event):
            nowy = event.y_root

            sectionmoved = 45
            if nowy > self.prevy:
                self.just_moved = True
                event.delta = -sectionmoved
            elif nowy < self.prevy:
                self.just_moved = True
                event.delta = sectionmoved
            else:
                event.delta = 0
            self.prevy= nowy

            self.scrollposition += event.delta
            canvas.yview_moveto(self.scrollposition/ self.canvasheight)

        self.bind("<Enter>", lambda _: self.bind_all('<Button-1>', on_press), '+')
        self.bind("<Leave>", lambda _: self.unbind_all('<Button-1>'), '+')
        self.bind("<Enter>", lambda _: self.bind_all('<B1-Motion>', on_touch_scroll), '+')
        self.bind("<Leave>", lambda _: self.unbind_all('<B1-Motion>'), '+')

    def select_food(self, food):
        if (not self.just_moved):
            conn = sqlite3.connect('db_groceryList.db')
            with conn:
                cur = conn.cursor()
                if self.food_list[food][0]:
                    cur.execute("""SELECT food_autoadd FROM tbl_foodList WHERE food_name = '{}'""".format(food[0]))
                    food_auto_add = cur.fetchone()[0]
                    if food_auto_add:
                        message = messagebox.askokcancel("Remove from list?", "Are you sure you want to remove {} from the list? \nNote, thsi food is labed as 'Auto Add'".format(food))
                    else:
                        message = messagebox.askokcancel("Remove from list?", "Are you sure you want to remove {} from the list?".format(food[0]))
                    if message:
                        self.food_list[food][0] = 0
                        cur.execute("""UPDATE tbl_foodList SET food_selected = {0} WHERE food_name = '{1}'""".format(0,food[0]))
                        self.food_list[food][4].configure(image=self.food_list[food][3])
                else:
                    message = messagebox.askokcancel("Add to list?", "Are you sure you want to add {} to the list?".format(food[0]))
                    if message:
                        self.food_list[food][0] = 1
                        cur.execute("""UPDATE tbl_foodList SET food_selected = {0} WHERE food_name = '{1}'""".format(1,food[0]))
                        self.food_list[food][4].configure(image=self.food_list[food][2])

    def update_foods(self):
        conn = sqlite3.connect('db_groceryList.db')
        with conn:
            cur = conn.cursor()
            for food in self.food_list:
                cur.execute("""SELECT food_selected FROM tbl_foodList WHERE food_name = '{}'""".format(food[0]))
                self.food_list[food][0] = cur.fetchone()[0]
                if self.food_list[food][0]:
                    self.food_list[food][4].configure(image=self.food_list[food][2])
                else:
                    self.food_list[food][4].configure(image=self.food_list[food][3])
        conn.close()
        
        
class GroceryOptions(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self,parent)

        self.config(bg=home.bg_color)

        print_list_button = tk.Button(self, text="Print List", command=self.print_list)
        print_list_button.pack()
        add_recipe_button = tk.Button(self, text="Add Recipes List")
        add_recipe_button.pack()
        back_button = tk.Button(self, text="←", command=lambda: controller.show_frame("GroceryListPage"))
        back_button.pack()

    def print_list(self):
        if not messagebox.askokcancel("Print List", "Are you sure you want to print the list? \nThis will reset the current list after printing"):
            return
        list_to_print = "─────────────────────────────────────────────────────────┰─────────────────────────────────────────────────────────\n"

        conn = sqlite3.connect('db_groceryList.db')
        with conn:
            cur = conn.cursor()
            for isle in range(21):
                isle += 1
                left_isle = str(isle) + "l"
                right_isle = str(isle) + "r"

                cur.execute("""SELECT food_name FROM tbl_foodList WHERE food_isle = '{}' AND food_selected = 1""".format(left_isle))
                left_food_list = cur.fetchall()
                cur.execute("""SELECT food_name FROM tbl_foodList WHERE food_isle = '{}' AND food_selected = 1""".format(right_isle))
                right_food_list = cur.fetchall()

                if len(left_food_list) >= len(right_food_list):
                    biggest_count = len(left_food_list)
                else:
                    biggest_count = len(right_food_list)

                for i in range(biggest_count):

                    # Add left side
                    if len(left_food_list) > i:
                        food_l = " " + left_food_list[i][0]
                        while len(food_l) < 57:
                            food_l += " "
                    else:
                        food_l = "                                                         "
                    food_l += "│ "
                    list_to_print += food_l

                    # Add right side
                    if len(right_food_list) > i:
                        food_r = right_food_list[i][0] + "\n"
                    else:
                        food_r = "\n"
                    list_to_print += food_r
                if isle != 21:
                    list_to_print += "─────────────────────────────────────────────────────────┽─────────────────────────────────────────────────────────\n"
            list_to_print += "─────────────────────────────────────────────────────────┸─────────────────────────────────────────────────────────\n"

            cur.execute("""UPDATE tbl_foodList SET food_selected = 0 WHERE food_selected = 1 AND food_autoadd = 0""")

            # Makes sure that all auto adds are added
            cur.execute("""UPDATE tbl_foodList SET food_selected = 1 WHERE food_autoadd = 1""")

            conn.commit 
                
        conn.close()

        with io.open("list.txt", 'w', encoding="utf-8") as file:
            file.write(list_to_print)
            file.close()

        os.system("lp list.txt")

        # print(list_to_print)
                
            



        
        




if __name__ == "__main__":
    pass
