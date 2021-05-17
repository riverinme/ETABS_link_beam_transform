# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 11:18:38 2021

To transfer frame link beams to shell link beams

@author: HH
"""

import comtypes.client
import numpy as np

SapModel = comtypes.client.CreateObject('ETABSv1.Helper').GetObject("CSI.ETABS.API.ETABSObject") .SapModel

#to obtain all frame lbs
print("读取所有需要转换的连梁")
core_group = "core"
SapModel.SelectObj.ClearSelection()
SapModel.SelectObj.Group(core_group)
ret = SapModel.SelectObj.GetSelected()
lbs = [j for i, j in zip(ret[1], ret[2]) if i == 2]
SapModel.SelectObj.ClearSelection()

#to obtain LBs end points and sections
print("读取连梁端点")
points = []
prpt = []
for i in lbs:
    prpt.append(SapModel.FrameObj.GetSection(i)[0])
    points.append(SapModel.FrameObj.GetPoints(i)[:-1])

# to botain LBs h, b, and concretes
print("读取连梁截面尺寸和混凝土")
beam_heights = []
beam_concs = []
beam_widths = []
for i in prpt:
    ret = SapModel.PropFrame.GetRectangle(i)
    beam_heights.append(ret[2])
    beam_widths.append(ret[3])
    beam_concs.append(ret[1])

# to create new wall properties for LBs
print("定义新的墙截面")
new_wall_prpts = []
for i, j, k in zip(beam_concs, beam_widths, lbs):
    new_name = k+"_"+i+"_"+str(j)
    SapModel.PropArea.SetWall(new_name, 1, 1, i, j)
    new_wall_prpts.append(new_name)

# to draw new wall like lbs
print("绘制shell连梁")
for i, j, k in zip(points, beam_heights, new_wall_prpts):
    x1, y1, z1 = SapModel.PointObj.GetCoordCartesian(i[0])[:-1]
    x2, y2, z2 = SapModel.PointObj.GetCoordCartesian(i[1])[:-1]
    X = [x1, x2, x2, x1]
    Y = [y1, y2, y2, y1]
    Z = [z1, z2, z2-j, z1-j]
    SapModel.AreaObj.AddByCoord(4, X, Y, Z, k, k, k)

# to delete original lbs
print("删除原连梁")
SapModel.SelectObj.ClearSelection()
SapModel.FrameObj.SetSelected(core_group, True, 1)
SapModel.FrameObj.Delete("all", 2)

SapModel.SelectObj.ClearSelection()
SapModel.View.RefreshView()

