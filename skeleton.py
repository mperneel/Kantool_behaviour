# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 12:29:37 2021

@author: Maarten

In this file, the skeleton class is defined. this class stores all information
with regardto the sckeleton according to which annotations are made
"""

#%% import packages
import numpy as np

#%%
class Skeleton():
    """
    Class to store all information with regard to the skeleton according to which
    annotations are made

    Attributes
    -----
    self.keypoints : list (n)
        Names of the keypoints. The names of the keypoints are given as strings.
        Keypoint names may not contain spaces

    self.coordinates : numpy array (n, 2)
        Coordinates of the keypoints as [x, y]. Images have their origin in the
        right top, the x-axis is horizontal, the y-axis is vertical

    self.parent : numpy array (n)
        Indices of the parent keypoints. The central keypoint has parent -1

    self.color : list (n)
        Colors with which the keypoints should be displayed colors are stored
        in a list with three elements and are specified according to the RGB
        convention (integers between 0 and 255)

    self.annotation_order : list (n)
        Each keypoint is assigned an annotation order (integer) starting
        from zero for the first point which should be annotated, and increasing
        in steps of one.

    self.func_annotation_order : list (n)
        The first element of func_annotation_order contains the index of
        the first keypoint which should be annotated. The second element of
        func_annotation_order contains the index of the second keypoint which
        should be annotated,...


    Methods
    -----
    self.check_hierarchy()
        Check if the skeleton has a valid hierarchy
    """

    def __init__(self):
        #name of the keypoints
        self.keypoints = None
        #list (n), containing the names of the keypoints. The names of the keypoints
        #are given as strings. Keypoint names may not contain spaces

        #coordinates of the keypoints
        self.coordinates = None
        #numpy array with dimensions (n, 2) containing the coordinates of the
        #keypoints as [x, y]. Images have their origin in the right top, the
        #x-axis is horizontal, the y-axis is vertical

        #indices of the parent keypoints
        self.parent = None
        #numpy array with dimensions (n), containing the indices of the parent
        #keypoints. The central keypoint has parent -1

        #color of the keypoints
        self.color = None
        #list (n), containing the colors with which the keypoints should be displayed
        #colors are stored in a list with three elements and are specified
        #according to the RGB convention (integers between 0 and 255)

        #annotation order
        self.annotation_order = None
        #list (n), each keypoint is assigned an annotation order (integer) starting
        #from zero for the first point which should be annotated, and increase
        #in steps of one.

        #functional annotation order
        self.func_annotation_order = None
        #list (n), the first element of func_annotation_order contains the index of
        #the first keypoint which should be annotated. The second element of
        #func_annotation_order contains the index of the second keypoint which
        #should be annotated,...

        #In contrast to the annotation_order, the functional annotation order
        #can be used directly by the software to look up the index of the next
        #keypoint to annotate. This limits the number of comparisons the software
        #has to execute, thereby speeding up the code
        
        self.image = None
        #background image for skeleton

    def check_hierarchy(self):
        """
        Check if the skeleton has a valid hierarchy

        Returns
        -------
        If the skeleton has a valid hierarchy, True is returned. if the
        hierarchy is incorrect, False is returned.
        """

        #list all connections
        connections = np.zeros(shape=(len(self.keypoints) - 1, 2)).astype(int)
        j = 0
        for i, parent in enumerate(self.parent):
            if parent != -1:
                connections[j, :] = [i, parent]
                j += 1

        #construct hierarchy

        #boolean to trace which connections were already used
        used_connections = np.zeros(shape=(len(self.keypoints) - 1)).astype(bool)

        #list to store the hierarchic levels
        hierarchy = []

        #index of central keypoint
        central_keypoint = np.where(self.parent == -1)[0][0]
        #np.where returns a tuple containing a list with the indices of the
        #elements for which the specified condition is true

        #while loop to construct the hierarchy
        next_level = [central_keypoint]
        classified_keypoints = 0

        while len(next_level) > 0:
            #append next_level to the hierarchy
            hierarchy.append(next_level)

            #update counter of classified keypoints
            classified_keypoints += len(next_level)

            #re-initiate next_level
            next_level = []

            #check which keypoints belong to the next hierarchical level
            for i in hierarchy[-1]:
                for j, connection in enumerate(connections):
                    if not used_connections[j]:
                        if connection[0] == i:
                            next_level.append(connection[1])
                            used_connections[j] = True
                        elif connection[1] == i:
                            next_level.append(connection[0])
                            used_connections[j] = True

        return classified_keypoints == len(self.keypoints)
    
    def marginal_keypoint_index(self, i):
        """
        Find marginal keypoint index of keypoint with real keypoint index i

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        pass
    
    def keypoint_index(self, i):
        """
        find real keypoint index of keypoint with marginal keypoint index i

        Parameters
        ----------
        i : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        return self.func_annotation_order[i]
    
    @property
    def n_keypoints(self):
        """
        Get number of keypoints in the skeleton
        """
        if self.keypoints is None:
            return None
        return len(self.keypoints)
