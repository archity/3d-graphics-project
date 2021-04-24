import glfw

from node import Node


class ProceduralAnimation(Node):
    def __init__(self, anim_func):
        super().__init__()
        self.gen_keyframe = anim_func

    def draw(self, projection, view, model):
        self.transform = self.gen_keyframe()
        super().draw(projection, view, model)

