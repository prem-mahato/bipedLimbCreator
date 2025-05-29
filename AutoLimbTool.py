"""
Auto Limb Tool (Create Biped Limb With IK/FK, Stretch and Twist Functionality)

Author: Prem Kumar Mahato
Version: 1.0
Last Update: 25/01/2025



"""
import maya.cmds as cmds
import maya.mel as mel

class autoLimbUi():
    
    def __init__(self):
        self.window = "AutoLimb"
        self.title = "Biped Limb Tool"
        self.size = (400, 150)
        
        if cmds.window(self.window, exists = True):
            cmds.deleteUI(self.window)
        
        self.wind = cmds.window(self.window, title = self.title, wh = self.size)
        self.column = cmds.columnLayout(adjustableColumn = True)
        
        self.formLay = cmds.formLayout()
        
        self.prefix = cmds.textField("prefix_name", pht="Ex: Character Name or Prefix!!!")
        self.limbSelection = cmds.radioButtonGrp( label='Limb : ', labelArray2=['Arm', 'Leg'], numberOfRadioButtons=2, select=1)
        
        self.ctrlSize = cmds.floatSliderGrp( label='Control Size : ', field=True, minValue=0.1, maxValue=100, fieldMinValue=0.1, fieldMaxValue=100.0, value=1 )
        
        self.createButton = cmds.button(l="Create Limb", c=self.runFunction)
        
        cmds.formLayout(self.formLay, e=1, attachForm=[(self.prefix, "top", 10), (self.prefix, "left", 5), (self.prefix, "right", 5),
                        (self.limbSelection, "top", 35), (self.limbSelection, "left", 0), (self.limbSelection, "right", 5),
                        (self.ctrlSize, "top", 65), (self.ctrlSize, "left", 0), (self.ctrlSize, "right", 5),
                        (self.createButton, "top", 100), (self.createButton, "left", 5), (self.createButton, "right", 5), (self.createButton, "bottom", 5)])
        


        cmds.showWindow(self.wind)

    def runFunction(self, *args):
        prefix = cmds.textField(self.prefix, q=1, tx=1)
        limbValue = cmds.radioButtonGrp(self.limbSelection, q=1, select=1)
        
        if limbValue == 1:
            nameLimb = "Arm"
        if limbValue == 2:
            nameLimb = "Leg"
            
        controlSize = cmds.floatSliderGrp(self.ctrlSize, q=1, value=1)
        
        autoLimbTest(characterName=prefix, ctrlSize=controlSize, whichLimb = nameLimb)
        createTwist(ctrlSize = controlSize)
        
        

def autoLimbTest(characterName, ctrlSize, whichLimb):
    
    global switch_pos, ctrlRotateY
    jointSelection = cmds.ls(sl=1, type = "joint")
    
    ##--------------------- Selection Check ---------------------##
    if not jointSelection:
        cmds.error("Please Select Root Joint Shoulder or Thigh!!")
        
    root_chain = cmds.ls(jointSelection[0])
    
    ## Controlloer Size ##
    pvSize = (ctrlSize / 1.5)
    ikHand_ctrlSize = (ctrlSize * 1.5)
    ikfk_switchSize = (ctrlSize / 4)
    
    ## Checking joint Side ##
    for jnt in root_chain:
        if not "L_" in jnt:
            if not "R_" in jnt:
                cmds.error("Please Use Left or Right in Joint Naming. !! Example: character_LeftArm  ")
    
    ## renaming ik fk and Stretch joint to use on duplication ##
    for name in root_chain:
        if "L_" in name:
            sideName = ("L_")
            side = 1
        if "R_" in name:
            side = 0
            sideName = ("R_")
            
            
        IK = ("_IK")
        ikName = name.replace("_Jnt", "_ik_Jnt")
        fkName = name.replace("_Jnt", "_fk_Jnt")
        stretchName = name.replace("_Jnt", "_stretch_Jnt")
    ## Duplicating main Joint Chain and Renaming suffix to ik ## NOTE: this will help to duplicate and replcae name ik
    if side ==1: ## for Left side
        ikRoot = cmds.duplicate(rr=1, st=1, name = ikName)
        mel.eval('searchReplaceNames "L_" "left_" "hierarchy";') ## replacing hierarchy side name to "_L_"
        mel.eval('searchReplaceNames "left_" "L_" "selected";') ## returning root ik joint to original side name
        ik_list = cmds.listRelatives(ikRoot, ad = 1)
        
    elif side ==0:## for Right side
        ikRoot = cmds.duplicate(rr=1, st=1, name = ikName)
        mel.eval('searchReplaceNames "R_" "right_" "hierarchy";') ## replacing hierarchy side name to "_R_"
        mel.eval('searchReplaceNames "right_" "R_" "selected";') ## returning root ik joint to original side name
        ik_list = cmds.listRelatives(ikRoot, ad = 1)
    ## returning _side_ to original naming ##
    for name in ik_list:
        cmds.rename(name, name + "_ik")
    if side ==1:
        mel.eval('searchReplaceNames "left_" "L_" "hierarchy";')
    if side ==0:
        mel.eval('searchReplaceNames "right_" "R_" "hierarchy";')
        
    ## Duplicating fk and Stretch joint ##
    for i in range(0,2):
        if i == 0:
            fkRoot = cmds.duplicate(rr=1, st=1, name = fkName)
            mel.eval('searchReplaceNames "_ik" "_fk" "hierarchy";')
        if i > 0:
            StretchRoot = cmds.duplicate(rr=1, st=1, name = stretchName)
            mel.eval('searchReplaceNames "_fk" "_stretch" "hierarchy";')       
    
    ##  listing ik, fk and Stretch Chain ##
    ## ik List ##
    ikChain = cmds.listRelatives(ikRoot, allDescendents = 1, type = "joint") ##ik_List
    ikChain.append(ikRoot)
    ikChain.reverse()
    
    ik_joint = ikChain[0:3]
    cmds.delete(ikChain[3:])

    ## fk List ##
    fkChain = cmds.listRelatives(fkRoot, allDescendents = 1, type = "joint") ##fk_List
    fkChain.append(fkRoot)
    fkChain.reverse()
    
    fk_joint = fkChain[0:3]
    cmds.delete(fkChain[3:])

    ## stretch List ##
    stretchChain = cmds.listRelatives(StretchRoot, allDescendents = 1, type = "joint") ##stretch_List
    stretchChain.append(StretchRoot)
    stretchChain.reverse()
    
    stretch_joint = stretchChain[0:3]
    cmds.delete(stretchChain[3:])
    
    ## bind List ##
    bindChain = cmds.listRelatives(root_chain, allDescendents = 1, type = "joint") ##bind_List
    bindChain.append(root_chain)
    bindChain.reverse()
    
    bind_joint = bindChain[0:3]
    
    ## hiding ik fk stretch joint ##
    chain_visibility = cmds.ls(ik_joint[0], fk_joint[0], stretch_joint[0])
    #print chain_visibility
    for vis in chain_visibility:
        cmds.setAttr(vis + ".visibility", 0)
        
    #------------------------Ctrl------------------------------------#
    ## Adding curve Point for Ctrl
    cube_crvp = [[0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
                [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5],
                [0.5, -0.5, 0.5], [0.5, -0.5, -0.5], [-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5]]

    plus_crvp = [[-0.5, 0.0, -1.5], [0.5, 0.0, -1.5], [0.5, 0.0, -0.5], [1.5, 0.0, -0.5], [1.5, 0.0, 0.5], [0.5, 0.0, 0.5], [0.5, 0.0, 1.5],
                [-0.5, 0.0, 1.5], [-0.5, 0.0, 0.5], [-1.5, 0.0, 0.5], [-1.5, 0.0, -0.5], [-0.5, 0.0, -0.5], [-0.5, 0.0, -1.5]]

    cone_crvp = [[0.0, 1.0, 0.0], [1.0, -1.0, 0.0], [-4.371138828673793e-08, -1.0, 1.0], [0.0, 1.0, 0.0],
                [1.3113415775478643e-07, -1.0, -1.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0], [-1.0, -1.0, -8.742277657347586e-08],
                [1.3113415775478643e-07, -1.0, -1.0], [1.0, -1.0, 0.0],	[-4.371138828673793e-08, -1.0, 1.0], [-1.0, -1.0, -8.742277657347586e-08]]

    diamond_crvp = [[0.0, 1.0, 0.0], [-1.0, 0.00278996, 6.18172e-08], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [1.0, 0.00278996, 0.0],
                    [0.0, 0.0, 1.0], [1.0, 0.00278996, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0], [-1.0, 0.00278996, 6.18172e-08], [0.0, -1.0, 0.0],
                    [0.0, 0.0, -1.0],[1.0, 0.00278996, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]

    ## --------------ctrl Naming & Color Values------------------ ##
    for name in root_chain:
        if "L" in name:
            sideName = ("L")
            ## RGB values ##
            R= 1.0
            G = 0.0
            B = 0.0

        if "R" in name:
            sideName = ("R")
            ## RGB values ##
            R = 0.0
            G = 0.0
            B = 1.0

        if "Arm" in whichLimb:
            if "L_" in name:
                switch_pos = (ctrlSize + ctrlSize)
            if "R_" in name:
                switch_pos = (-(ctrlSize + ctrlSize))
            
            limbName = ("")
            limb = 0

            ## pv Position
            pvMove = (-(ctrlSize*10))
            pvRot = 90

            ##ctrl rotation
            ctrlRotateY = 90

        if "Leg" in whichLimb:
            if "L_" in name:
                limb = 1
                switch_pos = (ctrlSize + ctrlSize)
            if "R_" in name:
                limb = 2
                switch_pos = (-(ctrlSize + ctrlSize))
            limbName = ("")
            ## pv Position
            pvMove = (ctrlSize*10)
            pvRot = -90
            ##ctrl rotation
            ctrlRotateY = 90


    # character name ##
    charName = characterName

    # ik/fk switch Controller
    ikfk_switch = cmds.curve(d = 1, editPoint = plus_crvp, name = charName + sideName +"_"+ whichLimb + "IKFK_switch_Ctrl")
    shape = cmds.listRelatives(ikfk_switch, shapes = 1)[0]
    cmds.rename(shape, ikfk_switch + "shape")
    ikfk_switchOffset = cmds.group(em = 1, n = charName + sideName +"_"+ whichLimb + "IKFK_switch_ctrlOffset")
    cmds.parent(ikfk_switch, ikfk_switchOffset)
    par  = cmds.parentConstraint(bind_joint[2], ikfk_switchOffset, mo=0)
    
    cmds.move(switch_pos, ikfk_switch, x=1, r=1, ws=1)

    cmds.scale(ikfk_switchSize, ikfk_switchSize, ikfk_switchSize, ikfk_switch)
    cmds.makeIdentity(ikfk_switch, apply = 1)
    
    ## Adding Attributes to IFFK_switch ##
    cmds.addAttr(ikfk_switch, longName = "___________", attributeType = "enum", enumName = "IKFK_Switch", keyable = 1)
    cmds.addAttr(ikfk_switch, longName="IKFK", at = "float", k=1, min=0, max=1, defaultValue = 1.0)
    cmds.addAttr(ikfk_switch, longName = "____________", attributeType = "enum", enumName = "Stretch", keyable = 1)
    cmds.addAttr(ikfk_switch, longName="stretch", at = "float", k=1, min=0, max=1, defaultValue = 1.0)
    cmds.addAttr(ikfk_switch, longName="volume", at = "float", k=1, defaultValue = -0.5)
    cmds.addAttr(ikfk_switch, longName="upArmStretch", at = "float", k=1)
    cmds.addAttr(ikfk_switch, longName="lowArmStretch", at = "float", k=1)
    
    ##  unParenting ik,fk & stretch root to IKFK Group ##
    
    clavicle_Joint = cmds.listRelatives(root_chain, parent = 1)
    
    if not clavicle_Joint:
        ikfkGroup = cmds.group(n=charName + sideName+"_"+whichLimb + "IKFK_jnt_Grp", em=1)
        ikfk_ctrlGrp = cmds.group(n=charName + sideName+"_"+whichLimb + "IKFK_Ctrl_icons", em=1)
        fk_ctrlGrp = cmds.group(n=charName + sideName+"_"+whichLimb + "FK_Ctrl_Grp", em=1)
        ik_ctrlGrp = cmds.group(n=charName + sideName+"_"+whichLimb + "IK_Ctrl_Grp", em=1)
        
    else:
        ikfkGroup = cmds.group(n=charName + sideName+"_"+whichLimb + "IKFK_jnt_Grp", em=1)
        ikfk_ctrlGrp = cmds.group(n=charName + sideName+"_"+whichLimb + "IKFK_Ctrl_icons", em=1)
        fk_ctrlGrp = cmds.group(n=charName + sideName+"_"+whichLimb + "FK_ctrl_Grp", em=1)
        ik_ctrlGrp = cmds.group(n=charName + sideName+"_"+whichLimb + "IK_ctrl_Grp", em=1)
        par1 = cmds.parentConstraint(clavicle_Joint, ikfkGroup, mo=0)
        par2 = cmds.parentConstraint(clavicle_Joint, fk_ctrlGrp, mo=0)
        par3 = cmds.parentConstraint(clavicle_Joint, ik_ctrlGrp, mo=0)
        cmds.delete(par1, par2, par3)
    ## parenting joint to group ##
    unparentJoint = cmds.ls(ikRoot, fkRoot, StretchRoot)
    for par in unparentJoint:
        cmds.parent(par, ikfkGroup)
    
    
    ## Connecting ik fk and bind chain ##
    ## listing joints to connect ##
    ik_chain = cmds.ls(ik_joint[0], ik_joint[1], ik_joint[2])
    fk_chain = cmds.ls(fk_joint[0], fk_joint[1], fk_joint[2])
    bind_chain = cmds.ls(bind_joint[0], bind_joint[1], bind_joint[2])

    for ik, fk, bind in zip(ik_chain, fk_chain, bind_chain):
        name = (bind)
        parCons = cmds.parentConstraint(ik, fk, bind, mo=0)[0]
        scaleCons = cmds.scaleConstraint(ik, fk, bind, mo=0)[0]
                
        rev_node = cmds.createNode("reverse", n = name + "_fkSwitch_rev")
        revScale_node = cmds.createNode("reverse", n = name + "_fkScale_rev")
        
        cmds.connectAttr(ikfk_switch + ".IKFK", parCons +"."+ ik + "W0")
        cmds.connectAttr(ikfk_switch + ".IKFK", rev_node + ".inputX")
        cmds.connectAttr(rev_node + ".outputX", parCons +"."+ fk + "W1")
        
        cmds.connectAttr(ikfk_switch + ".IKFK", scaleCons +"."+ ik + "W0")
        cmds.connectAttr(ikfk_switch + ".IKFK", revScale_node + ".inputX")
        cmds.connectAttr(revScale_node + ".outputX", scaleCons +"."+ fk + "W1")

    
    ##-------------Creating controllers---------------##
    ## For FK Control
    fk_upJoint = cmds.ls(fk_chain[0])
    fk_midJoint = cmds.ls(fk_chain[1])
    fk_loJoint = cmds.ls(fk_chain[2])

    for fk in fk_upJoint:
        upFK_Ctrl = cmds.circle(r = 1, n = fk.replace("_Jnt", "")+"_Ctrl")[0]
        cmds.rotate(ctrlRotateY, upFK_Ctrl, y=1)
        cmds.scale(ctrlSize, ctrlSize, ctrlSize, upFK_Ctrl, ws = True)
        cmds.makeIdentity(upFK_Ctrl, apply = True)
        cmds.delete(upFK_Ctrl, constructionHistory = True)
         
        upFK_CtrlOffset = cmds.group(n = fk + "_Ctrl_Offset", em=1, w=1)
        cmds.parent(upFK_Ctrl, upFK_CtrlOffset)
        
        par = cmds.parentConstraint(fk, upFK_CtrlOffset, mo=0)
        cmds.delete(par)
        
    for fk in fk_midJoint:
        midFK_Ctrl = cmds.circle(r = 1, n = fk.replace("_Jnt", "")+"_Ctrl")[0]
        cmds.rotate(ctrlRotateY, midFK_Ctrl, y=1)
        cmds.scale(ctrlSize, ctrlSize, ctrlSize, midFK_Ctrl, ws = True)
        cmds.makeIdentity(midFK_Ctrl, apply = True)
        cmds.delete(midFK_Ctrl, constructionHistory = True)
        
        midFK_CtrlOffset = cmds.group(n = fk + "_Ctrl_Offset", em=1, w=1)
        cmds.parent(midFK_Ctrl, midFK_CtrlOffset)
        
        par = cmds.parentConstraint(fk, midFK_CtrlOffset, mo=0)
        cmds.delete(par)
        
    for fk in fk_loJoint:
        loFK_Ctrl = cmds.circle(r = 1, n = fk.replace("_Jnt", "")+"_Ctrl")[0]
        cmds.rotate(ctrlRotateY, loFK_Ctrl, y=1)
        cmds.scale(ctrlSize, ctrlSize, ctrlSize, loFK_Ctrl, ws = True)
        cmds.makeIdentity(loFK_Ctrl, apply = True)
        cmds.delete(loFK_Ctrl, constructionHistory = True)
        
        loFK_CtrlOffset = cmds.group(n = fk + "_Ctrl_Offset", em=1, w=1)
        cmds.parent(loFK_Ctrl, loFK_CtrlOffset)
        
        par = cmds.parentConstraint(fk, loFK_CtrlOffset, mo=0)
        cmds.delete(par)
        
    ## parenting fk ctrl to hierarchy ##
    cmds.parent(loFK_CtrlOffset, midFK_Ctrl)
    cmds.parent(midFK_CtrlOffset, upFK_Ctrl)
    cmds.parent(upFK_CtrlOffset, fk_ctrlGrp)

    ## constraining fk joint to fk controller ##
    cmds.parentConstraint(upFK_Ctrl, fk_upJoint, mo=1)
    cmds.parentConstraint(midFK_Ctrl, fk_midJoint, mo=1)
    cmds.parentConstraint(loFK_Ctrl, fk_loJoint, mo=1)

    ## For IK Control
    ik_upJoint = cmds.ls(ik_chain[0])
    ik_midJoint = cmds.ls(ik_chain[1])
    ik_loJoint = cmds.ls(ik_chain[2])
    for ik in ik_upJoint:
        upIK_Ctrl = cmds.circle(r = 1, n = ik.replace("_Jnt", "")+"_Ctrl")[0]
        cmds.rotate(ctrlRotateY, upIK_Ctrl, y=1)
        cmds.scale(ctrlSize, ctrlSize, ctrlSize, upIK_Ctrl, ws = True)
        cmds.makeIdentity(upIK_Ctrl, apply = True)
        cmds.delete(upIK_Ctrl, constructionHistory = True)
         
        upIK_CtrlOffset = cmds.group(n = ik + "_Ctrl_Offset", em=1, w=1)
        cmds.parent(upIK_Ctrl, upIK_CtrlOffset)
        
        par = cmds.parentConstraint(ik, upIK_CtrlOffset, mo=0)
        cmds.delete(par)
        
    for ik in ik_midJoint:
        midIK_Ctrl = cmds.curve(d = 1, editPoint = cone_crvp, n=ik.replace("_Jnt", "")+"_Ctrl")
        shapes = cmds.listRelatives(midIK_Ctrl, s=1)
        cmds.rename(shapes, midIK_Ctrl + "shape")
        cmds.rotate(pvRot, midIK_Ctrl, x=1, ws=1)
        cmds.scale(pvSize, pvSize, pvSize, midIK_Ctrl, ws = True)
        cmds.makeIdentity(midIK_Ctrl, apply = True)
        cmds.delete(midIK_Ctrl, constructionHistory = True)
         
        midIK_CtrlOffset = cmds.group(n = ik + "PV_Ctrl_Offset", em=1, w=1)
        cmds.parent(midIK_Ctrl, midIK_CtrlOffset)
        
        par = cmds.pointConstraint(ik, midIK_CtrlOffset, mo=0)
        cmds.delete(par)
        cmds.move(pvMove, midIK_CtrlOffset, z=1, ws=1)
        
    for ik in ik_loJoint:
        loIK_Ctrl = cmds.curve(d = 1, editPoint = cube_crvp, n = ik.replace("_Jnt", "")+"_Ctrl")
        shapes = cmds.listRelatives(loIK_Ctrl, s=1)
        cmds.rename(shapes, loIK_Ctrl + "shape")
        cmds.rotate(pvRot, loIK_Ctrl, x=1, ws=1)
        cmds.scale(ikHand_ctrlSize, ikHand_ctrlSize, ikHand_ctrlSize, loIK_Ctrl, ws = True)
        cmds.makeIdentity(loIK_Ctrl, apply = True)
        cmds.delete(loIK_Ctrl, constructionHistory = True)
         
        loIK_CtrlOffset = cmds.group(n = ik + "_Ctrl_Offset", em=1, w=1)
        cmds.parent(loIK_Ctrl, loIK_CtrlOffset)
        
        par = cmds.pointConstraint(ik, loIK_CtrlOffset, mo=0)
        cmds.delete(par)
    
    ## parenting ik ctrl to hierarchy ##
    cmds.parent(upIK_CtrlOffset, midIK_CtrlOffset, loIK_CtrlOffset, ik_ctrlGrp)
    cmds.parent(ikfk_switchOffset, ik_ctrlGrp, fk_ctrlGrp, ikfk_ctrlGrp)
    
    ## Creating ikHandle and contraining ik controller ##
    cmds.parentConstraint(upIK_Ctrl, ik_upJoint, mo=1)
    cmds.orientConstraint(loIK_Ctrl, ik_loJoint, mo=1)

    ## ikHandle ##
    ik_list = cmds.ls(ik_upJoint, ik_loJoint)
    ikHandle = cmds.ikHandle(name = charName + sideName + whichLimb + "_ikHandle", 
                              startJoint = ik_list[0], endEffector = ik_list[1], sol="ikRPsolver")
    cmds.poleVectorConstraint(midIK_Ctrl, ikHandle[0]) ## poleVector
    cmds.setAttr(ikHandle[0]+".visibility", 0)
    
    cmds.parent(ikHandle[0], loIK_Ctrl)
    
    ## Hiding IKFK Controllers ##
    revNode = cmds.createNode("reverse", n = charName + sideName +"_"+ whichLimb + "_IKFK_rev")
    cmds.connectAttr(ikfk_switch+".IKFK", ik_ctrlGrp+".visibility")
    cmds.connectAttr(ikfk_switch+".IKFK", revNode+".inputX")
    cmds.connectAttr(revNode+".outputX", fk_ctrlGrp+".visibility")
    
    ##---------------------------------------------------------------------------------------##
    ##------------------------------------Stretch & Squash-----------------------------------##
    ##---------------------------------------------------------------------------------------##


    limbName = whichLimb
    stretchJoint = cmds.ls(stretchChain[0], stretchChain[1], stretchChain[2]) ## stretch joint list
    
    ## locator for ctrl distance ##
    DisUpLoc = cmds.spaceLocator(n = charName+sideName+"_"+limbName+"_DistanceUp_loc")[0]
    DisLoLoc = cmds.spaceLocator(n = charName+sideName+"_"+limbName+"_DistanceLo_loc")[0]

    ## set visibility ##
    for loc in (DisUpLoc, DisLoLoc):
        cmds.setAttr(loc+".v", 0)
    
    par1 = cmds.parentConstraint(upIK_Ctrl, DisUpLoc, mo=0) ## moving locator to respected ctrl
    par2 = cmds.parentConstraint(loIK_Ctrl, DisLoLoc, mo=0)
    cmds.delete(par1 + par2)
    
    cmds.parent(DisUpLoc, upIK_Ctrl)
    cmds.parent(DisLoLoc, loIK_Ctrl)
    
    ## creating distance node for stretch joint and ctrl ##
    jointDis1 = cmds.createNode("distanceBetween", n= charName+sideName+"_"+limbName+"Up_dis")
    jointDis2 = cmds.createNode("distanceBetween", n= charName+sideName+"_"+limbName+"Lo_dis")
    ctrlDis = cmds.createNode("distanceBetween", n= charName+sideName+"_"+limbName+"FullCtrl_dis")
    
    adl = cmds.createNode("addDoubleLinear", n= charName+sideName+"_"+limbName+"FullJointDis_adl") ## creating addDoubleLinear node
    
    ## connecting stretch joint and ctrl to distance node ##
    cmds.connectAttr(stretchJoint[0] + ".worldMatrix", jointDis1 + ".inMatrix1")
    cmds.connectAttr(stretchJoint[1] + ".worldMatrix", jointDis1 + ".inMatrix2")
    cmds.connectAttr(stretchJoint[1] + ".worldMatrix", jointDis2 + ".inMatrix1")
    cmds.connectAttr(stretchJoint[2] + ".worldMatrix", jointDis2 + ".inMatrix2")
    
    cmds.connectAttr(jointDis1+".distance", adl+".input1")
    cmds.connectAttr(jointDis2+".distance", adl+".input2")
    #
    cmds.connectAttr(DisUpLoc + ".worldMatrix", ctrlDis + ".inMatrix1")
    cmds.connectAttr(DisLoLoc + ".worldMatrix", ctrlDis + ".inMatrix2")
    
    ## Creating Multiply node and conditon node ##
    cond = cmds.createNode("condition", n= charName+sideName+"_"+limbName+"Stretch_cond")
    multiValue = cmds.createNode("multiplyDivide", n= charName+sideName+"_"+limbName+"scaleValue_multi")
    multiVolume = cmds.createNode("multiplyDivide", n= charName+sideName+"_"+limbName+"stretchVolume_multi")
    
    cmds.setAttr(multiValue + ".operation", 2) ## divide
    cmds.setAttr(cond + ".operation", 2) ## greater than
    cmds.setAttr(multiVolume + ".operation", 3) ## power
    cmds.setAttr(multiVolume + ".input2.input2X", -0.5)

    ## connecting nodes##
    cmds.connectAttr(ctrlDis+".distance", cond+".firstTerm")
    cmds.connectAttr(adl+".output", cond+".secondTerm")
    cmds.connectAttr(ctrlDis+".distance", multiValue+".input1.input1X")
    cmds.connectAttr(adl+".output", multiValue+".input2.input2X")
    cmds.connectAttr(multiValue+".outputX", cond+".colorIfTrue.colorIfTrueR")
    cmds.connectAttr(multiValue+".outputX", multiVolume+".input1.input1X")
    cmds.connectAttr(multiVolume+".outputX", cond+".colorIfTrue.colorIfTrueG")
    
    ## Connecting Stretch Condition to ik Joint chains ##
    ikfkOff = cmds.createNode("blendColors", n= charName+sideName+"_"+limbName+"StretchIKFK_OnOff_blend")
    stretch_OnOff = cmds.createNode("blendColors", n= charName+sideName+"_"+limbName+"StretchOnOff_blend")
    
    armStretchIKFKOnOFF = cmds.createNode("blendColors", n= charName+sideName+"_UpLow"+limbName+"IKFK_OnOff_blend")
    armStretchOnOFF = cmds.createNode("blendColors", n= charName+sideName+"_UpLow"+limbName+"Stretch_OnOff_blend")
    
    upStretch = cmds.createNode("plusMinusAverage", n= charName+sideName+"_"+limbName+"UpArmStretch_pma")
    loStretch = cmds.createNode("plusMinusAverage", n= charName+sideName+"_"+limbName+"LowArmStretch_pma")
    
    cmds.setAttr(ikfkOff + ".color2.color2R", 1) ## setiing attr .color2 to 1
    cmds.setAttr(ikfkOff + ".color2.color2B", 1) ## setiing attr .color2 to 1
    cmds.setAttr(ikfkOff + ".color2.color2G", 1) ## setiing attr .color2 to 1
    
    cmds.setAttr(stretch_OnOff + ".color2.color2R", 1) ## setiing attr .color2 to 1
    cmds.setAttr(stretch_OnOff + ".color2.color2B", 1) ## setiing attr .color2 to 1
    cmds.setAttr(stretch_OnOff + ".color2.color2G", 1) ## setiing attr .color2 to 1
    
    ## Connecting conditon to ikfkf ON OFF blend 
    
    cmds.connectAttr(cond + ".outColor.outColorR", ikfkOff+".color1.color1R")
    cmds.connectAttr(cond + ".outColor.outColorG", ikfkOff+".color1.color1G")
    ## connecting ikfk onOff blend to stretch onOff blend
    cmds.connectAttr(ikfkOff+".output.outputR", stretch_OnOff+".color1.color1R")
    cmds.connectAttr(ikfkOff+".output.outputG", stretch_OnOff+".color1.color1G")
    

    ## connecting ikfk_switch controller to OnOff blend node
    cmds.connectAttr(ikfk_switch+".IKFK", ikfkOff+".blender")
    cmds.connectAttr(ikfk_switch+".stretch", stretch_OnOff+".blender")
    cmds.connectAttr(ikfk_switch+".IKFK", armStretchIKFKOnOFF+".blender")
    cmds.connectAttr(ikfk_switch+".stretch", armStretchOnOFF+".blender")
    cmds.connectAttr(ikfk_switch+".volume", multiVolume+".input2.input2X")
    
    ## Connecting plusNinusAverange ot OnOF Blend node
    cmds.connectAttr(stretch_OnOff+".output.outputR", upStretch+".input3D[0].input3Dx")
    cmds.connectAttr(stretch_OnOff+".output.outputR", loStretch+".input3D[0].input3Dx")
    
    cmds.connectAttr(ikfk_switch+".upArmStretch", armStretchIKFKOnOFF+".color1.color1R")
    cmds.connectAttr(ikfk_switch+".lowArmStretch", armStretchIKFKOnOFF+".color1.color1G")
    
    cmds.connectAttr(armStretchIKFKOnOFF+".outputR", armStretchOnOFF+".color1.color1R")
    cmds.connectAttr(armStretchIKFKOnOFF+".outputG", armStretchOnOFF+".color1.color1G")
    
    cmds.connectAttr(armStretchOnOFF+".outputR", upStretch+".input3D[1].input3Dx")
    cmds.connectAttr(armStretchOnOFF+".outputG", loStretch+".input3D[1].input3Dx")
    
    ## Connecting ik Joints scalex and scaleZY to Stretch and valume network
    
    cmds.connectAttr(upStretch+".output3D.output3Dx", ik_chain[0] + ".scaleX") ## Stretch Connection
    cmds.connectAttr(loStretch+".output3D.output3Dx", ik_chain[1] + ".scaleX") ## Stretch Connection
    
    cmds.connectAttr(stretch_OnOff+".outputG", ik_chain[1]+".scaleY") ## Volume Connection
    cmds.connectAttr(stretch_OnOff+".outputG", ik_chain[1]+".scaleZ") ## Volume Connection
    
    ## Controllers Color ##
    ctrl = cmds.ls(loIK_Ctrl, midIK_Ctrl, upIK_Ctrl, loFK_Ctrl, midFK_Ctrl, upFK_Ctrl, ikfk_switch)
    #ctrl = cmds.ls(sl=1)
    ctrlShp = cmds.listRelatives(ctrl, shapes=1)
    for color in ctrlShp:
        cmds.setAttr(color + ".overrideEnabled", 1)
        cmds.setAttr(color + ".overrideRGBColors", 1)
        cmds.setAttr(color + ".overrideColorRGB", R,G,B)
    
    print ("Auto Rig Has Been Created Successfully")

    autoLimbTest.rootJoint = root_chain

def createTwist(ctrlSize):
    """
    
    """
    rootJoint = autoLimbTest.rootJoint

    # listing joints
    chainList = [rootJoint[0]]
    for i in range(0,2):
        childJoint = cmds.listRelatives(chainList[-1], c=True, type="joint")[0]
        chainList.append(childJoint)

    for twist in (chainList[0], chainList[-1]):
        print(twist)
        cmds.select(cl=True)
        holdJoint = cmds.joint(n=twist.replace("_Jnt", "TwistHold_Jnt"))
        twistJoint = cmds.joint(n=twist.replace("_Jnt", "Twist_Jnt"))
        mat = cmds.xform(twist, q=1, m=1, ws=1)
        cmds.xform(holdJoint, m=mat, ws=1)

        par = cmds.pointConstraint(twist, chainList[-2], twistJoint, mo=0)
        cmds.delete(par)

        # setting up twist joints
        hold_loc = cmds.spaceLocator(n=twist.replace("_Jnt", "TwistHold_Loc"))[0]
        cmds.setAttr(hold_loc+".v",0)
        cmds.xform(hold_loc, m=mat, ws=1)
        cmds.move(ctrlSize, hold_loc, z=1, r=1, os=1)

        if "shoulder" in twist or "thigh" in twist or "Shoulder" in twist or "Thigh" in twist:
            parentjoint= cmds.listRelatives(twist, p=True, type="joint")
            cmds.parent(holdJoint, twist)
            cmds.parent(hold_loc, parentjoint)
            cmds.makeIdentity(holdJoint, apply = True, jo=1)

            if "L_" in twist:
                aimV = [1,0,0]
                upV=[0,0,1]
            if "R_" in twist:
                aimV = [-1,0,0]
                upV=[0,0,1]
            cmds.aimConstraint(chainList[-2], holdJoint, aimVector=aimV, upVector=upV, worldUpType="object", worldUpObject=hold_loc)
        
        elif "wrist" in twist or "ankle" in twist or "Wrist" in twist or "Ankle" in twist:
            parentjoint= twist
            cmds.parent(holdJoint, twist)
            cmds.parent(twistJoint, twistJoint, chainList[-2])
            cmds.parent(hold_loc, parentjoint)

            oriPar01 = cmds.orientConstraint(chainList[-2], holdJoint, mo=0)
            oriPar02 = cmds.orientConstraint(chainList[-2], twistJoint, mo=0)
            cmds.delete(oriPar01, oriPar02)

            cmds.makeIdentity(holdJoint, twistJoint, apply = True, jo=1)

            if "L_" in twist:
                aimV = [-1,0,0]
                upV=[0,0,1]
            if "R_" in twist:
                aimV = [1,0,0]
                upV=[0,0,1]
            cmds.aimConstraint(chainList[-2], holdJoint, aimVector=aimV, upVector=upV, worldUpType="object", worldUpObject=hold_loc)
        
        multi_node=cmds.createNode("multiplyDivide", n=twist.replace("_Jnt", "Twist_Multi"))

        ## set data and connect
        rootTwist = twist
        value = 0.5
        cmds.setAttr(multi_node+".input2X", value) # set data to half output
        twistAttr = "rx"
        if "ankle" in twist.lower():
            #rootTwist = holdJoint
            twistAttr = "rx"
            value = 0.5
            #print(rootTwist)
        cmds.setAttr(multi_node+".input2X", value) # set data to half output

        cmds.connectAttr(rootTwist+"."+twistAttr, multi_node+".input1X") # make connection
        cmds.connectAttr(multi_node+".outputX", twistJoint+".rx") # make connection

## USE THIS COMMOND TO RUN THE SCRIPT ##
#autoLimbTest("Character1", 4) ## Remove '#' From the command
