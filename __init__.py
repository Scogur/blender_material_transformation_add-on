bl_info = {
    "name": "Material Transformer",
    "author": "Scogur",
    "version": (1, 0),
    "blender": (3, 5, 0),
    "location": "Material Properties",
    "description": "Transforms a material using a Fresnel-like blend with a random color.",
    "warning": "",
    "category": "Material",
}

import bpy
import random



def debug(text):
    print(text)


def create_fresnel_like_material(original_material):

    new_material = bpy.data.materials.new(name=original_material.name + "_transformed")
    new_material.use_nodes = True
    nodes = new_material.node_tree.nodes
    color = (0.0, 0.0, 1.0, 1.0)

    try:
        color = original_material.diffuse_color if original_material.use_nodes is False else original_material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
    except:
        print("Error: Could not get original material color. Using default white.")
        color = (0.0, 0.0, 1.0, 1.0)

    nodes.remove(nodes["Principled BSDF"])

    output_node = nodes["Material Output"]
    gamma_node = nodes.new("ShaderNodeGamma")
    mix_node = nodes.new("ShaderNodeMixRGB")
    mix_shader_node = nodes.new("ShaderNodeMixShader")
    subtract_node = nodes.new("ShaderNodeMath")
    subtract_node.operation = 'SUBTRACT'
    dot_product_node = nodes.new("ShaderNodeVectorMath")
    dot_product_node.operation = 'DOT_PRODUCT'
    separate_xyz_node = nodes.new("ShaderNodeSeparateXYZ")
    greater_than_node = nodes.new("ShaderNodeMath")
    greater_than_node.operation = 'GREATER_THAN'
    geometry_node = nodes.new("ShaderNodeNewGeometry")

    subtract_node.inputs[0].default_value = 1.0
    greater_than_node.inputs[0].default_value = 0.1
    gamma_node.inputs[0].default_value = color

    random_color = (random.random(), random.random(), random.random(), 1.0)

    r_node = nodes.new("ShaderNodeValue")
    r_node.outputs[0].default_value = random_color[0]
    g_node = nodes.new("ShaderNodeValue")
    g_node.outputs[0].default_value = random_color[1]
    b_node = nodes.new("ShaderNodeValue")
    b_node.outputs[0].default_value = random_color[2]

    rgb_combine = nodes.new("ShaderNodeCombineXYZ")
    new_material.node_tree.links.new(r_node.outputs[0], rgb_combine.inputs[0])
    new_material.node_tree.links.new(g_node.outputs[0], rgb_combine.inputs[1])
    new_material.node_tree.links.new(b_node.outputs[0], rgb_combine.inputs[2])
    new_material.node_tree.links.new(rgb_combine.outputs[0], mix_shader_node.inputs[2])

    new_material.node_tree.links.new(rgb_combine.outputs[0], mix_node.inputs[1])
    new_material.node_tree.links.new(gamma_node.outputs[0], mix_node.inputs[2])
    new_material.node_tree.links.new(subtract_node.outputs[0], mix_node.inputs[0])
    new_material.node_tree.links.new(geometry_node.outputs[1], dot_product_node.inputs[0])
    new_material.node_tree.links.new(geometry_node.outputs[4], dot_product_node.inputs[1])
    new_material.node_tree.links.new(dot_product_node.outputs[0], subtract_node.inputs[1])

    new_material.node_tree.links.new(geometry_node.outputs[1], separate_xyz_node.inputs[0])
    new_material.node_tree.links.new(separate_xyz_node.outputs[2], greater_than_node.inputs[1])
    new_material.node_tree.links.new(greater_than_node.outputs[0], mix_shader_node.inputs[0])


    new_material.node_tree.links.new(mix_node.outputs[0], mix_shader_node.inputs[1])
    new_material.node_tree.links.new(mix_shader_node.outputs[0], output_node.inputs[0])
    return new_material


class MaterialTransformerPanel(bpy.types.Panel):
    bl_label = "Material Transformer"
    bl_idname = "MATERIAL_PT_transformer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        layout.operator("material.transform")


class MaterialTransformerOperator(bpy.types.Operator):
    bl_idname = "material.transform"
    bl_label = "Transform Material"

    def execute(self, context):
        material = context.material
        if material:
            new_material = create_fresnel_like_material(material)
            context.object.active_material = new_material
            # Optional: delete the original material
            # bpy.data.materials.remove(material)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MaterialTransformerPanel)
    bpy.utils.register_class(MaterialTransformerOperator)


def unregister():
    bpy.utils.unregister_class(MaterialTransformerPanel)
    bpy.utils.unregister_class(MaterialTransformerOperator)


if __name__ == "__main__":
    register()