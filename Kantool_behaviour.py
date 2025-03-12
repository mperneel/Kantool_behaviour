# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 08:27:07 2021

@author: Maarten Perneel

Master script for the Kantool application. In this script, the Application
class is defined, which codes for the main window of the application
"""
# %% Load packages
import os
import shutil
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
import numpy as np
import ctypes
import json

from skeleton import Skeleton
from ethogram import Ethogram
from annotation_canvas import AnnotationCanvas
from skeleton_canvas import SkeletonCanvas
from new_project import NewProject
from export_dataset import ExportDataset
from object_canvas import ObjectCanvas
from settings_dialog import SettingsDialog
from annotations import Annotations
from settings import Settings
from import_mask_template_dialog import ImportMaskTemplateDialog
from save_mask_template_dialog import SaveMaskTemplateDialog
from mask_template_manager import MaskTemplateManager
from ask_mask_template import AskMaskTemplate
from ethogram_editor import EthogramEditor

# %% Main application


class Application(tk.Frame):


    def __init__(self, master=None, program_dir=None):
        # initiate frame
        tk.Frame.__init__(self, master)
        self.pack()
        self.master = master

        # make sure the application fills the whole window
        self.master.state('zoomed')
        root.update()

        # Declare attributes
        self.program_dir = program_dir  # path to software files
        self.mode = 0  # annotation mode
        self.wdir = None  # working directory

        # get useable width and height (expressed in pixels)
        self.uw = root.winfo_width()  # useable_width
        self.uh = root.winfo_height()  # useable_height

        # format application

        # initiate main panel
        self.main_panel = tk.PanedWindow(bd=0,
                                         bg="black",
                                         orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH,
                             expand=True)

        # set title
        self.master.title("Kantool behaviour")

        # Declare attributes belonging to custom classes
        # skeleton
        self.skeleton = Skeleton()

        #ethogram
        self.ethogram = Ethogram(master=self)

        # annotations
        self.annotations = Annotations(master=self)

        # settings
        self.settings = Settings()

        # canvas to show image
        self.annotation_canvas = AnnotationCanvas(master=self,
                                                  bd=10,
                                                  width=self.uw * 0.7,
                                                  height=self.uh)

        # canvas to show skeleton
        self.skeleton_canvas = SkeletonCanvas(master=self,
                                              bd=10,
                                              width=self.uw * 0.15,
                                              height=self.uh*0.5)

        # canvas with masks
        self.object_canvas = ObjectCanvas(master=self,
                                          width=int(self.uw * 0.15),
                                          height=int(self.uh*0.5))

        #check modes
        self.object_canvas.check_mode()
        self.annotation_canvas.check_mode()

        # add annotation canvas
        self.main_panel.add(self.annotation_canvas)

        # create second paned window on the left side to add skeleton_canvas
        # and object_canvas above each other
        self.right_panel = tk.PanedWindow(self.main_panel,
                                          bd=0,
                                          bg="black",
                                          orient=tk.VERTICAL)

        self.main_panel.add(self.right_panel)

        # add skeleton canvas
        self.right_panel.add(self.skeleton_canvas)

        # add mask canvas
        self.right_panel.add(self.object_canvas)

        # configure menu
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)

        # file menu
        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.file_menu.add_command(label="Open project (Ctrl+Shift+O)",
                                   command=self.open_project)
        self.file_menu.add_command(label="New project (Ctrl+Shift+N)",
                                   command=self.new_project)
        self.file_menu.add_command(label="Open image (Ctrl+O)",
                                   command=self.annotation_canvas.open_image)
        self.file_menu.add_command(label="Close image (Ctrl+W)",
                                   command=self.annotation_canvas.close_image)
        self.file_menu.add_command(label="Save annotations (Ctrl+S)",
                                   command=self.save)
        self.file_menu.add_command(label="Delete keypoint (Del)",
                                   command=self.annotation_canvas.delete_keypoint)
        self.file_menu.add_command(label="Delete object (Ctrl+Del)",
                                   command=self.annotation_canvas.delete_object)
        self.file_menu.add_command(label="Previous image (F7)",
                                   command=lambda: self.annotation_canvas.switch_image(direction=-1))
        self.file_menu.add_command(label="Next image (F8)",
                                   command=lambda: self.annotation_canvas.switch_image(direction=1))
        self.file_menu.add_command(label="Import image (Ctrl+I)",
                                   command=self.import_images)
        self.file_menu.add_command(label="Export dataset (F5)",
                                   command=self.export_dataset)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.master.bind("<Control-Shift-O>",\
                         lambda event: self.open_project())
        self.master.bind("<Control-Shift-N>",\
                         lambda event: self.new_project())
        self.master.bind("<Control-o>",\
                         lambda event: self.annotation_canvas.open_image())
        self.master.bind("<Control-w>",\
                         lambda event: self.annotation_canvas.close_image())
        self.master.bind("<Control-Delete>",\
                         lambda event: self.annotation_canvas.delete_object())
        self.master.bind("<F7>",\
                         lambda event: self.annotation_canvas.switch_image(direction=-1))
        self.master.bind("<F8>",\
                         lambda event: self.annotation_canvas.switch_image(direction=1))
        self.master.bind("<Control-i>",\
                         lambda event: self.import_images())
        self.master.bind("<F5>",\
                         lambda event: self.export_dataset())
        self.master.bind("<Key-Delete>",\
                         lambda event: self.delete_keypoint())
        # Delete is bound to two methods therefore a method in the Application
        # class is provoked, which activates on it's turn
        # self.skeleton_canvas.delete_keypoint() or
        # self.annotation_canvas.delete_keypoint(), depending on the mode of the
        # application (annotation mode or skeleton mode)

        self.master.bind("<Control-s>", lambda event: self.save())
        # Save is bound to two methods, therefore, a method in the Application
        # class is first provoked, which activates on it's turn the appropriate
        # method of SkeletonCanvas or AnnotationCanvas

        # disable all menu items which may only be used when a project is opened
        self.file_menu.entryconfig("Open image (Ctrl+O)", state="disabled")
        self.file_menu.entryconfig("Close image (Ctrl+W)", state="disabled")
        self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="disabled")
        self.file_menu.entryconfig("Delete keypoint (Del)", state="disabled")
        self.file_menu.entryconfig("Delete object (Ctrl+Del)", state="disabled")
        self.file_menu.entryconfig("Previous image (F7)", state="disabled")
        self.file_menu.entryconfig("Next image (F8)", state="disabled")
        self.file_menu.entryconfig("Import image (Ctrl+I)", state="disabled")
        self.file_menu.entryconfig("Export dataset (F5)", state="disabled")

        # edit menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=False)
        self.edit_menu.add_command(label='Import mask template',
                                   command=lambda: self.import_mask_template())
        self.edit_menu.add_command(label='Save mask template',
                                   command=lambda: self.save_mask_template())
        self.edit_menu.add_command(label='Mask template manager',
                                   command=lambda: self.manage_mask_templates())
        self.edit_menu.add_command(label='Ethogram',
                                   command=lambda: EthogramEditor(self))
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)

        # disable all menu items which may only be used when a project is opened
        self.edit_menu.entryconfig("Import mask template", state="disabled")
        self.edit_menu.entryconfig("Save mask template", state="disabled")
        self.edit_menu.entryconfig("Mask template manager", state="disabled")

        # mode menu
        self.mode_menu = tk.Menu(self.menubar, tearoff=False)
        self.mode_menu.add_command(label="Annotation",
                                   command=lambda: self.set_mode(0))
        self.mode_menu.add_command(label="Skeleton",
                                   command=lambda: self.set_mode(1))
        self.menubar.add_cascade(label="Mode", menu=self.mode_menu)

        # settings menu
        self.settings_menu = tk.Menu(self.menubar, tearoff=False)
        self.settings_menu.add_command(label="Settings",
                                       command=lambda: self.modify_settings())
        self.menubar.add_cascade(label="Settings", menu=self.settings_menu)

        # help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=False)
        self.help_menu.add_command(label="Help (F1)", command=self.launch_help)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.master.bind("<F1>", lambda event: self.launch_help())

        # skeleton menu
        self.skeleton_menu = tk.Menu(self.menubar, tearoff=False)
        self.skeleton_menu.add_command(label="Change order keypoints",
                                       command=self.skeleton_canvas.change_order_keypoints)
        self.skeleton_menu.add_command(label="Save skeleton (Ctrl+S)",
                                       command=self.save)
        self.skeleton_menu.add_command(label="Delete keypoint (Del)",
                                       command=self.skeleton_canvas.delete_keypoint)
        self.skeleton_menu.add_command(label="Change central keypoint",
                                       command=self.skeleton_canvas.change_central_keypoint)

        # bind events to methods
        self.master.bind("<Configure>", lambda event: self.resize_app())

        self.master.bind("<Key-Return>",
                         lambda event: self.annotation_canvas.new_object())
        # remark that the key is bound to self.master (root)

        # dimension self.window properly
        self.resize_app()

    def launch_help(self):
        """
        Launch the help file
        """
        if os.path.exists(os.path.join(self.program_dir, "help/help.pdf")):
            #this case will be executed when the application is run from the .py file
            os.startfile(os.path.join(self.program_dir, "help/help.pdf"))
        elif os.path.exists(os.path.join(self.program_dir, "_internal/help/help.pdf")):
            #this case will be executed when the application is run from a .exe
            #file generated with pyinstaller
            os.startfile(os.path.join(self.program_dir, "_internal/help/help.pdf"))

    def resize_app(self):
        """
        Adjust the position of the sash when te application is resized
        """
        uw = root.winfo_width()  # useable_width
        if self.uw != uw:
            uw_init = self.uw
            self.uw = uw

            sash_position_new = np.round(self.main_panel.sash_coord(0)[0] * self.uw/uw_init)\
                .astype(int)
            self.main_panel.sash_place(0,
                                       x=sash_position_new,
                                       y=self.main_panel.sash_coord(0)[1])

    def set_mode(self, mode):
        """
        Set mode of application

        Parameters
        ----------
        mode : int
            Mode of the application

            - 0 annotation mode
            - 1 skeleton mode
        """

        if mode == 0:
            # Annotation
            if self.mode == 1:
                # check if there are changes
                permission = self.skeleton_canvas.prepare_for_annotation_mode()

                if permission:
                    self.right_panel.forget(self.skeleton_canvas)
                    self.main_panel.forget(self.right_panel)
                    self.main_panel.add(self.annotation_canvas)
                    self.main_panel.add(self.right_panel)
                    self.right_panel.add(self.skeleton_canvas)
                    self.right_panel.add(self.object_canvas)
                    self.update()
                    self.skeleton_canvas.configure(bg='#f0f0f0')
                    self.skeleton_canvas.reset_zoom_level()
                    self.annotation_canvas.reset_zoom_level()
                    self.menubar.delete(2, 5)
                    self.menubar.add_cascade(
                        label="Edit", menu=self.edit_menu)
                    self.menubar.add_cascade(
                        label="Mode", menu=self.mode_menu)
                    self.menubar.add_cascade(
                        label="Settings", menu=self.settings_menu)
                    self.menubar.add_cascade(
                        label="Help", menu=self.help_menu)

                    self.file_menu.entryconfig(
                        "Open project (Ctrl+Shift+O)", state="normal")
                    self.file_menu.entryconfig(
                        "New project (Ctrl+Shift+N)", state="normal")
                    if self.wdir is not None:
                        self.file_menu.entryconfig(
                            "Open image (Ctrl+O)", state="normal")
                        self.file_menu.entryconfig(
                            "Close image (Ctrl+W)", state="normal")
                        self.file_menu.entryconfig(
                            "Save annotations (Ctrl+S)", state="normal")
                        self.file_menu.entryconfig(
                            "Delete keypoint (Del)", state="normal")
                        self.file_menu.entryconfig(
                            "Delete object (Ctrl+Del)", state="normal")
                        self.file_menu.entryconfig(
                            "Previous image (F7)", state="normal")
                        self.file_menu.entryconfig(
                            "Next image (F8)", state="normal")
                        self.file_menu.entryconfig(
                            "Import image (Ctrl+I)", state="normal")
                        self.file_menu.entryconfig(
                            "Export dataset (F5)", state="normal")

                    self.mode = mode
        else:  # mode == 1:
            # Skeleton
            if self.mode == 0:
                # close current image
                self.annotation_canvas.prepare_for_skeleton_mode()

                self.main_panel.forget(self.annotation_canvas)
                self.right_panel.forget(self.object_canvas)
                self.skeleton_canvas.configure(bg='#ff1a1a')
                self.update()
                self.skeleton_canvas.reset_zoom_level()
                self.menubar.delete(2, 5)
                self.menubar.add_cascade(
                    label="Mode", menu=self.mode_menu)
                self.menubar.add_cascade(
                    label="Skeleton", menu=self.skeleton_menu)
                self.menubar.add_cascade(
                    label="Settings", menu=self.settings_menu)
                self.menubar.add_cascade(
                    label="Help", menu=self.help_menu)

                self.file_menu.entryconfig(
                    "Open project (Ctrl+Shift+O)", state="disabled")
                self.file_menu.entryconfig(
                    "New project (Ctrl+Shift+N)", state="disabled")
                self.file_menu.entryconfig(
                    "Open image (Ctrl+O)", state="disabled")
                self.file_menu.entryconfig(
                    "Close image (Ctrl+W)", state="disabled")
                self.file_menu.entryconfig(
                    "Save annotations (Ctrl+S)", state="disabled")
                self.file_menu.entryconfig(
                    "Delete keypoint (Del)", state="disabled")
                self.file_menu.entryconfig(
                    "Delete object (Ctrl+Del)", state="disabled")
                self.file_menu.entryconfig(
                    "Previous image (F7)", state="disabled")
                self.file_menu.entryconfig("Next image (F8)", state="disabled")
                self.file_menu.entryconfig(
                    "Import image (Ctrl+I)", state="disabled")
                self.file_menu.entryconfig(
                    "Export dataset (F5)", state="disabled")

                self.mode = mode

        self.update_visualisations()

    def open_project(self, path=None):
        """
        Open a project

        Parameters
        ----------
        path : str, optional
            Path of the project. If None, there will be prompted a dialig to
            choose a directory. The default is None.
        """
        if path is None:
            # ask for a filepath
            path = tkfiledialog.askdirectory()

        if path != "":
            # check if path refers to a valid project

            files_folders = os.listdir(path)

            # load the skeleton
            # check if the directory is a valid project (skeleton present)
            if 'project' in files_folders:
                skeleton_files = os.listdir(os.path.join(path, 'project'))
                if ('skeleton.json' in skeleton_files) and\
                    (('skeleton.jpg' in skeleton_files) or
                     ('skeleton.png' in skeleton_files)):
                    # path refers to a valid project
                    valid_project = True

                    self.wdir = path
                    self.annotation_canvas.wdir = path
                    self.skeleton_canvas.wdir = path

                    # load the skeleton
                    if 'skeleton.jpg' in skeleton_files:
                        self.skeleton_canvas.skeleton_name = 'project\\skeleton.jpg'
                    elif 'skeleton.png' in skeleton_files:
                        self.skeleton_canvas.skeleton_name = 'project\\skeleton.png'
                    else:
                        raise ValueError("project folder misses an image file " +
                                         "called 'skeleton.jpg' or 'skeleton.png'")
                    self.skeleton_canvas.load_skeleton()

                    pth_ethogram = os.path.join(path, "project\\ethogram.json")
                    if os.path.exists(pth_ethogram):
                        self.ethogram.load(pth_ethogram)

                    # load the first image and annotations (if present)
                    image_found = False
                    i = -1

                    while not image_found:
                        i += 1
                        file = files_folders[i]

                        if (len(file.split('.')) == 2) and\
                                (file.split('.')[1] in ['jpg', 'png']):
                            image_found = True
                            self.annotation_canvas.load_image(os.path.join(path, file),
                                                              full_path=True)
                        elif i == len(files_folders) - 1:
                            image_found = True

                    # activate all entries within the File menu
                    self.file_menu.entryconfig(
                        "Open image (Ctrl+O)", state="normal")
                    self.file_menu.entryconfig(
                        "Close image (Ctrl+W)", state="normal")
                    self.file_menu.entryconfig(
                        "Save annotations (Ctrl+S)", state="normal")
                    self.file_menu.entryconfig(
                        "Delete keypoint (Del)", state="normal")
                    self.file_menu.entryconfig(
                        "Delete object (Ctrl+Del)", state="normal")
                    self.file_menu.entryconfig(
                        "Previous image (F7)", state="normal")
                    self.file_menu.entryconfig(
                        "Next image (F8)", state="normal")
                    self.file_menu.entryconfig(
                        "Import image (Ctrl+I)", state="normal")
                    self.file_menu.entryconfig(
                        "Export dataset (F5)", state="normal")
                    self.edit_menu.entryconfig(
                        "Import mask template", state="normal")
                    self.edit_menu.entryconfig(
                        "Save mask template", state="normal")
                    self.edit_menu.entryconfig(
                        "Mask template manager", state="normal")
                else:
                    valid_project = False
            else:
                valid_project = False
        else:  # path=""
            return

        if not valid_project:
            message = "This is not a valid project\n\n" +\
                      "A valid project has to contain a folder 'project' with " +\
                      "following files:\n" +\
                      "-skeleton.jpg or skeleton.png\n" +\
                      "-skeleton.json"
            tkmessagebox.showerror(title="Invalid Project",
                                   message=message)

    def delete_keypoint(self):
        """
        Decisive method to delete a keypoint of an object or a keypoint of the
        skeleton
        """
        if self.mode == 1:
            #delete a keypoint of the skeleton
            self.skeleton_canvas.delete_keypoint()
            return

        if self.annotation_canvas.mode == 0:
            # annotation_canvas is in keypoint annotation mode
            self.annotation_canvas.delete_keypoint()
        elif  self.annotation_canvas.mode == 1:
            # annotation_canvas is in mask mode
            self.annotation_canvas.delete_mask_point()

    def save(self):
        """
        Decisive method to save the annotations of the current image or the skeleton
        """
        if self.mode == 0:
            # annotation mode
            self.annotation_canvas.save()
        else:  # self.mode == 1:
            self.skeleton_canvas.save()

    def new_project(self):
        """
        Create a new project
        """
        NewProject(self)

    def export_dataset(self):
        """
        Export the project to a dataset of a chosen format
        """
        ExportDataset(self)

    def import_images(self):
        """
        Import images
        """
        # check if a project is loaded
        if self.wdir is None:
            return

        #import images
        first_file = True
        files_list = os.listdir(self.wdir)
        files = tkfiledialog.askopenfilenames(
            filetypes=[("Images", ".png .jpg")])

        if self.settings.ask_for_mask_template:
            AskMaskTemplate(self)
        else:
            self.settings.default_mask_template = None

        for filepath in files:

            if os.path.split(filepath)[1] in files_list:
                # there is a file with the same name in the project directory
                message = os.path.split(filepath)[1] + " exists yet in the project\n\n" +\
                    "Do you want to replace the current file?"
                answer = tkmessagebox.askyesno(title="Filename not unique",
                                               message=message)
                if answer:
                    #answer is True
                    core = os.path.split(filepath)[1].split(".")[0]

                    annotations_filename =  core + ".csv"
                    if annotations_filename in files_list:
                        os.remove(annotations_filename)

                    masks_filename = core + "_mask.json"
                    if masks_filename in files_list:
                        os.remove(masks_filename)
                else:
                    #answer is False
                    continue

            # copy the file
            src = filepath
            dst = os.path.join(self.wdir, os.path.split(filepath)[1])
            shutil.copy(src, dst)

            #save the mask template
            if self.settings.default_mask_template is not None:
                masks_dict = self.settings.default_mask_template
                masks_filename = self.wdir + "/" +\
                    os.path.split(filepath)[1].split(".")[0] + "_mask.json"

                f = open(masks_filename, 'w')
                json.dump(masks_dict, f)
                f.close()

            # Load the first image which is imported
            # under the condition that there is currently no image loaded
            if first_file and (self.annotation_canvas.image_name is None):
                first_file = False
                self.annotation_canvas.load_image(dst, full_path=True)


    def modify_settings(self):
        SettingsDialog(self)

    def update_visualisations(self):
        self.annotation_canvas.update_image(mode=0)
        self.skeleton_canvas.update_image(mode=0)

    def import_mask_template(self):
        ImportMaskTemplateDialog(self)

    def save_mask_template(self):
        SaveMaskTemplateDialog(self)

    def manage_mask_templates(self):
        MaskTemplateManager(self)

# %% Start mainloop


# adjust DPI to screen resolution
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# start mainloop
root = tk.Tk()

#set application icon
if os.path.exists("icon/Kantool_behaviour_icon.ico"):
    #this case will be executed when the application is run from the .py file
    root.iconbitmap("icon/Kantool_behaviour_icon.ico")
elif os.path.exists("_internal/icon/Kantool_behaviour_icon.ico"):
    #this case will be executed when the application is run from a .exe file
    #generated with pyinstaller
    root.iconbitmap("_internal/icon/Kantool_behaviour_icon.ico")

soft_dir = os.getcwd()
app = Application(master=root, program_dir=soft_dir)
app.mainloop()
