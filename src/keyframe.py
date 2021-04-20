import glfw

from node import Node
from transform import rotate, translate, scale
from bisect import bisect_left
from transform import (quaternion_slerp, quaternion_matrix, quaternion,
                       quaternion_from_euler, lerp)


class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""

    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
        keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # 1. ensure time is within bounds else return boundary keyframe
        if time <= self.times[0]:
            return self.values[0]
        elif time >= self.times[len(self.times) - 1]:
            return self.values[len(self.times) - 1]

        # 2. search for closest index entry in self.times, using bisect_left function
        index_closest = bisect_left(self.times, time)

        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        f = (time - self.times[index_closest - 1]) / (self.times[index_closest] - self.times[index_closest - 1])

        interpolated_val = self.interpolate(self.values[index_closest], self.values[index_closest - 1], f)
        return interpolated_val


class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """

    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.translate_keys = KeyFrames(translate_keys)
        self.rotate_keys = KeyFrames(rotate_keys, interpolation_function=quaternion_slerp)
        self.scale_keys = KeyFrames(scale_keys)

    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """
        T = translate(self.translate_keys.value(time=time))
        R = quaternion_matrix(self.rotate_keys.value(time=time))
        S = scale(self.scale_keys.value(time=time))
        return T @ R @ S


class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """

    def __init__(self, translate_keys, rotate_keys, scale_keys):
        super().__init__()
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

    def draw(self, projection, view, model):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform = self.keyframes.value(glfw.get_time())
        super().draw(projection, view, model)
