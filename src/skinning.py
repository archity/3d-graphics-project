import numpy as np
import glfw
import OpenGL.GL as GL
from mesh import Mesh
from node import Node
from keyframe import TransformKeyFrames
from transform import identity

# -------------- Linear Blend Skinning : TP7 ---------------------------------
MAX_VERTEX_BONES = 4
MAX_BONES = 128


class SkinnedMesh(Mesh):
    """class of skinned mesh nodes in scene graph """

    def __init__(self, shader, attribs, bone_nodes, bone_offsets, index=None):
        super().__init__(shader, attribs, index)

        # store skinning data
        self.bone_nodes = bone_nodes
        self.bone_offsets = np.array(bone_offsets, np.float32)

    def draw(self, projection, view, model, primitives=GL.GL_TRIANGLES):
        """ skinning object draw method """
        GL.glUseProgram(self.shader.glid)

        # bone world transform matrices need to be passed for skinning
        world_transforms = [node.world_transform for node in self.bone_nodes]
        bone_matrix = world_transforms @ self.bone_offsets
        loc = GL.glGetUniformLocation(self.shader.glid, 'bone_matrix')
        GL.glUniformMatrix4fv(loc, len(self.bone_nodes), True, bone_matrix)

        super().draw(projection, view, model)


# -------- Skinning Control for Keyframing Skinning Mesh Bone Transforms ------
class SkinningControlNode(Node):
    """ Place node with transform keys above a controlled subtree """

    def __init__(self, *keys, transform=identity()):
        super().__init__(transform=transform)
        self.keyframes = TransformKeyFrames(*keys) if keys[0] else None
        self.world_transform = identity()

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        if self.keyframes:  # no keyframe update should happens if no keyframes
            self.transform = self.keyframes.value(glfw.get_time())

        # store world transform for skinned meshes using this node as bone
        self.world_transform = model @ self.transform

        # default node behaviour (call children's draw method)
        super().draw(projection, view, model)
