import glfw
import numpy as np


class FogColour:
    def __init__(self):
        self.colour = [0, 0, 0]
        self.time = 0
        self.time_period = 6000

        # 0.5 to make the transitions a little slower
        self.factor = (1 / self.time_period) * 0.5

        self.day_color = [0.6, 0.7, 0.7]
        self.night_colour = [0.2, 0.3, 0.3]
        self.light_pos = [[1000, 1000, 1000],
                          [-60, 7, -30],
                          [15, 7, 55],
                          [10, 7, -10]]

        self.day_atten = [[0, 0.00001, 0.0000004],
                          [1, 1, 1],
                          [1, 1, 1],
                          [1, 1, 1]]

        self.night_atten = [[.01, .0001, .000004],
                            [0.4, 0.001, 0.0005],
                            [0.4, 0.001, 0.004],
                            [0.4, 0.001, 0.004]]

        self.light_atten = [[0, 0.00001, 0.0000004],
                            [0.4, 0.001, 0.0005],
                            [0.4, 0.001, 0.004],
                            [0.4, 0.001, 0.004]]
        self.num_light_src = 4

        self.toggle_value = 8

        self.atten_factor = self.calc_transition_factors()
    def get_num_light_src(self):
        return self.num_light_src
    def calc_transition_factors(self):
        atten_diff = [[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0]]
        atten_factor = [[0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0]]

        for i in range(self.num_light_src):
            for j in range(3):
                atten_diff[i][j] = np.abs(self.day_atten[i][j] - self.night_atten[i][j])
                atten_factor[i][j] = atten_diff[i][j] * self.factor

        return atten_factor

    def get_atten(self):
        if self.toggle_value == 8:
            # Toggle day-night transition
            self.time = glfw.get_time() * 1000

            # Divide the time into 4 parts, each of length time_period
            self.time %= self.time_period * 4

        elif self.toggle_value == 6:
            # Day only
            self.time = self.time_period * 2 + 1
        elif self.toggle_value == 7:
            # Night only
            self.time = 0

        # Night
        if 0 <= self.time < self.time_period * 0.5:
            self.light_atten[0] = [.01, .0001, .000004]
            self.light_atten[1] = [0.4, 0.001, 0.0005]
            self.light_atten[2] = [0.4, 0.001, 0.004]
            self.light_atten[3] = [0.4, 0.001, 0.004]

        # Night to day transition
        elif 0.5 * self.time_period <= self.time < self.time_period * 2:

            if self.light_atten[0] > self.day_atten[0]:
                self.light_atten[0][0] -= self.atten_factor[0][0] * 20
                self.light_atten[0][1] -= self.atten_factor[0][1] * 20
                self.light_atten[0][2] -= self.atten_factor[0][2] * 20

            if self.light_atten[1] < self.day_atten[1]:
                self.light_atten[1][0] += self.atten_factor[1][0] / 1
                self.light_atten[1][1] += self.atten_factor[1][1] / 1
                self.light_atten[1][2] += self.atten_factor[1][2] / 1

            if self.light_atten[2] < self.day_atten[2]:
                self.light_atten[2][0] += self.atten_factor[2][0] / 1
                self.light_atten[2][1] += self.atten_factor[2][1] / 1
                self.light_atten[2][2] += self.atten_factor[2][2] / 1

            if self.light_atten[3] < self.day_atten[3]:
                self.light_atten[3][0] += self.atten_factor[3][0] / 1
                self.light_atten[3][1] += self.atten_factor[3][1] / 1
                self.light_atten[3][2] += self.atten_factor[3][2] / 1

            # print(self.light_atten[2])

        # Day
        elif 2 * self.time_period <= self.time < self.time_period * 2.5:
            self.light_atten[0] = [0, 0.00001, 0.0000004]
            self.light_atten[1] = [1, 1, 1]
            self.light_atten[2] = [1, 1, 1]
            self.light_atten[3] = [1, 1, 1]

        # Day to night transition
        else:
            if self.light_atten[0] < self.night_atten[0]:
                self.light_atten[0][0] += self.atten_factor[0][0] * 20
                self.light_atten[0][1] += self.atten_factor[0][1] * 20
                self.light_atten[0][2] += self.atten_factor[0][2] * 20

            if self.light_atten[1] > self.night_atten[1]:
                self.light_atten[1][0] -= self.atten_factor[1][0] * 1
                self.light_atten[1][1] -= self.atten_factor[1][1] * 1
                self.light_atten[1][2] -= self.atten_factor[1][2] * 1

            if self.light_atten[2] > self.night_atten[2]:
                self.light_atten[2][0] -= self.atten_factor[2][0] * 1
                self.light_atten[2][1] -= self.atten_factor[2][1] * 1
                self.light_atten[2][2] -= self.atten_factor[2][2] * 1

            if self.light_atten[3] > self.night_atten[3]:
                self.light_atten[3][0] -= self.atten_factor[3][0] * 1
                self.light_atten[3][1] -= self.atten_factor[3][1] * 1
                self.light_atten[3][2] -= self.atten_factor[3][2] * 1

        return self.light_atten

    def get_colour(self):
        if self.toggle_value == 8:
            # Toggle day-night transition
            self.time = glfw.get_time() * 1000
            self.time %= self.time_period * 4
        elif self.toggle_value == 6:
            # Day only
            self.time = self.time_period * 2
        elif self.toggle_value == 7:
            # Night only
            self.time = 0

        # Night
        if 0 <= self.time < 0.5*self.time_period:
            self.colour = [0.2, 0.3, 0.3]
            # print(self.colour)

        # Night to day transition
        elif 0.5*self.time_period <= self.time < self.time_period * 2:
            if self.colour[0] < self.day_color[0]:
                self.colour[0] += self.factor
                self.colour[1] += self.factor
                self.colour[2] += self.factor
                # print(self.colour)

        # Day
        elif 2 * self.time_period <= self.time < self.time_period * 2.5:
            self.colour = [0.6, 0.7, 0.7]
            # print(self.colour)

        # Day to night transition
        else:
            if self.colour[0] > self.night_colour[0]:
                self.colour[0] -= self.factor
                self.colour[1] -= self.factor
                self.colour[2] -= self.factor
                # print(self.colour)

        return self.colour
