# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 11:18:38 2021

To transfer frame link beams to shell link beams

@author: HH
"""

import comtypes.client
import numpy as np

SapModel = comtypes.client.GetActiveObject(
    "CSI.ETABS.API.ETABSObject").SapModel


transfer_all = True  # I mean it
ratio_limit = 4  # Shell beams w l/h ratio smaller than this won't be changed


def euclidean(x, y):
    return np.sqrt(np.sum((x - y)**2))


story_levels = SapModel.Story.GetStories_2()[3]
stories = SapModel.Story.GetStories_2()[2]
count = SapModel.PropArea.Count()


for i, j in zip(stories, story_levels):
    areas_on_story = SapModel.AreaObj.GetNameListOnStory(i)[1]
    points_on_story = set(SapModel.PointObj.GetNameListOnStory(i)[1])
    lbs = []
    count = []
    for area in areas_on_story[:]:
        if SapModel.AreaObj.GetDesignOrientation(area)[0] == 1:
           # area_prpt =
            area_points = list(SapModel.AreaObj.GetPoints(area)[1])

            if all([i in points_on_story for i in area_points]):
                coords = sorted([np.array(SapModel.PointObj.GetCoordCartesian(
                                k)[:-1]) for k in area_points], key=lambda x: x[-1], reverse=True)[:-1]
                lb_length = euclidean(coords[0][:-1], coords[1][:-1])
                lb_height = abs(coords[0][-1]-coords[2][-1])
                lbs.append(area)

                lb_prpt = SapModel.PropArea.GetWall(
                    SapModel.AreaObj.GetProperty(area)[0])
                lb_conc = lb_prpt[2]
                lb_thickness = lb_prpt[3]

                new_name = "LB"+str(int(lb_thickness))+"x" + \
                    str(int(lb_height))+"x"+lb_conc
                SapModel.PropFrame.SetRectangle(
                    new_name, lb_conc, lb_height, lb_thickness)

                if transfer_all:
                    print("All link beams are been transfered, don't regret")
                    count.append(area)
                    SapModel.AreaObj.Delete(area)
                    SapModel.FrameObj.AddByCoord(
                        *coords[0], *coords[1], new_name, new_name)

                elif lb_length/lb_height >= ratio_limit:
                    count.append(area)
                    SapModel.AreaObj.Delete(area)
                    SapModel.FrameObj.AddByCoord(
                        *coords[0], *coords[1], new_name, new_name)

    print("{} of {} shell LBs have been transfered on {}.".format(
        len(count), len(lbs), i))


SapModel.View.RefreshView()
