# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 15:33:50 2021

@author: Maarten

In this script, the ExportDataset class is defined. The ExportDataset class
construct a wizard to export a keypoint dataset to a dataset format of choice
"""

#%% import packages
import os
import json
import shutil
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
import random
import pandas as pd
import cv2
import numpy as np

#%%

class ExportDataset(tk.Toplevel):
    """
    The ExportDataset class construct a wizard to export a keypoint dataset to
    a dataset format of choice

    Attributes
    -----
    self.master : Application
        Master object which invokes ExportDataset

    self.dataset_types : list
        Dataset types to which the project can be exported

    self.skeleton : Skeleton
        Skeleton object containing all information about the used skeleton

    self.dataset_title : tkinter.StringVar
        Title of the exported dataset

    self.wdir : tkinter.StringVar
        Directory to store exported dataset

    self.dataset_type : tkinter.StringVar
        Dataset type

    Methods
    -----
    self.choose_directory
        Invoke dialog to choose a directory

    self.resize_window
        Resize the entry fields if the size of the new-project-dialog window
        changes

    self.confirm
        Confirm the title, directory and type and export the dataset

    self.to_psota_2019
        Export dataset to Psota_2019 format
    """
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.master = master

        self.dataset_types = ["Perneel", "Psota_2019"]
        self.skeleton = self.master.skeleton

        #set default size
        self.geometry('600x360')

        #set title
        self.title("Export dataset")

        #create tkinter variables
        self.dataset_title = tk.StringVar() #title of the exported dataset
        self.wdir = tk.StringVar() #directory to store exported dataset
        self.dataset_type = tk.StringVar() #dataset type
        self.train_perc = tk.StringVar(value='100') #% of data in training split
        self.val_perc = tk.StringVar(value='0') #% of data in validation
        self.test_perc = tk.StringVar(value='0') #% of data in test split
        self.include_empty = tk.IntVar(value=0)
        #include images without object in exported dataset
        self.include_video = tk.IntVar(value=0)
        #include corresponding videos in dataset

        #set memory attributes for the split-percentage attributes
        self.train_perc.old_value = '100'
        self.val_perc.old_value = '0'
        self.test_perc.old_value = '0'

        #use .trace() to add a method to the tkinter variables that takes action
        #if the user entered an invalid value
        self.train_perc.trace('w', self.check_integer_value)
        self.val_perc.trace('w', self.check_integer_value)
        self.test_perc.trace('w', self.check_integer_value)

        #create frames
        """
        |---------------|
        |  frame_title  |
        |---------------|
        |---------------|
        |   frame_dir   |
        |---------------|
        |---------------|
        |  frame_type   |
        |---------------|
        |---------------|
        |  frame_split  |
        |---------------|
        |---------------|
        | frame_options |
        |---------------|
        """
        self.frame_title = tk.Frame(self)
        self.frame_dir = tk.Frame(self)
        self.frame_type = tk.Frame(self)
        self.frame_split = tk.Frame(self)
        self.frame_options = tk.Frame(self)
        frame_split_labels = tk.Frame(self.frame_split)
        frame_split_fields = tk.Frame(self.frame_split)
        frame_options_fields = tk.Frame(self.frame_options)

        #create labels
        self.label_title = tk.Label(self.frame_title,
                                    text="Title", width=8, anchor='w')
        self.label_dir = tk.Label(self.frame_dir,
                                  text='Directory', width=8, anchor='w')
        self.label_type = tk.Label(self.frame_type,
                                   text="Type", width=8, anchor='w')
        self.label_split = tk.Label(self.frame_split,
                                   text="Split", width=8, anchor='w')
        self.label_train_perc = tk.Label(frame_split_labels,
                                   text="Train (%)", anchor='w')
        self.label_val_perc = tk.Label(frame_split_labels,
                                   text="Validation (%)", anchor='w')
        self.label_test_perc = tk.Label(frame_split_labels,
                                   text="Test (%)", anchor='w')
        self.label_options = tk.Label(self.frame_options,
                                      text="Options", anchor="w")
        self.label_include_empty = tk.Label(frame_options_fields,
                                            text="Include images without objects",
                                            anchor="w")
        self.label_include_video = tk.Label(frame_options_fields,
                                            text="Include corresponding video files",
                                            anchor="w")

        #create entry fields
        self.field_title = tk.Entry(self.frame_title,
                                    width=60,
                                    textvariable=self.dataset_title)
        self.field_dir = tk.Entry(self.frame_dir,
                                  width=57,
                                  textvariable=self.wdir)
        self.field_train_perc = tk.Entry(self.frame_split,
                                          width=3,
                                          textvariable=self.train_perc)
        self.field_val_perc = tk.Entry(self.frame_split,
                                        width=3,
                                        textvariable=self.val_perc)
        self.field_test_perc = tk.Entry(self.frame_split,
                                        width=3,
                                        textvariable=self.test_perc)

        #create checkboxes/checkbuttons
        self.checkbtn_include_empty = tk.Checkbutton(frame_options_fields,
                                                     variable=self.include_empty,
                                                     height=1)
        self.checkbtn_include_video = tk.Checkbutton(frame_options_fields,
                                                     variable=self.include_video,
                                                     height=1)

        #create drop down boxes
        self.field_type = ttk.Combobox(self.frame_type,
                                       state="readonly",
                                       width=22,
                                       textvariable=self.dataset_type)

        #add values to drop down boxes
        self.field_type['values'] = tuple(self.dataset_types)

        #set default value for drop down box
        self.dataset_type.set(self.dataset_types[0])

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

        self.button_dir = tk.Button(self.frame_dir,
                                    text="...",
                                    image=pixel,
                                    compound="center",
                                    width=30,
                                    height=22,
                                    command=lambda: self.choose_directory(self.wdir))

        self.button_ok = tk.Button(self,
                                   text="OK",
                                   command=self.confirm)

        #pack all elements
        #frame_title
        self.label_title.pack(side='left', anchor='nw', padx=5)
        self.field_title.pack(anchor='nw')

        #frame_dir
        self.label_dir.pack(side='left', anchor='nw', padx=5)
        self.field_dir.pack(side='left', anchor='nw')
        self.button_dir.pack(anchor='nw')

        #frame_type
        self.label_type.pack(side='left', anchor='nw', padx=5)
        self.field_type.pack(anchor='nw')

        #frame_split
        self.label_split.pack(side='left', anchor='nw', padx=5)

        self.label_train_perc.pack(side='top', anchor='nw', padx=5)
        self.label_val_perc.pack(side='top', anchor='nw', padx=5)
        self.label_test_perc.pack(side='top', anchor='nw', padx=5)
        frame_split_labels.pack(side='left', anchor='nw')

        self.field_train_perc.pack(side='top', anchor='nw', padx=5)
        self.field_val_perc.pack(side='top', anchor='nw', padx=5)
        self.field_test_perc.pack(side='top', anchor='nw', padx=5)
        frame_split_fields.pack(side='left', anchor='nw')

        #frame_options
        self.label_options.pack(side='left', anchor='nw', padx=5)

        self.checkbtn_include_empty.grid(sticky="w", row=0, column=0)
        self.checkbtn_include_video.grid(sticky="w", row=1, column=0)
        self.label_include_empty.grid(sticky="w", row=0, column=1)
        self.label_include_video.grid(sticky="w", row=1, column=1)
        frame_options_fields.pack(side='left', anchor="nw")

        #self
        self.frame_title.pack(pady=5, anchor='nw')
        self.frame_dir.pack(pady=5, anchor='nw')
        self.frame_type.pack(pady=5, anchor='nw')
        self.frame_split.pack(pady=5, anchor='nw')
        self.frame_options.pack(pady=5, anchor='nw')
        self.button_ok.pack(pady=5, side="bottom")

        #set focus on first entryfield
        self.field_title.focus()

        #bind hitting return/enter key to invocation of button/checkbox
        self.bind_class("Button",
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

    def resize_window(self):
        """
        Resize the entry fields if the size of the new-project-dialog window
        changes
        """
        #get useable width
        uw = self.winfo_width()

        self.field_title.config(width=int((uw - 115)/10))
        self.field_dir.config(width=int((uw - 150)/10))

    def confirm(self):
        """
        Confirm the title, directory, type, dataset split and export the dataset

        Depending on the dataset type, the appropriate method, responsible for
        the actual exporting, will be called
        """

        #normalize dataset split percentages so they sum up to 100%
        #if this would not be the case

        #get values
        train_perc =  int(self.train_perc.get())
        val_perc =  int(self.val_perc.get())
        test_perc =  int(self.test_perc.get())

        #calculate sum of split percentages
        split_sum = train_perc + val_perc + test_perc

        #renormalise if necessary
        if split_sum != 100:
            train_perc = round(train_perc / split_sum)
            val_perc = round(val_perc / split_sum)
            test_perc = round(test_perc / split_sum)

            #if all three splits are equal, the previous calculations
            #will result in a sum of 99 instaed of 100
            if train_perc + val_perc + test_perc != 100:
                train_perc = 100 - val_perc - test_perc

            #assign new values
            self.train_perc.set(str(train_perc))
            self.val_perc.set(str(val_perc))
            self.test_perc.set(str(test_perc))

        #get dataset type
        dataset_type = self.dataset_type.get()

        if dataset_type == "Psota_2019":
            self.to_psota_2019()
        elif dataset_type == "Perneel":
            self.to_perneel()
        else:
            message = "something went wrong"
            tkmessagebox.showerror(title="Error",
                                   message=message)
            return

    def to_psota_2019(self):
        """
        Export dataset to Psota_2019 format.
        """

        #list all valid images
        files_list = os.listdir()
        files = []
        for filename in files_list:
            if (len(filename.split(".")) == 2) and\
                (filename.split(".")[-1] in ['png', 'jpg']) and\
                (filename.split(".")[0] + ".json" in files_list):
                #file is an image (.jpg or .png), accompanied with a .json file
                #with annotations

                if self.include_empty.get() == 1:
                    #all images may be included in the exported dataset
                    files.append(filename)
                else: #self.include_empty.get() == 0:
                    #only images with annotated objects may be included

                    #read annotations
                    with open(filename.split(".")[0] + ".json") as f:
                        dict_annotations = json.load(f)

                    if "keypoints" in dict_annotations:
                        n_keypoints = len(dict_annotations["keypoints"]\
                                          [self.skeleton.keypoints[0]])
                        if n_keypoints > 0:
                            #image contains annotated objects
                            files.append(filename)

        #if no valid files are present, end method
        if len(files) == 0:
            return

        #create splits (train, validation, test)

        #shuffle files
        random.shuffle(files) #shuffles the list in place

        val_size = round(float(self.val_perc.get()) / 100 * len(files))
        test_size = round(float(self.test_perc.get()) / 100 * len(files))

        files_val =  files[:val_size]
        files_test = files[val_size: val_size + test_size]
        files_train = files[val_size + test_size:] #all the other images

        #sort the splits in place
        files_train.sort()
        files_val.sort()
        files_test.sort()

        lists_files = [files_train, files_val, files_test]
        suffices = ["_train", "_val", "_test"]

        for split in range(3):
            files = lists_files[split]

            if len(files) > 0:
                #check if there are filenames in files

                #construct export path and make all directories
                try:
                    export_path = os.path.join(self.wdir.get(),
                                               self.dataset_title.get() + suffices[split])
                    os.mkdir(export_path)
                    os.mkdir(os.path.join(export_path, "images"))
                    if self.include_video:
                        os.mkdir(os.path.join(export_path, "video"))
                except FileExistsError:
                    message = export_path + " already exists\n\n" +\
                              "Do you want to replace the existing folder?"
                    answer = tkmessagebox.askyesnocancel(title="Error",
                                                         message=message)
                    if answer is None:
                        #Destroy wizard
                        self.destroy()
                    if answer:
                        #answer is True/Yes
                        #replace directories
                        shutil.rmtree(export_path)
                        os.mkdir(export_path)
                        os.mkdir(os.path.join(export_path, "images"))
                    else:
                        #answer is False/No
                        #return to wizard and set focus on first entryfield
                        self.field_title.focus()
                        self.field_title.select_range(0, "end")
                        return

                #create export dictionary
                dataset_dict = {}

                i = 0
                for filename in files:
                    if (len(filename.split(".")) == 2) and\
                        (filename.split(".")[-1] in ['png', 'jpg']) and\
                        (filename.split(".")[0] + ".json" in files_list):
                        #file is an image (.jpg or .png), accompanied with a .json file
                        #with annotations

                        #read image
                        image = cv2.imread(filename)

                        #read annotations
                        with open(filename.split(".")[0] + ".json") as f:
                            dict_annotations = json.load(f)

                        #apply masks (if present)
                        if "masks" in dict_annotations:
                            masks = dict_annotations["masks"]

                            #apply masks
                            for key in masks:
                                #extract edges of mask
                                points_dict = masks[key]["points"]
                                mask = np.empty(shape=(0,2))
                                for point_key in points_dict:
                                    x = points_dict[point_key]['x']
                                    y = points_dict[point_key]['y']
                                    mask = np.append(mask,[[x, y]], axis=0)

                                #round coordinates and draw mask on image
                                mask = np.int64(mask).reshape((-1, 1, 2))

                                image= cv2.fillPoly(image,
                                                    [mask],
                                                    color=[0,0,0])

                        #get keypoint annotations
                        if "keypoints" in dict_annotations:
                            dict_keypoints = {}
                            for key, item in dict_annotations["keypoints"].items():
                                coordinates = np.array(item)
                                dict_keypoints[key + "_x"] = coordinates[:,0].tolist()
                                dict_keypoints[key + "_y"] = coordinates[:,1].tolist()

                            df_keypoints = pd.DataFrame(dict_keypoints)
                            del dict_keypoints

                            if len(df_keypoints) > 0:
                                objects_present = True
                            else: #len(df_keypoints) == 0:
                                #no objects (annotated) on image
                                objects_present = False

                        #Python is zero based, Matlab (and Psota) one based, therefore
                        #we have to increase all locations with one
                        df_keypoints = df_keypoints + 1
                        #replace NaN with zero
                        df_keypoints = df_keypoints.fillna(0)

                        #construct dictionary for image
                        dict_image = {}
                        dict_image["image"] = "images/" + filename

                        for j, keypoint in enumerate(self.skeleton.keypoints):
                            if objects_present:
                                #add keypoint coordinates
                                dict_image[keypoint] = \
                                    df_keypoints.iloc[:, 2 * j: 2 * j + 2].\
                                    to_numpy().tolist()
                            else:
                                #no objects present on image
                                dict_image[keypoint] = []

                        #save image
                        cv2.imwrite(os.path.join(export_path, "images", filename),
                                    image)

                        #copy video file if present
                        if self.include_video:
                            extensions = [".mp4", ".avi", ".mov"]
                            for ext in extensions:
                                video_name = filename.split(".")[0] + ext
                                if video_name in files_list:
                                    src = video_name
                                    dst = os.path.join(export_path, "video", video_name)
                                    shutil.copyfile(src, dst)

                        #add image dictionary to dataset dictionary
                        dataset_dict[str(i)] = dict_image
                        i += 1

                #write json file
                os.chdir(export_path)
                file = open("annotations.json", "w")
                json.dump(dataset_dict, file, indent=2)
                file.close()
                #return to project directory
                os.chdir(self.master.wdir)

        #Destroy wizard
        self.destroy()

    def to_perneel(self):
        """
        Export dataset to Psota_2019 format.
        """

        #list all valid images
        files_list = os.listdir()
        files = []
        for filename in files_list:
            if (len(filename.split(".")) == 2) and\
                (filename.split(".")[-1] in ['png', 'jpg']) and\
                (filename.split(".")[0] + ".json" in files_list):
                #file is an image (.jpg or .png), accompanied with a .json file
                #with annotations

                if self.include_empty.get() == 1:
                    #all images may be included in the exported dataset
                    files.append(filename)
                else: #self.include_empty.get() == 0:
                    #only images with annotated objects may be included

                    #read annotations
                    with open(filename.split(".")[0] + ".json") as f:
                        dict_annotations = json.load(f)

                    if "keypoints" in dict_annotations:
                        n_keypoints = len(dict_annotations["keypoints"]\
                                          [self.skeleton.keypoints[0]])
                        if n_keypoints > 0:
                            #image contains annotated objects
                            files.append(filename)

        #if no valid files are present, end method
        if len(files) == 0:
            return

        #create splits (train, validation, test)

        #shuffle files
        random.shuffle(files) #shuffles the list in place

        val_size = round(float(self.val_perc.get()) / 100 * len(files))
        test_size = round(float(self.test_perc.get()) / 100 * len(files))

        files_val =  files[:val_size]
        files_test = files[val_size: val_size + test_size]
        files_train = files[val_size + test_size:] #all the other images

        #sort the splits in place
        files_train.sort()
        files_val.sort()
        files_test.sort()

        lists_files = [files_train, files_val, files_test]
        suffices = ["_train", "_val", "_test"]

        for split in range(3):
            files = lists_files[split]

            if len(files) > 0:
                #check if there are filenames in files

                #construct export path and make all directories
                try:
                    export_path = os.path.join(self.wdir.get(),
                                               self.dataset_title.get() + suffices[split])
                    os.mkdir(export_path)
                    os.mkdir(os.path.join(export_path, "images"))
                    if self.include_video:
                        os.mkdir(os.path.join(export_path, "video"))
                except FileExistsError:
                    message = export_path + " already exists\n\n" +\
                              "Do you want to replace the existing folder?"
                    answer = tkmessagebox.askyesnocancel(title="Error",
                                                         message=message)
                    if answer is None:
                        #Destroy wizard
                        self.destroy()
                    if answer:
                        #answer is True/Yes
                        #replace directories
                        shutil.rmtree(export_path)
                        os.mkdir(export_path)
                        os.mkdir(os.path.join(export_path, "images"))
                    else:
                        #answer is False/No
                        #return to wizard and set focus on first entryfield
                        self.field_title.focus()
                        self.field_title.select_range(0, "end")
                        return

                #create export dictionary
                dataset_dict = {}

                i = 0
                for filename in files:
                    if (len(filename.split(".")) == 2) and\
                        (filename.split(".")[-1] in ['png', 'jpg']) and\
                        (filename.split(".")[0] + ".json" in files_list):
                        #file is an image (.jpg or .png), accompanied with a .json file
                        #with annotations

                        #read image
                        image = cv2.imread(filename)

                        #read annotations
                        with open(filename.split(".")[0] + ".json") as f:
                            dict_annotations = json.load(f)

                        #apply masks (if present)
                        if "masks" in dict_annotations:
                            masks = dict_annotations["masks"]

                            #apply masks
                            for key in masks:
                                #extract edges of mask
                                points_dict = masks[key]["points"]
                                mask = np.empty(shape=(0,2))
                                for point_key in points_dict:
                                    x = points_dict[point_key]['x']
                                    y = points_dict[point_key]['y']
                                    mask = np.append(mask,[[x, y]], axis=0)

                                #round coordinates and draw mask on image
                                mask = np.int64(mask).reshape((-1, 1, 2))

                                image= cv2.fillPoly(image,
                                                    [mask],
                                                    color=[0,0,0])

                        #get keypoint annotations
                        if "keypoints" in dict_annotations:
                            dict_keypoints = {}

                            for key, item in dict_annotations["keypoints"].items():
                                coordinates = np.array(item)

                                #Python is zero based, exported coordinates are
                                #one based, therefore we have to increase all
                                #locations with one
                                coordinates = coordinates + 1

                                #In the perneel convention, nan values are
                                #kept as nan (and not replaced by zeros)

                                #add to dict_keypoints
                                dict_keypoints[key] = coordinates.tolist()

                        else: #"keypoints" not in dict_annotations:
                            for j, keypoint in enumerate(self.skeleton.keypoints):
                                dict_keypoints[keypoint] = []

                        #get behaviour annotations in right format
                        behaviour_list = []
                        for key, item in dict_annotations["behaviour"]["behaviour"].items():
                            behaviour_list.append(item)

                        #construct dictionary for image
                        dict_image = {}
                        dict_image["image"] = "images/" + filename
                        dict_image["keypoints"] = dict_keypoints
                        dict_image["behaviour"] = behaviour_list
                        dict_image["masks"] = dict_annotations["masks"]

                        #save image
                        cv2.imwrite(os.path.join(export_path, "images", filename),
                                    image)

                        #copy video file if present
                        if self.include_video:
                            extensions = [".mp4", ".avi", ".mov"]
                            for ext in extensions:
                                video_name = filename.split(".")[0] + ext
                                if video_name in files_list:
                                    src = video_name
                                    dst = os.path.join(export_path, "video", video_name)
                                    shutil.copyfile(src, dst)

                        #add image dictionary to dataset dictionary
                        dataset_dict[str(i)] = dict_image
                        i += 1

                #write json file
                os.chdir(export_path)
                file = open("annotations.json", "w")
                json.dump(dataset_dict, file, indent=2)
                file.close()
                #return to project directory
                os.chdir(self.master.wdir)

        #Destroy wizard
        self.destroy()

    def check_integer_value(self, *args):
        """
        Check if the changes to self.train_perc, self.val_perc or self.test_perc still
        result in a valid entry.

        If the changes would result in an invalid entry (not an integer in the
        interval [0, 100]), the changes are undone by replacing the invalid
        entry with the value stored in the attribute .old_value

        If an integer greater than 100 is entered, the value is floored to 100
        """

        for textvar in [self.train_perc, self.val_perc, self.test_perc]:
            if textvar.get().isdigit():
                #the current value only contains digits; accept this
                if float(textvar.get()) > 100:
                    #the current value is too high, floor to 100
                    textvar.set('100')
                #update textvar.old_value
                textvar.old_value = textvar.get()
            elif textvar.get() == '':
                #the field is empty (equal to a zero entry); accept this
                #update textvar.old_value
                textvar.old_value = textvar.get()
            else:
                # there's non-digit characters in the input; reject this
                textvar.set(textvar.old_value)
