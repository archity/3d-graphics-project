import glfw

from core import Node
from transform import rotate, translate, scale
from bisect import bisect_left
from transform import (quaternion_slerp, quaternion_matrix, quaternion,
                       quaternion_from_euler, lerp)


class ProceduralAnim(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, anim_func):
        super().__init__()
        self.gen_keyframe = anim_func

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform = self.gen_keyframe()  # transform belongs to parent class i,e, Node
        super().draw(projection, view, model)

