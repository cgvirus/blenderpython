# 「プロパティ」エリア > 「マテリアル」タブ > リスト右の▼
# "Propaties" Area > "Material" Tab > List Right ▼

import bpy

################
# オペレーター #
################


class RemoveNoAssignMaterial(bpy.types.Operator):
    bl_idname = "material.remove_no_assign_material"
    bl_label = "Delete Non-assignment Material"
    bl_description = "Delete all one assigned to surface material"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (len(obj.material_slots) <= 0):
            return False
        return True

    def execute(self, context):
        preActiveObj = context.active_object
        for obj in context.selected_objects:
            if (obj.type == "MESH"):
                context.scene.objects.active = obj
                preActiveMaterial = obj.active_material
                slots = []
                for slot in obj.material_slots:
                    slots.append((slot.name, 0))
                me = obj.data
                for face in me.polygons:
                    slots[face.material_index] = (slots[face.material_index][0], slots[face.material_index][1] + 1)
                for name, count in slots:
                    if (name != "" and count == 0):
                        i = 0
                        for slot in obj.material_slots:
                            if (slot.name == name):
                                break
                            i += 1
                        obj.active_material_index = i
                        bpy.ops.object.material_slot_remove()
        context.scene.objects.active = preActiveObj
        return {'FINISHED'}


class RemoveAllMaterialSlot(bpy.types.Operator):
    bl_idname = "material.remove_all_material_slot"
    bl_label = "Remove all material slots"
    bl_description = "Delete all material slots for this object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (len(obj.material_slots) <= 0):
            return False
        return True

    def execute(self, context):
        activeObj = context.active_object
        if (activeObj.type == "MESH"):
            while True:
                if (0 < len(activeObj.material_slots)):
                    bpy.ops.object.material_slot_remove()
                else:
                    break
        return {'FINISHED'}


class RemoveEmptyMaterialSlot(bpy.types.Operator):
    bl_idname = "material.remove_empty_material_slot"
    bl_label = "Remove empty material slots"
    bl_description = "Delete all material of this object has not been assigned material slots"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        for slot in obj.material_slots:
            if (not slot.material):
                return True
        return False

    def execute(self, context):
        activeObj = context.active_object
        if (activeObj.type == "MESH"):
            slots = activeObj.material_slots[:]
            slots.reverse()
            i = 0
            for slot in slots:
                active_material_index = i
                if (not slot.material):
                    bpy.ops.object.material_slot_remove()
                i += 1
        return {'FINISHED'}


class SetTransparentBackSide(bpy.types.Operator):
    bl_idname = "material.set_transparent_back_side"
    bl_label = "Set transparent face back"
    bl_description = "Sets shader nodes transparently mesh back"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        if (not mat):
            return False
        if (mat.node_tree):
            if (len(mat.node_tree.nodes) == 0):
                return True
        if (not mat.use_nodes):
            return True
        return False

    def execute(self, context):
        mat = context.material
        mat.use_nodes = True
        if (mat.node_tree):
            for node in mat.node_tree.nodes:
                if (node):
                    mat.node_tree.nodes.remove(node)
        mat.use_transparency = True
        node_mat = mat.node_tree.nodes.new('ShaderNodeMaterial')
        node_out = mat.node_tree.nodes.new('ShaderNodeOutput')
        node_geo = mat.node_tree.nodes.new('ShaderNodeGeometry')
        node_mat.material = mat
        node_out.location = [node_out.location[0] + 500, node_out.location[1]]
        node_geo.location = [node_geo.location[0] + 150, node_geo.location[1] - 150]
        mat.node_tree.links.new(node_mat.outputs[0], node_out.inputs[0])
        mat.node_tree.links.new(node_geo.outputs[8], node_out.inputs[1])
        return {'FINISHED'}


class MoveMaterialSlotTop(bpy.types.Operator):
    bl_idname = "material.move_material_slot_top"
    bl_label = "Slot to Top"
    bl_description = "Active material slots on top moves"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (not obj):
            return False
        if (len(obj.material_slots) <= 2):
            return False
        if (obj.active_material_index <= 0):
            return False
        return True

    def execute(self, context):
        activeObj = context.active_object
        for i in range(activeObj.active_material_index):
            bpy.ops.object.material_slot_move(direction='UP')
        return {'FINISHED'}


class MoveMaterialSlotBottom(bpy.types.Operator):
    bl_idname = "material.move_material_slot_bottom"
    bl_label = "Slot to Bottom"
    bl_description = "Move active material slot at bottom"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (not obj):
            return False
        if (len(obj.material_slots) <= 2):
            return False
        if (len(obj.material_slots) - 1 <= obj.active_material_index):
            return False
        return True

    def execute(self, context):
        activeObj = context.active_object
        lastSlotIndex = len(activeObj.material_slots) - 1
        for i in range(lastSlotIndex - activeObj.active_material_index):
            bpy.ops.object.material_slot_move(direction='DOWN')
        return {'FINISHED'}

################
# メニュー追加 #
################

# メニューのオン/オフの判定


def IsMenuEnable(self_id):
    for id in bpy.context.user_preferences.addons['Scramble Addon'].preferences.disabled_menu.split(','):
        if (id == self_id):
            return False
    else:
        return True

# メニューを登録する関数


def menu(self, context):
    if (IsMenuEnable(__name__.split('.')[-1])):
        self.layout.separator()
        self.layout.operator(MoveMaterialSlotTop.bl_idname, icon='PLUGIN', text="To Top")
        self.layout.operator(MoveMaterialSlotBottom.bl_idname, icon='PLUGIN', text="To Bottom")
        self.layout.separator()
        self.layout.operator(RemoveAllMaterialSlot.bl_idname, icon='PLUGIN')
        self.layout.operator(RemoveEmptyMaterialSlot.bl_idname, icon='PLUGIN')
        self.layout.operator(RemoveNoAssignMaterial.bl_idname, icon='PLUGIN')
        self.layout.separator()
        self.layout.operator(SetTransparentBackSide.bl_idname, icon='PLUGIN')
    if (context.user_preferences.addons['Scramble Addon'].preferences.use_disabled_menu):
        self.layout.separator()
        self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
