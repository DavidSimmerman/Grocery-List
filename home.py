import tkinter as tk
from PIL import ImageTk, Image

import grocery

# Added to make it easy to change colors
bg_color = "lightgray"

class ParentWindow(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.title("PiApp")
        self.geometry('800x480')
        #self.attributes('-fullscreen', True)
        
        container = tk.Frame(self)
        container.config(bg=bg_color)
        container.pack(side='top', fill='both', expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (HomePage, grocery.GroceryListPage, grocery.GroceryOptions):

            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame("HomePage")

    def show_frame(self, cont):

        if cont == "GroceryListPage":
            self.frames[cont].update_foods()
        
        frame = self.frames[cont]
        frame.tkraise()

class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self,parent)

        self.config(bg=bg_color)

        self.grocery_icon = ImageTk.PhotoImage(Image.open("images/icons/groceryListIcon.png"))
        grocery_button = tk.Button(self, image=self.grocery_icon, bg=bg_color, activebackground=bg_color, bd=0,
                                   command=lambda: controller.show_frame("GroceryListPage"))
        grocery_button.grid(column=0, row=0)







if __name__ == "__main__":
    app = ParentWindow()
    app.mainloop()


"""
TODO list

    - Add search function
    - Add recipe adds
    - Add printing
    - Fix bottom row
    - Tune scrolling
    
"""
