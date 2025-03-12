# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 15:42:05 2021

@author: Maarten

In this script, the class NewProject is defined. The class NewProject codes for
a wizard to easily create and configure a new project.
"""
#%% import packages
import os
import re
import shutil
import json
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

#%%

class NewProject(tk.Toplevel):
    """
    The class NewProject codes for a wizard to easily create and configure a
    new project
    """
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.master = master

        #set default size
        self.geometry('600x380')

        #set title
        self.title("New project")

        #create tkinter variables
        self.titlevar = tk.StringVar() #title of project
        self.directory = tk.StringVar() #directory of project
        self.img_skeleton = tk.StringVar() #image to create new skeleton
        self.dir_skeleton = tk.StringVar() #directory of skeleton to import
        self.img_skeleton_bool = tk.BooleanVar() #True if user wants to create new skeleton
        self.dir_skeleton_bool = tk.BooleanVar() #True if user wants to import skeleton

        #set default values of tkinter variables
        self.img_skeleton_bool.set(True)
        self.dir_skeleton_bool.set(False)

        #create frames
        self.frame_title = tk.Frame(self)
        self.frame_directory = tk.Frame(self)
        self.frame_skeleton = tk.Frame(self)
        self.frame_img_skeleton = tk.Frame(self.frame_skeleton)
        self.frame_dir_skeleton = tk.Frame(self.frame_skeleton)

        #create labels
        self.label_title = tk.Label(self.frame_title,
                                    text="Title", width=8, anchor='w')
        self.label_directory = tk.Label(self.frame_directory,
                                        text="Directory", width=8, anchor='w')
        self.label_skeleton = tk.Label(self.frame_skeleton,
                                       text="Skeleton", width=8, anchor='w')
        self.label_img_skeleton = tk.Label(self.frame_img_skeleton,
                                           text="Image", width=8, anchor='w')
        self.label_dir_skeleton = tk.Label(self.frame_dir_skeleton,
                                           text="Directory", width=8, anchor='w')

        #set default configurations of labels
        self.label_dir_skeleton.config(state='disabled')

        #create checkbuttons
        self.checkbut_img_skeleton = tk.Checkbutton(self.frame_img_skeleton,
                                                    variable=self.img_skeleton_bool,
                                                    text='New',
                                                    command=self.img_skeleton_checkbutton)

        self.checkbut_dir_skeleton = tk.Checkbutton(self.frame_dir_skeleton,
                                                    variable=self.dir_skeleton_bool,
                                                    text='Import',
                                                    command=self.dir_skeleton_checkbutton)

        #create entry fields
        self.field_title = tk.Entry(self.frame_title,
                                    width=60,
                                    textvariable=self.titlevar)
        self.field_directory = tk.Entry(self.frame_directory,
                                        width=57,
                                        textvariable=self.directory)
        self.field_img_skeleton = tk.Entry(self.frame_img_skeleton,
                                           width=47,
                                           textvariable=self.img_skeleton)
        self.field_dir_skeleton = tk.Entry(self.frame_dir_skeleton,
                                           width=47,
                                           textvariable=self.dir_skeleton)

        #set default configurations of fields
        self.field_dir_skeleton.config(state='disabled')

        #create buttons

        #create an invisible image of 1 pixel
        pixel = tk.PhotoImage(width=1, height=1)
        #if we add this image to a button, we can specify the height and width
        #in pixels instead of in characters (number of times width of a 0 /
        #number of times height of a 0), allowing to resize the button so it
        #exactly matches the entryfield next to it
        #When a button is created, the option compound should be set to 'center'
        #so the (invisible) image is displayed in the background center, with
        #the text on top of it (the 'normal' position)

        self.button_directory = \
            tk.Button(self.frame_directory,
                      text="...",
                      image=pixel,
                      compound="center",
                      width=30,
                      height=22,
                      command=lambda: self.choose_directory(self.directory))

        self.button_img_skeleton = \
            tk.Button(self.frame_img_skeleton,
                      text="...",
                      image=pixel,
                      compound="center",
                      width=30,
                      height=22,
                      command=lambda: self.choose_file(self.img_skeleton))

        self.button_dir_skeleton =  \
            tk.Button(self.frame_dir_skeleton,
                      text="...",
                      image=pixel,
                      compound="center",
                      width=30,
                      height=22,
                      command=lambda: self.choose_directory(self.dir_skeleton))

        self.button_ok = tk.Button(self,
                                   text="OK",
                                   command=self.confirm)

        #set default configurations of buttons
        self.button_dir_skeleton.config(state='disabled')

        #pack all elements
        #frame_title
        self.label_title.pack(side='left')
        self.field_title.pack()

        #frame_directory
        self.label_directory.pack(side='left')
        self.field_directory.pack(side='left')
        self.button_directory.pack()

        #frame_img_skeleton
        self.checkbut_img_skeleton.pack(anchor='w')
        self.label_img_skeleton.pack(side='left')
        self.field_img_skeleton.pack(anchor='w', side='left')
        self.button_img_skeleton.pack()

        #frame_dir_skeleton
        self.checkbut_dir_skeleton.pack(anchor='w')
        self.label_dir_skeleton.pack(side='left')
        self.field_dir_skeleton.pack(anchor='w', side='left')
        self.button_dir_skeleton.pack()

        #frame_skeleton
        self.label_skeleton.pack(side='left', anchor='nw')
        self.frame_img_skeleton.pack(anchor='nw')
        self.frame_dir_skeleton.pack(anchor='nw')

        #self
        self.frame_title.pack(anchor='w', pady=5)
        self.frame_directory.pack(anchor='w', pady=5)
        self.frame_skeleton.pack(anchor='w', pady=5)
        self.button_ok.pack(side='bottom', pady=5)

        #set focus on first entryfield
        self.field_title.focus()

        #bind hitting return/enter key to invocation of button/checkbox
        self.bind_class("Button",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())
        self.bind_class("Checkbutton",
                        "<Key-Return>",
                        lambda event: event.widget.invoke())

        #bind method to resize entry field to <Configure> event
        self.bind("<Configure>", lambda event: self.resize_window())

        #general child-window settings
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def choose_directory(self, textvar):
        """
        Invoke dialog to choose a directory

        Parameters
        ----------
        textvar : tkinter.StringVar
            Variable to which the directory-string has to be assigned
        """
        path = tkfiledialog.askdirectory()
        textvar.set(path)

    def choose_file(self, textvar):
        """
        Invoke dialog to choose a file

        Parameters
        ----------
        textvar : tkinter.StringVar
            Variable to which the directory of the file has to be assigned
        """
        path = tkfiledialog.askopenfilename()
        textvar.set(path)

    def img_skeleton_checkbutton(self):
        """
        Configure all elements within frame_img_skeleton and frame_dir_skeleton

        If self.checkbut_img_skeleton was activated, disable all elements in
        frame_dir_skeleton (except the checkbutton) and enable all elements in
        frame_img_skeleton

        If self.checkbut_img_skeleton was deactivated, disable all elements in
        frame_img_skeleton (except the checkbutton) and enable all elements in
        frame_dir_skeleton
        """
        value = self.img_skeleton_bool.get()

        if value:
            self.label_img_skeleton.config(state='normal')
            self.field_img_skeleton.config(state='normal')
            self.button_img_skeleton.config(state='normal')
            self.dir_skeleton_bool.set(False)
            self.label_dir_skeleton.config(state='disabled')
            self.field_dir_skeleton.config(state='disabled')
            self.button_dir_skeleton.config(state='disabled')
        else: #not value
            self.label_img_skeleton.config(state='disabled')
            self.field_img_skeleton.config(state='disabled')
            self.button_img_skeleton.config(state='disabled')
            self.dir_skeleton_bool.set(True)
            self.label_dir_skeleton.config(state='normal')
            self.field_dir_skeleton.config(state='normal')
            self.button_dir_skeleton.config(state='normal')

    def dir_skeleton_checkbutton(self):
        """
        Configure all elements within frame_img_skeleton and frame_dir_skeleton

        If self.checkbut_dir_skeleton was activated, disable all elements in
        frame_img_skeleton (except the checkbutton) and enable all elements in
        frame_dir_skeleton

        If self.checkbut_dir_skeleton was deactivated, disable all elements in
        frame_dir_skeleton (except the checkbutton) and enable all elements in
        frame_img_skeleton
        """
        value = self.dir_skeleton_bool.get()

        if value:
            self.label_dir_skeleton.config(state='normal')
            self.field_dir_skeleton.config(state='normal')
            self.button_dir_skeleton.config(state='normal')
            self.img_skeleton_bool.set(False)
            self.label_img_skeleton.config(state='disabled')
            self.field_img_skeleton.config(state='disabled')
            self.button_img_skeleton.config(state='disabled')
        else: #not value
            self.label_dir_skeleton.config(state='disabled')
            self.field_dir_skeleton.config(state='disabled')
            self.button_dir_skeleton.config(state='disabled')
            self.img_skeleton_bool.set(True)
            self.label_img_skeleton.config(state='normal')
            self.field_img_skeleton.config(state='normal')
            self.button_img_skeleton.config(state='normal')

    def resize_window(self):
        """
        Resize the entry fields if the size of the new-project-dialog window
        changes
        """
        #get useable width
        uw = self.winfo_width()

        self.field_title.config(width=int((uw - 115)/10))
        self.field_directory.config(width=int((uw - 150)/10))
        self.field_img_skeleton.config(width=int((uw - 230)/10))
        self.field_dir_skeleton.config(width=int((uw - 230)/10))

    def check_title(self):
        """
        Check if the title is valid

        A valid title may only contain Unicode word characters, Unicode digits,
        underscores and dashes
        """
        #check if there was entered a title
        if self.titlevar.get() == "":
            message = "No title was entered"
            tkmessagebox.showerror(title="Invalid title",
                                   message=message)
            self.field_title.focus()
            return False

        #check if the title is valid
        if not re.match(r"^[\w\d_-]*$", self.titlevar.get()):
            message = "The project title may only contain Unicode word characters, " +\
                      "Unicode digits, underscores and dashes"
            tkmessagebox.showerror(title="Invalid title",
                                   message=message)
            self.field_title.focus()
            self.field_title.selection_range(0, 'end')
            return False
        return True

    def check_directory(self):
        """
        Check if an existing directory was given
        """
        #check if a directory was given
        if self.directory.get() == "":
            message = "No directory was entered"
            tkmessagebox.showerror(title="Invalid directory",
                                   message=message)
            self.field_directory.focus()
            self.field_directory.selection_range(0, 'end')
            return False

        #check if directory exists
        try:
            os.chdir(self.directory.get())
            if self.master.wdir is not None:
                os.chdir(self.master.wdir)
        except FileNotFoundError:
            message = "The directory you entered doesn't exist"
            tkmessagebox.showerror(title="Invalid directory",
                                   message=message)
            self.field_directory.focus()
            self.field_directory.selection_range(0, 'end')
            return False
        return True

    def check_img_skeleton(self):
        """
        Check if a valid image was given

        Images with extension .jpg or .png are allowed
        """
        #check if a value was entered
        if self.img_skeleton.get() == "":
            message = "No image was entered"
            tkmessagebox.showerror(title="Invalid skeleton image",
                                   message=message)
            self.field_img_skeleton.focus()
            return False

        #check if file exists
        try:
            open(self.img_skeleton.get())
        except FileNotFoundError:
            message = "The skeleton image you entered doesn't exist"
            tkmessagebox.showerror(title="Invalid skeleton image",
                                   message=message)
            self.field_img_skeleton.focus()
            self.field_img_skeleton.selection_range(0, 'end')
            return False

        #check if file is an image
        if self.img_skeleton.get().split(".")[-1] not in ["jpg", "png"]:
            message = "The skeleton image you entered hasn't right extension\n\n" +\
                      "valid extensions:\n" +\
                      ".jpg\n" +\
                      ".png"
            tkmessagebox.showerror(title="Invalid skeleton image",
                                   message=message)
            self.field_img_skeleton.focus()
            self.field_img_skeleton.selection_range(0, 'end')
            return False
        return True

    def check_dir_skeleton(self):
        """
        Check if a valid skeleton directory was given

        A valid skeleton directory is an existing directory containing at least
        following files:
            - skeleton.json
            - skeleton.jpg or skeleton.png
        """
        #check if a value was entered
        if self.dir_skeleton.get() == "":
            message = "No skeleton directory was entered"
            tkmessagebox.showerror(title="Invalid skeleton directory",
                                   message=message)
            self.field_dir_skeleton.focus()
            return False

        #check if entered directory exists
        try:
            os.chdir(self.dir_skeleton.get())
        except FileNotFoundError:
            message = "The skeleton directory you entered doesn't exist"
            tkmessagebox.showerror(title="Invalid skeleton directory",
                                   message=message)
            self.field_dir_skeleton.focus()
            self.field_dir_skeleton.selection_range(0, 'end')
            return False

        #check if the directory contains the right files
        files = os.listdir()
        if ("skeleton.json" not in files) or\
            (("skeleton.png" not in files) and\
             ("skeleton.jpg" not in files)):
            message = "The skeleton directory you entered doesn't contain all " +\
                      "necessary files\n \n" +\
                      "The skeleton folder should contain following files:\n" +\
                      "- skeleton.json\n" +\
                      "- skeleton.png or skeleton.jpg"
            tkmessagebox.showerror(title="Invalid skeleton directory",
                                   message=message)

            if self.master.wdir != "":
                os.chdir(self.master.wdir)

            self.field_dir_skeleton.focus()
            self.field_dir_skeleton.selection_range(0, 'end')
            return False

        if self.master.wdir is not None:
            os.chdir(self.master.wdir)
        return True

    def confirm(self):
        """
        Confirm the settings for the new project

        If all entries are valid, a new project is created
        """
        #check if all entries are valid

        #title
        if self.check_title() is False:
            return

        #directory
        if self.check_directory() is False:
            return

        #skeleton
        if self.img_skeleton_bool.get():
            #the user wants to create a new skeleton
            if self.check_img_skeleton() is False:
                return
        else:
            #the user wants to import a skeleton
            if self.check_dir_skeleton() is False:
                return

        #all entries are valid

        #create the project
        project_path = os.path.join(self.directory.get(), self.titlevar.get())
        os.mkdir(project_path)

        if self.img_skeleton_bool.get():
            #user wants to create a new skeleton
            skeleton_dir = os.path.join(project_path, "project")
            os.mkdir(skeleton_dir)

            #copy image
            src = self.img_skeleton.get()
            img_name = "skeleton." + src.split(".")[-1]
            dst = os.path.join(skeleton_dir, img_name)
            shutil.copy(src, dst)

            #create empty skeleton.json file
            skeleton_dict = {}
            json_path = os.path.join(skeleton_dir, "skeleton.json")
            file = open(json_path, 'w')
            json.dump(skeleton_dict, file)
            file.close()

            self.master.set_mode(1)
        else:
            #user wants to import a skeleton
            src = self.dir_skeleton.get()
            dst = os.path.join(project_path, "project")
            shutil.copytree(src, dst)

        #open the project
        self.master.open_project(path=project_path)

        #destroy the window
        self.destroy()

        if self.img_skeleton_bool.get():
            #a new projcet was initiated succesfully

            #show an infobox to inform the user the skeleton can be initiated
            #in the next step
            message = \
            """
            The project was initiated succesfully

            You can now initiate the keypoints of the skeleton
            """
            tkmessagebox.showinfo(title="Project initiated",
                                   message=message)
