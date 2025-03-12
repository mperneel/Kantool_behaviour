# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 14:59:15 2022

@author: Maarten

Defenition of the settings class, which contains all modifiable setting values
"""
#%%

class Settings():
    
    def __init__(self):
        
        #linewidth
        #unit: px
        self.linewidth = 3
        
        #point size
        #unit: px
        self.point_size = 5
        
        #focus circle diameter
        #unit: px
        self.circle_radius = 20
        
        #sensitivity for re-activation, expressed at the user scale
        #unit: px
        self.reactivation_sensitivity = 10
        
        #magnetic image border for drawing masks
        #unit: px
        self.magnetic_border = 40
        
        #highlight active keypoint on skeleton
        #bool
        self.highlight_skeleton_keypoint = False
        
        #ask for applying a mask template when importing an image
        #bool
        self.ask_for_mask_template = True
        
        #default mask template
        #dict
        self.default_mask_template = None


    @property
    def point_size_skeleton(self):
        """
        Point size of the keypoints on the skeleton canvas
        """
        #keypoints on the skeleton canvas are drawn larger in comparison with
        #those on the annotation canvas
        return int(self.point_size  * 1.5)