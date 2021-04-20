import glfw

from node import Node


class ProceduralAnim(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, anim_func):
        super().__init__()
        self.gen_keyframe = anim_func

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform = self.gen_keyframe()  # transform belongs to parent class i,e, Node
        super().draw(projection, view, model)

