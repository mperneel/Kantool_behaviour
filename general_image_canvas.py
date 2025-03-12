# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:06:49 2021

@author: Maarten

In this script the class GeneralImageCanvas is defined. This class is a
subclass of tk.Canvas and is extended with multiple methods to zoom and move
images. GeneralImageCanvas is the parent class of SkeletonCanvas and
AnnotationCanvas
"""
#%% import packages
import tkinter as tk

#%%
class GeneralImageCanvas(tk.Canvas):
    """
    Subclass of tk.Canvas, extended with multiple methods to zoom and move images

    Attributes
    -----
    self.master : Application
        master object

    self._image_photoimage : PhotoImage
        Attribute to store PhotoImage so it is efectively shown

    self.wdir : str
        Working directory

    self.zoom_level: float
        Zoom level, relative to original image

    self.zoom_delta_x : int
        Left intercept for self.shown_image

    self.zoom_delta_y : int
        Top intercept for self.shown_image

    self.mouse_x : int
        x position of mouse

    self.mouse_y : int
        y position of mouse

    self.image_name : str
        Name of the current image

    self.image : numpy array
        Image matrix

    Methods
    -----
    self._on_mousewheel
        Zoom image

    self.move_image
        Move image

    self.move_image_activate
        Get initial variables considering mouse position

    self.reset_zoom_level
        Calculate default zoom level: factor with which the image has to be
        rescaled to show it as large as possible in self.window

    self.update_image
        Dummy method which is overwritten by the children classes of
        GeneralImageCanvas
    """
    def __init__(self, master, **kwargs):
        #initiate parent class with **kwargs
        super().__init__(**kwargs)

        #assign master
        self.master = master
        
        #get size of grey border
        if 'bd' in kwargs:            
            self.bd = kwargs['bd']
        else:
            self.bd = 0

        #initiate image
        self.image_photoimage = self.create_image(self.bd, self.bd, anchor='nw')
        self._image_photoimage = None #variable to store PhotoImage

        #working directory
        self.wdir = None

        #declare attributes containing window variables
        self.zoom_level = 1.0 #zoom level, relative to original image
        self.zoom_delta_x = 0 #left intercept for self.shown_image
        self.zoom_delta_y = 0 #top intercept for self.shown_image
        self.mouse_x = 0 #x position of mouse
        self.mouse_y = 0 #y position of mouse
        self.image_name = None #name of the current image
        self.image = None #image matrix

        #bind events
        self.bind("<MouseWheel>",
                  self._on_mousewheel)
        self.bind("<B2-Motion>",
                  self.move_image)
        self.bind("<Button-2>",
                  self.move_image_activate)

    def _on_mousewheel(self, event):
        """
        Zoom image

        Parameters
        ----------
        event : tkinter.Event
            MouseWheel event
        """

        if self.image is not None:
            #get current scale
            s = self.zoom_level

            #determine zooming center on original image
            x_zoom_center_image = (event.x + self.zoom_delta_x) / s
            y_zoom_center_image = (event.y + self.zoom_delta_y) / s

            #increase self.zoom_level with 5%
            self.zoom_level *= (1.05)**(event.delta/120)
            #event.delta is always a multiple of 120

            #get current scale
            s = self.zoom_level

            #calculate intercepts

            #at least 0
            self.zoom_delta_x = max(0, x_zoom_center_image * s - event.x)
            self.zoom_delta_y = max(0, y_zoom_center_image * s - event.y)

            #if image fits on self.self, intercepts have to be 0
            self.zoom_delta_x = min(max(0, self.image.shape[1] * self.zoom_level +\
                                        2 * self.bd - self.winfo_width()),
                                    self.zoom_delta_x)
            self.zoom_delta_y = min(max(0, self.image.shape[0] * self.zoom_level +\
                                        2 * self.bd - self.winfo_height()),
                                    self.zoom_delta_y)

            #convert intercepts to integers
            self.zoom_delta_x = int(self.zoom_delta_x)
            self.zoom_delta_y = int(self.zoom_delta_y)

            #update image
            #mode should be 0 because self.zoom_level has changed
            self.update_image(mode=0)

    def move_image(self, event):
        """
        Move image

        Parameters
        ----------
        event : tkinter.Event
            Motion event
        """
        if self.image is not None:
            #adapt intercepts
            self.zoom_delta_x += (self.mouse_x - event.x)
            self.zoom_delta_y += (self.mouse_y - event.y)

            #At least 0
            self.zoom_delta_x = max(0, self.zoom_delta_x)
            self.zoom_delta_y = max(0, self.zoom_delta_y)

            #if image fits on self, intercepts have to be 0
            #important to take the margins of the frame into account
            self.zoom_delta_x = min(max(0, self.image.shape[1] * self.zoom_level +\
                                        2 * self.bd - self.winfo_width()),
                                    self.zoom_delta_x)
            self.zoom_delta_y = min(max(0, self.image.shape[0] * self.zoom_level +\
                                        2 * self.bd - self.winfo_height()),
                                    self.zoom_delta_y)

            #convert intercepts to integers
            self.zoom_delta_x = int(self.zoom_delta_x)
            self.zoom_delta_y = int(self.zoom_delta_y)

            #update mouse position parameters
            self.mouse_x = event.x
            self.mouse_y = event.y

            #update image
            self.update_image(mode=1)

    def move_image_activate(self, event):
        """
        Get initial variables considering mouse position

        Parameters
        ----------
        event : tkinter.Event
            ButtonPress event
        """
        self.mouse_x = event.x
        self.mouse_y = event.y

    def reset_zoom_level(self):
        """
        Calculate default zoom level: factor with which the image has to be
        rescaled to show it as large as possible in self.window
        """
        if self.image is not None:
            image_height, image_width = self.image.shape[:2]
            uw = self.winfo_width() - 2 * self.bd
            uh = self.winfo_height() - 2 * self.bd
            self.zoom_level = min(uw/image_width, uh/image_height)
            
            #when the zoom level is reset, the intercepts should be zero,
            #since the image will fit exactly in the canvas
            self.zoom_delta_x = 0 #left intercept
            self.zoom_delta_y = 0 #top intercept

    def update_image(self, mode=0):
        """
        Dummy method which is overwritten by the children classes of
        GeneralImageCanvas
        """
        #dummy method
        pass
    