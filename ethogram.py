# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 14:12:58 2023

@author: Maarten

Definition of the Ethogram class
"""
#%% packages
import json
import os


#%%

def ethogram_as_list(ethogram, masterkey=None):
    """
    generate a printeable list, giving an overview of an ethogram

    Parameters
    ----------
    ethogram : dict
        ethogram
    """
    #be aware this is a recursive function

    if masterkey is None:
        masterkey = ""

    ethogram_list = []
    for key, item in ethogram.items():
        ethogram_list.append(masterkey + key + " - " + item["description"])
        if "subclasses" in item:
            ethogram_list += ethogram_as_list(item["subclasses"],
                                              masterkey= masterkey + key)

    return ethogram_list

#%%
class Ethogram():
    """
    Class to store all data with regard to the skeleton to which annotations
    are made
    """

    def __init__(self, master):
        self.ethogram = None #dict to store ethogram
        self.master = master

    def load(self, fp):
        """
        Load ethogram data

        Parameters
        ----------
        fp : string
            Filepath to .json file containing ethogram data
        """

        #check if f is a .json file
        if len(fp.split(".")) != 2 or\
            fp.split(".")[-1] not in ["json"]:
            #invalid file (or folder)
            raise ValueError("fp should be a .json file")
        #fp is a valid json file

        #read json file
        with open(fp, "r") as f:
            self.ethogram = json.load(f)

    def subcategories(self,code, return_dict=False):
        """
        Get subcategories in ethogram of the given behaviour category

        Parameters
        ----------
        code : int or string
            behaviour class
        return_dict = Bool
            if True, a dictionary will returned which contains an item for each
            subclass. For each item, the key is given by the subclass code,
            while the description is given by the content of the item. If False
            a list with the subclass codes will be returned

        Returns
        -------
        subclasses
        """

        if isinstance(code, int):
            code = str(code)

        if self.ethogram is None:
            raise ValueError("No ethogram loaded")

        subethogram = self.ethogram.copy()
        if code is not None:
            for levelcode in code:
                try:
                    subethogram = subethogram[levelcode]
                except:
                    raise ValueError("code is an unvalid behavioural code")

                if "subclasses" in subethogram:
                    subethogram = subethogram["subclasses"]
                else:
                    #lowest level of the ethogram is reached
                    subethogram = {}
        else:
            #subethogram is the whole ethogram
            pass

        subcodes_singular = list(subethogram.keys())

        if code is not None:
            subcodes = [code + i for i in subcodes_singular]
        else:
            subcodes = subcodes_singular

        if return_dict:
            subclasses = {}
            for i, levelcode in enumerate(subcodes_singular):
                subclasses[subcodes[i]] = subethogram[levelcode]["description"]
        else: #return_dict is False
            subclasses = subcodes

        return subclasses

    def hierarchic_description(self, code):
        """
        Get a hierarchic description of a behaviour

        Parameters
        ----------
        code : str
            Behavioural code

        Returns
        -------
        descriptions_dict : dict
            Dictionary with a hierarchic description of the behaviour
        """

        if code is None:
            #if bclass is None, return an emtpy dict
            return {}

        descriptions_dict = {}

        subethogram = self.ethogram.copy()
        levelcode_full = ""

        for levelcode in code:
            levelcode_full += levelcode
            descriptions_dict[levelcode_full] = subethogram[levelcode]["description"]

            subethogram = subethogram[levelcode]
            if "subclasses" in subethogram:
                subethogram = subethogram["subclasses"]
            else:
                subethogram = {}

        return descriptions_dict

    def isvalid(self, code):
        """
        Check if a behavioural code is valid

        Parameters
        ----------
        code : str
            behavioural code

        Returns
        -------
        valid : bool
        """

        if self.ethogram is None:
            return False

        valid = True
        i = 0

        subethogram = self.ethogram.copy()
        while valid and (i < len(code)):
            if code[i] in subethogram:
                subethogram = subethogram[code[i]]
            else:
                valid = False

            if "subclasses" in subethogram:
                subethogram = subethogram["subclasses"]
            i += 1

        return valid

    def as_list(self):
        """
        return ethogram as printable list
        """

        return ethogram_as_list(self.ethogram)

    def save(self):
        """
        Save ethogram to json file
        """

        with open(os.path.join(self.master.wdir, "project\ethogram.json"), "w") as f:
            json.dump(self.ethogram, f, indent=3)

