import glfw

from node import Node


class ProceduralAnimation(Node):
    def __init__(self, anim_func, radius=10, x_offset=0, y_offset=0, z_offset=0, direction=0):
        super().__init__()
        self.gen_keyframe = anim_func
        self.radius = radius
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset
        self.direction = direction

    def draw(self, projection, view, model):
        self.transform = self.gen_keyframe(self.radius,
                                           self.x_offset,
                                           self.y_offset,
                                           self.z_offset,
                                           self.direction)
        super().draw(projection, view, model)

