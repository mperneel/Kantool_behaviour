# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:05:13 2021

@author: Maarten

In this script, the AnnotationCanvas class is defined. AnnotationCanvas regulates
all modifications to the annotations
"""
#%% import packages
import os
import tkinter as tk
import tkinter.messagebox as tkmessagebox
import tkinter.filedialog as tkfiledialog
import numpy as np
import pandas as pd
import cv2
from PIL import Image, ImageTk

from general_image_canvas import GeneralImageCanvas

#%%main code

class AnnotationCanvas(GeneralImageCanvas):
    """
    AnnotationCanvas regulates all modifications to the annotations
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.skeleton = master.skeleton
        self.annotations = master.annotations
        self.settings = master.settings

        self.image_inter_scale = 1.0 #scale of self.image_inter
        self.image_inter = None #intermediary image matrix
        #basic modifications to self.image are done once and then stored
        #in self.image_inter to speed up the code
        self.image = None #image matrix
        self.image_inter_1 = None
        self.image_shown = None #matrix with shown image

        self.show_mask = True #True if masks should be drawn

        self.mode = None
        #0 keypoint annotation mode
        #1 mask mode
        #2 behaviour mode

        self.object_canvas_active = False

        self.bind("<Button-1>",
                  self.button_1)
        self.bind("<ButtonRelease-1>",
                  self.button_1_release)
        self.bind("<Button-3>",
                  lambda event: self.button_3())
        self.bind("<B1-Motion>",
                  self.motion_b1)
        self.bind("<Motion>",
                  self.motion)

    def update_image(self, mode=0):
        """
        Update image

        mode : int
            0 : the image is constructed from scratch\n
            1 : the code starts from the rescaled image with all non-active
            objects drawn. This mode is used to draw the currently active object/mask
            and the mouse circle\n
            2 : the code starts from the rescaled image with all objects/masks drawn.
            This mode is used to draw the mouse circle
            3: the code starts from scratch. The active object is emphasized by
            drawing a circle around it's keypoints

        """

        annotations = self.annotations

        if annotations.image_name is None:
            #no image is loaded
            #display nothing
            self.itemconfigure(self.image_photoimage, image=None)
            self._image_photoimage = None
            return

        #There is an image loaded

        #get image height and width
        image_height, image_width = annotations.image.shape[:2]

        #get scale and intercepts
        s = self.zoom_level
        dx = self.zoom_delta_x
        dy = self.zoom_delta_y

        #get annotations
        df = annotations.annotations

        #rescale image
        if (mode in [0, 3]) or (self.image_inter_scale != s):
            #resize self.image_inter according to scale s
            self.image_inter = cv2.resize(annotations.image,
                                          dsize=(int(image_width * s),
                                                 int(image_height * s)))
            self.image_inter_scale = s

        #draw all non-active items
        if (mode in [0, 3]) or (self.image_inter_scale != s):
            #draw all non-active objects
            for i in df.index:
                if i != annotations.object:
                    data_object = df.loc[i, :].to_numpy()

                    self.image_inter = self.draw_skeleton(self.image_inter, s, data_object)

            #draw all non-active masks
            if self.show_mask:
                for i in annotations.names_masks["obj"]:
                    if i != annotations.mask_id:
                        mask = annotations.annotation_points_masks.loc[annotations.annotation_points_masks["obj"]==i,\
                                                             ["x", "y"]].to_numpy()
                        color = [0, 0, 0]

                        self.image_inter = self.draw_mask(self.image_inter, mask,\
                                                          s, color=color)


        #draw all active items
        if mode in [0, 1, 3]:
            self.image_inter_1 = self.image_inter.copy()

            #draw skeleton of active object
            i = annotations.object
            data_object = df.loc[i, :].to_numpy()

            self.image_inter_1 = self.draw_skeleton(self.image_inter_1,s, data_object)

            #draw points of active mask
            if self.show_mask:

                #draw lines of mask
                mask = annotations.points_mask.copy()
                color = [255, 255, 0] #yellow

                if len(mask)>=3:
                    #draw segment
                    #identical to drawing segments of active object
                    mask_color = color
                    self.image_inter_1 = self.draw_segment(self.image_inter_1, mask,\
                                                         s, color=mask_color)

                #draw points of active mask
                for point in annotations.points_mask:
                    x = int(point[0] * s)
                    y = int(point[1] * s)

                    self.image_inter_1= cv2.circle(self.image_inter_1,
                                                 (x,y),
                                                 radius=self.settings.point_size,
                                                 color=[0,255,0],
                                                 thickness=-1)

        #draw circle around mouse/activated keypoint

        if mode in [0,1,2]:
            self.image_shown = self.image_inter_1.copy()

            if self.mode == 0:

                if annotations.keypoint_reactivated:
                    #draw circle around activated keypoint
                    x, y = (df.iloc[annotations.object,
                                    annotations.keypoint_index * 2: annotations.keypoint_index * 2 + 2]
                            * s).astype(int)
                else: #not self.keypoint_reactivated:
                    #draw circle around mouse
                    x = int(self.mouse_x  + self.zoom_delta_x)
                    y = int(self.mouse_y  + self.zoom_delta_y)

                color = self.skeleton.color[annotations.keypoint_index]
                cv2.circle(self.image_shown, (x, y),
                           radius=self.settings.circle_radius,
                           color=color,
                           thickness=self.settings.linewidth)
            else: #self.mode in [0, 2]:
                #if in mask mode, nothing should be drawn around the mouse
                pass

        elif mode == 3:
            #redraw re-activated object with circles around keyoints
            self.image_shown = self.image_inter_1.copy()

            if self.mode in [0, 2]:
                i = annotations.object
                data_object = df.loc[i, :].to_numpy()
                self.image_shown = \
                    self.draw_skeleton(self.image_shown,s, data_object, highlight=True)

        #slice self.image_shown so slice fits in self
        uw = self.winfo_width() - 2 * self.bd
        uh = self.winfo_height() - 2 * self.bd
        if (self.image_shown.shape[1] > uw) or\
            (self.image_shown.shape[0] > uh):
            self.image_shown = self.image_shown[dy : dy + uh,
                                                dx: dx + uw,
                                                :]

        #show image
        image_shown = Image.fromarray(self.image_shown)
        image_shown = ImageTk.PhotoImage(image_shown)

        self.itemconfigure(self.image_photoimage, image=image_shown)
        self._image_photoimage = image_shown

    def check_mode(self):
        self.master.object_canvas.check_mode()
        self.mode = self.master.object_canvas.mode

    def draw_segment(self, image, segment, z, color):
        """
        Draw segment on image

        Segments contains all the points which define the segment

        z is the scale of the image relative to the original image
        """
        #rescale coordinates within segment
        segment *= z

        #round coordinates and draw segment on image
        segment = np.int64(segment).reshape((-1, 1, 2))

        image= cv2.polylines(image,
                            [segment],
                            isClosed=True,
                            color=color,
                            thickness=self.settings.linewidth)
        return image

    def draw_mask(self, image, mask, z, color):
        """
        Draw mask on image

        a mask is a polygon defined by a list of points
        """
        #check if mask has enough points
        if len(mask) < 3:
            return image

        #rescale coordinates within mask
        mask *= z

        #round coordinates and draw mask on image
        mask = np.int64(mask).reshape((-1, 1, 2))

        image= cv2.fillPoly(image,
                            [mask],
                            color=color)


        return image

    def draw_skeleton(self, image, z, annotations, highlight=False):
        """
        Draw a skeleton on an image

        z is the scale of the image relative to the original image
        """

        #below, two totally independent for loops are defined
        #to assure the points are on top of the lines
        for j, _ in enumerate(self.skeleton.keypoints):
            if not np.isnan(annotations[2 * j]):
                x, y = (annotations[2 * j: 2 * j + 2] * z).astype(int)

                #draw lines
                parent_id = self.skeleton.parent[j]
                if (parent_id != -1) and\
                    (not np.isnan(annotations[2 * parent_id])):
                    end_point = (x, y)
                    start_point = annotations[2 * parent_id:
                                              2 * parent_id + 2]
                    start_point = tuple((start_point * z).astype(int))
                    color = self.skeleton.color[j]
                    cv2.line(image,
                             start_point,
                             end_point,
                             color=color,
                             thickness=self.settings.linewidth)

        for j, _ in enumerate(self.skeleton.keypoints):
            if not np.isnan(annotations[2 * j]):
                x, y = (annotations[2 * j: 2 * j + 2] * z).astype(int)
                #draw points
                color = self.skeleton.color[j]
                cv2.circle(image,
                           (x, y),
                           radius=self.settings.point_size,
                           color=color,
                           thickness=-1)

                if highlight:
                    cv2.circle(image,
                               (x, y),
                               radius=self.settings.circle_radius,
                               color=color,
                               thickness=self.settings.linewidth)

        return image

    def open_image(self):
        """
        Open a dialog to choose an image to load
        """
        #check if a project is opened
        if self.wdir is None:
            return

        #ask for a filepath
        filepath = tkfiledialog.askopenfilename()

        if filepath != "":
            #load the image (and annotations)
            self.load_image(filepath, full_path=True)

    def load_image(self, filename, full_path=True):
        """
        Decisive method to load an image, together with it's annotations (if
        availabe)

        Parameters
        ----------
        filename : string
            DESCRIPTION.
        full_path : bool, optional
            DESCRIPTION. The default is True.
        """

        #set wdir and image_name
        if full_path is True:
            wdir, image_name = os.path.split(filename)
            #check if image is in project folder
            if wdir != self.wdir:
                message = "The file you selected is not located in the project folder"
                tkmessagebox.showerror(title='Invalid file',
                                       message=message)
                return
        else: #full_path = False
            wdir = self.wdir
            image_name = filename

        #check if file is a valid image
        if (len(image_name.split(".")) > 1) and \
            image_name.split(".")[1] in ['jpg', 'png']:

            if self.annotations.currently_saved:
                #annotations are saved (or there is currenlty no image shown)
                self.import_image(image_name)
            else:
                #there are currently unsaved changes in the annotations
                message = "do you want to save the annotation changes you made " +\
                          "for the current image?"
                answer = tkmessagebox.askyesnocancel("Save modifications",
                                                     message=message)
                if answer is True:
                    #Save changes
                    self.save()
                    self.import_image(image_name)
                elif answer is False:
                    #Discard changes
                    self.import_image(image_name)
                #else: #answer==None
                    #nothing has to be done
        else:
            #there was selected an object, but it was not a supported image
            tkmessagebox.showerror("Invalid file",
                                   "Only files with the extension .jpg or .png are supported")

    def import_image(self, image_name):
        """
        Executive method to import image and load annotations (if available)
        """

        #Update image
        self.annotations.import_image(image_name)

        #save image matrix also as an attribute in this object
        self.image = self.annotations.image

        #Update title of application
        self.master.master.title("Kantool behaviour " + image_name)

        #load data of objects and masks in object_canvas
        self.master.object_canvas.load_data()

        #Set initial zoom level
        self.reset_zoom_level()

        #Update image
        self.new_object()

        #activate correct object based on activate tab of object_canvas
        self.master.object_canvas.activate_default_object()

        self.update_image(mode=0)

        if self.mode == 2:
            self.update_image(mode=3)

    def reload_image(self):
        if self.annotations.image_name is not None:
            self.import_image(self.annotations.image_name)

    def reset_parameters(self):
        """
        Reset attributes to their default value
        """
        self.zoom_level = 1.0
        self.zoom_delta_x = 0
        self.zoom_delta_y = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.image_inter_scale = 1.0

        self.image = None
        self.image_inter = None
        self.image_inter_1 = None
        self.image_shown = None

        self.image_photoimage = self.create_image(self.bd, self.bd, anchor='nw')

        self.annotations.reset_parameters()

    def switch_image(self, direction=1):
        """
        Load the next/previous image in the working directory
        """

        if self.wdir != None and self.annotations.image_name != None:
            #Check if there is an image loaded

            #list all files within working directory
            files = np.array(os.listdir(self.wdir))

            #get index of current image
            file_number = np.argmax(files == self.annotations.image_name)

            #look for next/previous image
            keep_looking = True
            while keep_looking is True:
                if file_number == len(files) - 1:
                    if direction == 1:
                        file_number = 0
                    else:
                        file_number += direction
                elif file_number == 0:
                    if direction == -1:
                        file_number = len(files) - 1
                    else:
                        file_number += direction
                else:
                    file_number += direction

                image_name = files[file_number]

                #check if file extension is correct
                if (len(image_name.split(".")) > 1) and\
                    (image_name.split(".")[1] in ['jpg', 'png']):
                    keep_looking = False
                    #remark: if current image is the only image in the
                    #folder, the while loop will be ended once we
                    #re-encounter the name of the current image

            #load image
            self.load_image(image_name, full_path=False)

    def save(self):
        """
        Save the annotations
        """
        self.annotations.save()

    def keypoint_searching(self, event):
        """
        Update search circle around the mouse

        Parameters
        ----------
        event : tkinter.Event
            Motion event containing the position of the mouse
        """

        self.mouse_x = event.x - self.bd
        self.mouse_y = event.y - self.bd

        if self.image_shown is not None:
            self.mouse_x = max(min(self.mouse_x, self.image_shown.shape[1]), 0)
            self.mouse_y = max(min(self.mouse_y, self.image_shown.shape[0]), 0)

        if self.annotations.image is not None:
            self.update_image(mode=2)

    def motion_b1(self, event):
        """
        Desicive method to move a keypoint

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """
        if self.mode ==2:
            #behaviour mode
            return

        if self.annotations.keypoint_reactivated or\
            self.annotations.new_keypoint_created:
            self.move_current_keypoint(event)
        elif self.mode == 1:
            self.update_point_mask(event)

    def move_current_keypoint(self, event):
        """
        Executive method to move a keypoint

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """
        #get image coordinates for new point
        x, y = self.get_image_coordinates(event)

        #update keypoint coordinates
        self.annotations.update_keypoint(x, y)

        #update mouse positions
        self.mouse_x = event.x - self.bd
        self.mouse_y = event.y - self.bd

        if self.image_shown is not None:
            self.mouse_x = max(min(self.mouse_x, self.image_shown.shape[1]), 0)
            self.mouse_y = max(min(self.mouse_y, self.image_shown.shape[0]), 0)

        #update the shown image
        self.update_image(mode=1)

    def update_point_mask(self, event):

        if not self.master.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #set saved state to false
        self.currently_saved = False

        #set object_confirmed state to False
        self.current_mask_confirmed = False

        #get image coordinates for point
        x, y = self.get_image_coordinates(event)

        #update position of currently active point
        self.annotations.update_point_mask(x, y)

        #update the shown image
        self.update_image(mode=1)

    def activate_next_keypoint_searching(self):
        """
        Update all attributes so the next missing keypoint can be looked for.
        If an object is complete, a new object will be created
        """
        self.annotations.activate_next_missing_keypoint()

        #update object canvas
        self.master.object_canvas.load_data()

        #update skeleton canvas if required
        if self.settings.highlight_skeleton_keypoint:
            self.master.skeleton_canvas.update_image(mode=2)

        self.update_image(mode=0)

    def button_1(self, event):
        """
        Decisive method to re-activate a keypoint or draw a new keypoint

        If currently no keypoint is re-activated, a new keypoint can be drawn or
        a keypoint can be specified

        If currently a keypoint is re-activated, the keypoint can become
        deactivated or another keypoint can be reactivated, but no new keypoint
        can be drawn
        """

        #check if an image was loaded
        if self.annotations.image_name is None:
            return

        #get scale
        s = self.zoom_level

        #get image coordinates of event
        x, y = self.get_image_coordinates(event)
        location = np.array([x, y])

        if self.mode == 1:
            #annotation canvas is in mask mode

            if not self.master.object_canvas.masks_visible:
                #if masks are not visible, no modifications to the masks may be done
                return

            #get image dimensions
            h_img = self.annotations.image.shape[0]
            w_img = self.annotations.image.shape[1]

            #check if a valid point was added
            if (x > w_img) or (y > h_img):
                return

            sensitivity = self.settings.reactivation_sensitivity / s
            magnetic_border = self.settings.magnetic_border / s
            self.annotations.new_mask_point(x, y,
                                            sensitivity,
                                            magnetic_border)

        elif self.mode == 0:
            #annotation canvas is in keypoint annotation mode

            object_id, keypoint_id, min_distance =\
                self.annotations.closest_keypoint(location)

            if object_id is not None:
                #object_id will be None if no object or keypoint was yet declared

                sensitivity = self.settings.reactivation_sensitivity / s
                if (not np.isnan(min_distance)) and\
                    (min_distance < sensitivity):

                    #re-activate a keypoint
                    self.annotations.activate_keypoint(object_id, keypoint_id)

                    #update object_canvas
                    self.master.object_canvas.list_objects.select_clear(0, tk.END)
                    #blue color
                    self.master.object_canvas.list_objects.select_set(self.annotations.object)
                    #underlining
                    self.master.object_canvas.list_objects.activate(self.annotations.object)

                    self.update_image(mode=0)
                    return

            if self.annotations.keypoint_reactivated:
                #deactivate keypoint
                self.annotations.keypoint_reactivated = False
            else:
                #create a new keypoint
                self.annotations.new_keypoint(x, y)

                #update object names in object canvas
                #necessary to show the name of the last object if it was an empty
                #preallocated object previously
                self.master.object_canvas.load_data()

                #update image
                self.update_image(mode=1)
        else: #self.mode == 2:
            #behaviour mode

            #activate whole object if applicable
            object_id, keypoint_id, min_distance =\
                self.annotations.closest_keypoint(location)

            if object_id is not None:
                #object_id will be None if no object or keypoint was yet declared

                sensitivity = self.settings.reactivation_sensitivity / s
                if (not np.isnan(min_distance)) and\
                    (min_distance < sensitivity):

                    #re-activate a keypoint
                    self.annotations.activate_keypoint(object_id, keypoint_id)

                    #update object_canvas
                    self.master.object_canvas.list_objects.select_clear(0, tk.END)
                    #blue color
                    self.master.object_canvas.list_objects.select_set(self.annotations.object)
                    #underlining
                    self.master.object_canvas.list_objects.activate(self.annotations.object)

                    #update behaviour
                    self.master.object_canvas.update_frm_behaviour()

                    #update annotation canvas
                    self.update_image(mode=3)

                    return

    def button_3(self):
        """
        Method to skip the current keypoint where we are looking for or
        to de-activate the currently activated keypoint
        """
        #check if an image was loaded
        if self.annotations.image_name is None:
            return

        if self.mode == 1:
            return

        #there is an image loaded
        #activate the next missing keypoint
        #if a keypoint was re-activated previously, it will become de-activated
        #and the object and keypoint in the memory attributes will become activated
        self.annotations.activate_next_missing_keypoint()

        #update skeleton canvas if required
        if self.settings.highlight_skeleton_keypoint:
            self.master.skeleton_canvas.update_image(mode=2)

        self.update_image(mode=2)

    def new_object(self, remove_uncomplete=False):
        """
        Create a new object

        Parameters
        ----------
        remove_uncomplete : bool, optional
            Remove the current mask if it is not complete (less than three points).
            The default is False.
        """

        if self.mode == 1:
            #if we are in mask mode, a new mask should be initiated
            self.new_mask(remove_uncomplete=remove_uncomplete)
            return

        self.annotations.new_object()

        #load all names still present in object_canvas
        self.master.object_canvas.load_data()

        #update image
        self.update_image(mode=0)

    def new_mask(self, remove_uncomplete=False):
        """
        Confirm current mask
        """

        if not self.master.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #confirm current mask
        self.annotations.new_mask(remove_uncomplete=remove_uncomplete)

        #update image
        self.update_image(mode=0)

    def delete_keypoint(self):
        """
        Delete the currently activated keypoint
        """
        if self.annotations.keypoint_reactivated:

            #delete keypoint
            self.annotations.delete_keypoint()

            #update application to look for next keypoint
            self.activate_next_keypoint_searching()

            #update image
            self.update_image(mode=1)

    def delete_mask(self, mask_id=None, mask_name=None):

        if not self.master.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        self.annotations.delete_mask(mask_id=mask_id,
                                     mask_name=mask_name)

        self.update_image(mode=0)

    def delete_mask_point(self):
        """
        Delete the currently active point of mask
        """

        if not self.master.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        if self.annotations.point_mask_active:
            #delete point
            self.annotations.delete_mask_point()

            #update the shown image
            self.update_image(mode=1)

    def button_1_release(self, event):
        """
        Actions to take when left mouse button is released

        If a new keypoint was created, the search for the next keypoint may be
        activated

        If a keypoint was activated and there is clicked in another spot of the
        image, the search for the next keypoint may be activated
        """

        #check if an image was loaded
        if self.annotations.image_name is None:
            return

        self.mouse_x = event.x - self.bd
        self.mouse_y = event.y - self.bd

        if self.image_shown is not None:
            self.mouse_x = max(min(self.mouse_x, self.image_shown.shape[1]), 0)
            self.mouse_y = max(min(self.mouse_y, self.image_shown.shape[0]), 0)

        if self.annotations.new_keypoint_created:
            self.annotations.new_keypoint_created = False

        if not self.annotations.keypoint_reactivated:
            self.activate_next_keypoint_searching()

    def delete_object(self, obj_name=None, obj_id=None):
        """
        Delete the currently active object

        Only one of the inputs obj_name and obj_id may be specified

        Parameters
        ----------
        obj_name : str, optional
            Object name. The default is None.
        obj_id : int, optional
            object identifier integer. The default is None.
        """
        #delete object
        self.annotations.delete_object(obj_name, obj_id)

        #update image
        self.update_image(mode=0)

    def close_image(self):
        """
        Close the current image
        """

        if self.annotations.currently_saved is False:
            #there are currently unsaved changes in the annotations
            message = "do you want to save the annotation changes you made " +\
                      "for the current image?"
            answer = tkmessagebox.askyesnocancel("Save modifications",
                                                 message=message)
            if answer is True:
                #Save changes
                self.save()

                #set state of self.currently_saved to True
                self.currently_saved = True

        #reset annotation_canvas
        self.reset_parameters()
        self.image = None
        self.image_inter = None
        self.image_shown = None

        #update image
        self.update_image(mode=0)

    def prepare_for_skeleton_mode(self):
        """
        Prepare the AnnotationCanvas to switch to skeleton mode
        """
        #check if the current changes in self.annotations should be saved
        if (not self.annotations.currently_saved) and\
            (self.annotations.image_name is not None):
            #there are currently unsaved changes in the annotations
            message = "do you want to save the annotation changes you made " +\
                      "for the current image?"
            answer = tkmessagebox.askyesnocancel("Save modifications",
                                                 message=message)
            if answer is True:
                #Save changes
                self.save()

            #re-import image
            self.import_image(self.annotations.image_name)

    def motion(self, event):
        """
        Decisive method to invoke (or not) methods when the mouse moves

        Parameters
        ----------
        event : tkinter.event
            Motion event
        """
        if self.mode == 2:
            #behaviour_mode
            return

        if self.object_canvas_active:
            self.activate_next_keypoint_searching()
            self.object_canvas_active = False
        if not self.annotations.keypoint_reactivated:
            self.keypoint_searching(event)

    def get_image_coordinates(self, event):
        """
        Get the image coordinates. The image coordinates are calculated by
        correcting the event coordinates for translation and scale used during
        visualisation

        Parameters
        ----------
        event : tkinter.Event
            Motion event

        Returns
        -------
        x : float
            x coordinate (horizontal axis, origin=left side)
        y : float
            y coordinate (vertical axis, origin=top)

        """
        #get scale of image
        s = self.zoom_level

        #get x and y coordinate of event
        #self.bd: border size of canvas, attribute declared in the
        #general_image_canvas class
        x = (event.x + self.zoom_delta_x - self.bd) / s
        y = (event.y + self.zoom_delta_y - self.bd) / s

        #limit coordinates to size image
        x = max(min(x, self.annotations.image.shape[1] - 1), 0)
        y = max(min(y, self.annotations.image.shape[0] - 1), 0)

        return (x, y)