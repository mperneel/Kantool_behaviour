# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:09:09 2021

@author: Maarten

In this script, the ObjectCanvas class is defined. The objectCanvas class
allows the user to consult and modify all object- and mask- related annotations
"""
#%% import packages
import tkinter as tk
from tkinter import ttk

from rename_object import RenameObject
#%%

class ObjectCanvas(ttk.Notebook):
    """
    The objectCanvas class allows the user to consult and modify all object-
    and mask- related annotations
    """

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)

        #assign master
        self.master = master

        #assign annotation object
        self.annotations = master.annotations

        #assign skeleton object
        self.ethogram = master.ethogram

        #assign image object
        self.image = self.master.annotation_canvas.image

        self.master.master.update_idletasks()

        # tab with all objects
        self.objects = tk.Frame(master=self)

        #boolean to indicate if tracing of variables is allowed
        self.bool_var_tracing = True

        #create listbox and scrollbar
        self.list_objects = tk.Listbox(master=self.objects)
        self.scrollbar = tk.Scrollbar(self.objects,
                                      orient="vertical",
                                      width=20)

        #configure scrollbar
        self.scrollbar.config(command=self.list_objects.yview)
        self.list_objects.config(yscrollcommand=self.scrollbar.set)

        #bind events to self.list_objects
        self.list_objects.bind("<<ListboxSelect>>",
                               lambda event: self.activate_object())
        self.list_objects.bind("<Delete>",
                               lambda event: self.delete_object())
        self.list_objects.bind("<Double-1>",
                               lambda event: self.rename_object())
        #<Double-1> = double click of left mouse button

        #create button_frame
        self.object_buttons_frm = tk.Frame(master=self.objects)
        self.btn_draw_new_object = tk.Button(master=self.object_buttons_frm,
                                             text="draw new",
                                             command=self.draw_new_object)
        self.btn_delete_object = tk.Button(master=self.object_buttons_frm,
                                           text='delete',
                                           command=self.delete_button_pressed)

        #tab with all mask objects
        self.mask_objects = tk.Frame(master=self)

        #create listbox and scrollbar
        self.list_masks = tk.Listbox(master=self.mask_objects)
        self.scrollbar_masks = tk.Scrollbar(self.mask_objects,
                                      orient="vertical",
                                      width=20)

        #configure scrollbar
        self.scrollbar_masks.config(command=self.list_masks.yview)
        self.list_masks.config(yscrollcommand=self.scrollbar_masks.set)

        #bind events to self.list_objects

        self.list_masks.bind("<<ListboxSelect>>",
                               lambda event: self.activate_mask())
        self.list_masks.bind("<Delete>",
                               lambda event: self.delete_mask())
        self.list_masks.bind("<Double-1>",
                               lambda event: self.rename_mask())
        #<Double-1> = double click of left mouse button

        #create button_frame
        self.masks_buttons_frm = tk.Frame(master=self.mask_objects)
        self.btn_draw_new_mask = tk.Button(master=self.masks_buttons_frm,
                                             text="draw new",
                                             command=self.draw_new_mask)
        self.btn_hide_show_masks = tk.Button(master=self.masks_buttons_frm,
                                             text="hide all",
                                             command=self.hide_show_masks)
        self.btn_delete_mask = tk.Button(master=self.masks_buttons_frm,
                                           text='delete',
                                           command=self.delete_mask)

        #tab with behaviours
        self.behaviour_data = tk.Frame(master=self)
        self.frm_behaviour_annotations = tk.Frame(master=self.behaviour_data)
        self.frm_behaviour_buttons = tk.Frame(master=self.behaviour_data)

        #create labels and entry fields
        self.var_behavioural_choices = tk.StringVar()
        self.var_behaviour = tk.StringVar()
        self.var_object_id = tk.StringVar()

        self.lab_object_id = tk.Label(master=self.frm_behaviour_annotations,
                                     text="Object")
        self.lab_object_id_value = tk.Label(master=self.frm_behaviour_annotations,
                                            textvariable=self.var_object_id)
        self.lab_behaviour = tk.Label(master=self.frm_behaviour_annotations,
                                      text="Behaviour")
        self.lab_behaviour_choices = tk.Label(master=self.frm_behaviour_annotations,
                                              textvariable=self.var_behavioural_choices,
                                              justify='left')

        self.entry_behaviour = ttk.Entry(master=self.frm_behaviour_annotations,
                                         textvariable=self.var_behaviour)

        #bind tracing methods
        self.var_behaviour.trace('w',
                                 lambda *args: self.store_behaviour())

        #create button frame
        self.btn_next_object = \
            tk.Button(master=self.frm_behaviour_buttons,
                      text="Next (F10)",
                      command=lambda : self.activate_next_object(direction=1))
        self.btn_previous_object =\
            tk.Button(master=self.frm_behaviour_buttons,
                      text="Previous (F9)",
                      command=lambda : self.activate_next_object(direction=-1))

        #bind keys
        self.behaviour_data.bind_all('<F9>',
            lambda event: self.activate_next_object(direction=-1) \
            if self.index("current")==2\
            else None)
        self.behaviour_data.bind_all('<F10>',
            lambda event: self.activate_next_object(direction=1) \
            if self.index("current")==2\
            else None)


        #position all elements

        #add tabs to notebook
        self.add(self.objects, text="Objects")
        self.add(self.mask_objects, text='Masks')
        self.add(self.behaviour_data, text="Behaviour")

        #format self.objects
        self.btn_draw_new_object.grid(row=0,
                                      column=0,
                                      sticky='news')
        self.btn_delete_object.grid(row=0,
                                    column=1,
                                    sticky='news')
        self.object_buttons_frm.columnconfigure(0, weight=1)
        self.object_buttons_frm.columnconfigure(1, weight=1)


        self.object_buttons_frm.pack(side='bottom',
                               fill="x")
        self.list_objects.pack(side="left",
                               fill=tk.BOTH,
                               expand=True)
        self.scrollbar.pack(side="left",
                            fill="y")

        #format self.mask_objects
        self.btn_draw_new_mask.grid(row=0,
                                    column=0,
                                    sticky='news')
        self.btn_hide_show_masks.grid(row=0,
                                      column=1,
                                      sticky='news')
        self.btn_delete_mask.grid(row=0,
                                  column=2,
                                  sticky='news')
        self.masks_buttons_frm.columnconfigure(0, weight=1)
        self.masks_buttons_frm.columnconfigure(1, weight=1)
        self.masks_buttons_frm.columnconfigure(2, weight=1)

        self.masks_buttons_frm.pack(side='bottom',
                               fill="x")
        self.list_masks.pack(side="left",
                               fill=tk.BOTH,
                               expand=True)
        self.scrollbar_masks.pack(side="left",
                            fill="y")

        #format self.behaviour_data
        self.lab_object_id.grid(row=0,
                                column=0,
                                sticky="w")
        self.lab_object_id_value.grid(row=0,
                                      column=1,
                                      sticky="w")
        self.lab_behaviour.grid(row=1,
                                column=0,
                                sticky="w")
        self.entry_behaviour.grid(row=1,
                                  column=1,
                                  sticky='we')
        self.lab_behaviour_choices.grid(row=2,
                                        column=1,
                                        columnspan=2,
                                        sticky='nw')

        self.btn_previous_object.grid(row=0,
                                      column=0,
                                      sticky='news')
        self.btn_next_object.grid(row=0,
                                  column=1,
                                  sticky='news')


        self.frm_behaviour_annotations.columnconfigure(1, weight=1)

        self.frm_behaviour_buttons.columnconfigure(0, weight=1)
        self.frm_behaviour_buttons.columnconfigure(1, weight=1)

        self.frm_behaviour_annotations.pack(side="top",
                                            fill="x")
        self.frm_behaviour_buttons.pack(side="bottom",
                                        fill="x")


        #bind method to tab change
        self.bind('<<NotebookTabChanged>>',
                  lambda event: self.check_mode())

        #set attributes containing information about the application state
        self.active_object_index = None
        #index (within listbox) of currently active object
        self.active_mask_index = None
        #index (within listbox) of currently active mask
        self.mode = 0 #0 = object mode; 1 = mask mode
        self.masks_visible = True

        self.frm_behaviour_active = True

    def reset(self):
        """
        Reset self.list_objects
        """
        #delete all current objects
        self.list_objects.delete(0, tk.END)
        self.list_masks.delete(0, tk.END)

        self.bool_var_tracing = False
        self.var_behavioural_choices.set("")
        self.var_behaviour.set("")
        self.var_object_id.set("")
        self.bool_var_tracing = True

    def load_data(self):
        """
        (Re)load data of current image
        """

        #reset all panes
        self.reset()

        #(re)load all objects of an instance

        names = self.annotations.names

        #check if there are names defined at all
        if len(names) == 0:
            return

        #if last object is a preallocated object, its name shouldn't be shown (yet)
        if self.annotations.last_object_empty:
            names = names.iloc[:-1,:]

        for i in names.index:
            self.list_objects.insert(tk.END, names.loc[i,"name"])

        #load masks
        names = self.annotations.names_masks
        for i in names.index:
            self.list_masks.insert(tk.END, names.loc[i,"name"])

        #load behaviours
        self.update_frm_behaviour()

    def add_object(self, obj_name):
        """
        Add a new object
        """
        self.list_objects.insert(tk.END, obj_name)

    def delete_object(self):
        """
        delete an object
        """
        #this method may only be invoked if object_canvas is active from the
        #perspective of the annotation_canvas
        if not self.master.annotation_canvas.object_canvas_active:
            return

        if len(self.list_objects.curselection()) == 0:
            #if no objects are selected (or declared), no object may be deleted
            return

        obj_name = self.list_objects.get(self.active_object_index)
        self.list_objects.delete(self.list_objects.curselection()[0])
        self.master.annotation_canvas.delete_object(obj_name=obj_name)

        #activate the next object
        if self.active_object_index  < len(self.list_objects.get(0, tk.END)) :
            list_index = self.active_object_index
        else:
            list_index = 0

        self.list_objects.activate(list_index)
        self.list_objects.select_set(list_index)
        self.activate_object(list_index=list_index)

    def delete_button_pressed(self):
        """
        decisive method for delete button
        """
        #activate object_canvas is active from the perspective of annotation_canvas
        self.master.annotation_canvas.object_canvas_active = True

        #if the button was invoked after an object was activated by selction of
        #some keypoint in the annotation canvas, firstly the method activate_object
        #should be executed.
        #if this is not the case, no changes will happen as a result of invoking
        #activate_object()
        self.activate_object()

        #delete object
        self.delete_object()

        #de-activate object_canvas is active from the perspective of annotation_canvas
        self.master.annotation_canvas.object_canvas_active = False

    def activate_object(self, list_index=None):
        """
        Activate an object
        """
        #change active object
        if self.mode == 1:
            #this method should do nothing when in mask mode
            return

        #set attribute, so annotation_canvas knows the object_canvas is currently
        #used
        self.master.annotation_canvas.object_canvas_active = True

        if list_index is None:
            current_selection = self.list_objects.curselection()
            if len(current_selection) > 0:
                self.active_object_index = current_selection[0]
        else:
            self.active_object_index = list_index

        if self.active_object_index is not None:
            obj_name = self.list_objects.get(self.active_object_index)
            if (obj_name is not None) and\
                (obj_name != ""):
                self.annotations.update_active_object(obj_name=obj_name)
            else: #obj_name not None:
                #last (non confirmed) object should be activated
                self.annotations.update_active_object(obj_id="last")

        self.master.annotation_canvas.update_image(mode=3)

    def rename_object(self):
        """
        Rename an object
        """
        #this method is integrated in the software architecture, but disabled,
        #since the data-formats doesn't allow to store names for objects
        pass

    def draw_new_object(self):
        """
        Draw a new object
        """
        self.active_object_index = None
        self.list_objects.select_clear(0, tk.END)
        self.master.annotation_canvas.new_object()

    def activate_mask(self, list_index=None):
        """
        Activate a mask
        """
        if self.mode == 0:
            #this method should do nothing when in object mode
            return

        if not self.masks_visible:
            #if the masks are not visible, no mask may be activated
            return

        #assign to annotation_canvas no point is active any more
        self.master.annotation_canvas.point_mask_active = False

        #assign to annotation_canvas the object_canvas is active
        self.master.annotation_canvas.object_canvas_active = True

        #change active mask
        if list_index is None:
            current_selection = self.list_masks.curselection()
            if len(current_selection) > 0:
                self.active_mask_index = current_selection[0]
        else:
            self.active_mask_index = list_index

        if self.active_mask_index is not None:
            mask_name = self.list_masks.get(self.active_mask_index)

            if isinstance(mask_name, tuple):
                mask_name = mask_name[0]

            self.update_active_mask(mask_name=mask_name)

    def update_active_mask(self, mask_id=None, mask_name=None):
        """
        Change the active mask

        Only one of the inputs mask_id and mask_name should be defined

        Parameters
        ----------
        mask_id : int, optional
            Identification index of the mask. The default is None.
        mask_name : str, optional
            Name of the maks. The default is None.
        """

        if not self.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #process arguments
        if mask_id is None and mask_name is None:
            raise ValueError("mask_id and mask_name may not be both None")
        if mask_id is not None and mask_name is not None:
            raise ValueError("mask_id and mask_name may not be given both")
        if mask_name is not None:
            #only mask_name is given
            #get mask_id
            mask_id = self.annotations.get_mask_id(mask_name)

        #first store all adaptations to the current mask (if necessary)
        #to the general dataframes
        if self.annotations.current_mask_confirmed is False:
            #confirm current mask
            self.annotations.new_mask()

        self.annotations.update_active_mask(mask_id)

        self.master.annotation_canvas.update_image(mode=0)

    def delete_mask(self):
        """
        Delete a mask
        """
        #this method may only be invoked if object_canvas is active from the
        #perspective of the annotation_canvas
        if not self.master.annotation_canvas.object_canvas_active:
            return

        if not self.masks_visible:
            #if the masks are not visible, no mask may be deleted
            return

        if len(self.list_masks.curselection()) == 0:
            #if no masks are selected (or declared), no mask can be deleted
            return

        mask_index = self.list_masks.curselection()[0]
        mask_name=self.list_masks.get(mask_index)

        if isinstance(mask_name, int):
            #mask name is a list
            mask_name = mask_name[0]

        self.list_masks.delete(mask_index)
        self.master.annotation_canvas.delete_mask(mask_name=mask_name)

    def rename_mask(self):
        """
        Rename mask
        """

        if not self.masks_visible:
            #if the masks are not visible, no mask may be renamed
            return

        #get current name of mask
        self.active_mask_index = self.list_masks.curselection()[0]
        mask_current_name=self.list_masks.get(self.active_mask_index)

        if isinstance(mask_current_name, tuple):
            mask_current_name = mask_current_name[0]

        #get new name of mask
        RenameObject(self, mask_current_name)

        #activate renamed mask
        self.activate_mask(list_index=self.active_mask_index)

    def draw_new_mask(self):
        """
        Draw new mask
        """

        if not self.masks_visible:
            #if the masks are not visible, no new mask may be drawn
            return

        self.active_mask_index = None
        self.master.annotation_canvas.mask_mode = True
        self.master.annotation_canvas.new_object()

    def hide_show_masks(self):
        """
        Change visibility of masks
        """
        self.master.annotation_canvas.show_mask =\
            not self.master.annotation_canvas.show_mask

        if self.master.annotation_canvas.show_mask:
            self.masks_visible = True
            self.btn_hide_show_masks.configure(text="hide all")
            #re-activate buttons and listboxes
            self.list_masks.configure(state = tk.NORMAL)
            self.btn_draw_new_mask.configure(state = tk.ACTIVE)
            self.btn_delete_mask.configure(state = tk.ACTIVE)
        else:
            self.masks_visible = False
            self.btn_hide_show_masks.configure(text="show all")
            #disable buttons and listboxes so no wrong things can happen
            self.list_masks.configure(state = tk.DISABLED)
            self.btn_draw_new_mask.configure(state = tk.DISABLED)
            self.btn_delete_mask.configure(state = tk.DISABLED)

        self.master.annotation_canvas.update_image()

    def add_mask(self, obj_name):
        """
        Add mask
        """
        self.list_masks.insert(tk.END, obj_name)

    def check_mode(self):
        """
        check_mode object_canvas
        """
        self.mode = self.index("current")
        self.master.annotation_canvas.mode = self.mode

        if self.mode == 0 :
            #mode: making annotations

            if self.annotations.image is not None:
                self.master.annotation_canvas.new_object(remove_uncomplete=True)

        elif self.mode == 1:
            #mode: creating masks
            pass
        else: #self.mode == 2:
            #mode: making behaviour annotations

            #activate curent object
            self.activate_next_object(direction=0)

            #update image
            self.master.annotation_canvas.update_image(mode=3)

    def activate_default_object(self):
        """
        activate default object
        """

        self.check_mode()

        if self.mode == 0:
            #objects tab
            self.annotations.update_active_object(
                obj_id=len(self.annotations.annotations) - 1)
        elif self.mode == 1:
            #masks tab
            self.annotations.update_active_mask(
                mask_id=len(self.annotations.masks) - 1)
        elif self.mode == 2:
            #Behaviour tab
            self.annotations.update_active_object(obj_id=0)
            self.update_frm_behaviour()

    def store_behaviour(self):
        """
        store behaviour
        """

        #check if tracing of variables is allowed
        if not self.bool_var_tracing:
            return

        #check if behavioural code is valid
        valid = self.ethogram.isvalid(self.var_behaviour.get())

        if valid:
            #write behavioural code to annotations
            behaviour_old = self.annotations.behaviours.loc[self.annotations.object, "behaviour"]
            behaviour_new = self.var_behaviour.get()

            if behaviour_new == behaviour_old:
                #behavioural code was not changed
                return

            #behavioural code was changed
            self.annotations.behaviours.loc[self.annotations.object, "behaviour"] =\
                self.var_behaviour.get()

            self.annotations.currently_saved = False

        #update behavioural choices
        #if unvalid behavioural code, this will revert the modifications
        self.update_frm_behaviour()

    def activate_next_object(self, direction):
        """
        Activate the next object

        Parameters
        ----------
        direction : TYPE
            1 for increasing
            -1 for decreasing
            0 for activating current object
        """

        if self.annotations.image is None:
            return

        if self.annotations.object is None:
            self.activate_object(list_index=0)
        else:
            if len(self.annotations.annotations) == 1:
                list_index = 0
            elif self.annotations.last_object_empty:
                list_index = (self.annotations.object + direction) %\
                    (len(self.annotations.names) - 1)
            else:
                list_index = (self.annotations.object + direction) %\
                    len(self.annotations.names)
            self.activate_object(list_index=list_index)

        self.update_frm_behaviour()

        #select current behaviour entry to facilitate modifications
        self.entry_behaviour.focus()
        self.entry_behaviour.select_range(0, tk.END)

    def update_frm_behaviour(self):
        """
        Update all displayed annotation data with regard to behaviour
        """

        #check if frm_behaviour should be (de)activated
        if (self.annotations.valid_objects > 0) and\
            (not self.frm_behaviour_active):
            self.activate_frm_behaviour()
        elif (self.annotations.valid_objects == 0) and\
            (self.frm_behaviour_active):
            self.deactivate_frm_behaviour()

        #object id
        self.var_object_id.set(str(self.annotations.object))

        #object_behaviour
        object_behaviour = self.annotations.behaviours.loc[self.annotations.object, "behaviour"]

        self.bool_var_tracing = False
        if object_behaviour is not None:
            self.var_behaviour.set(str(object_behaviour))
        else:
            self.var_behaviour.set("")
        self.bool_var_tracing = True

        #behavioural_choices
        behavioural_choices_string = ""

        hierarchic_description = self.ethogram.hierarchic_description(object_behaviour)

        for key, item in hierarchic_description.items():
            behavioural_choices_string += key + " - " + item + "\n"

        subclasses = self.ethogram.subcategories(object_behaviour, return_dict=True)

        for key, item in subclasses.items():
            behavioural_choices_string += "    " + key + " - " + item + "\n"

        self.var_behavioural_choices.set(behavioural_choices_string)

    def deactivate_frm_behaviour(self):
        """
        Deactivate frm_behaviour
        """
        self.frm_behaviour_active = False
        self.lab_object_id.config(state="disabled")
        self.lab_object_id_value.config(state="disabled")
        self.lab_behaviour.config(state="disabled")
        self.entry_behaviour.config(state="disabled")
        self.lab_behaviour_choices.config(state="disabled")
        self.btn_previous_object.config(state="disabled")
        self.btn_next_object.config(state="disabled")


    def activate_frm_behaviour(self):
        """
        Activate frm_behaviour
        """
        self.frm_behaviour_active = True
        self.lab_object_id.config(state="normal")
        self.lab_object_id_value.config(state="normal")
        self.lab_behaviour.config(state="normal")
        self.entry_behaviour.config(state="normal")
        self.lab_behaviour_choices.config(state="normal")
        self.btn_previous_object.config(state="normal")
        self.btn_next_object.config(state="normal")


