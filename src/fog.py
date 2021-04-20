import glfw


class FogColour:
    def __init__(self):
        self.colour = [0, 0, 0]
        self.time = 0
        self.factor = (1 / 6000) * 14
        self.day_color = [0.6, 0.7, 0.7]
        self.night_colour = [0.2, 0.3, 0.3]

    def get_colour(self):
        self.time = glfw.get_time() * 1000
        self.time %= 24000
        if 0 <= self.time < 6000:
            self.colour = [0.2, 0.3, 0.3]
            # print(self.colour)

        elif 6000 <= self.time < 12000:
            if self.colour[0] < self.day_color[0]:
                self.colour[0] += self.factor
                self.colour[1] += self.factor
                self.colour[2] += self.factor
                # print(self.colour)

        elif 12000 <= self.time < 18000:
            self.colour = [0.6, 0.7, 0.7]
            # print(self.colour)

        else:
            if self.colour[0] > self.night_colour[0]:
                self.colour[0] -= self.factor
                self.colour[1] -= self.factor
                self.colour[2] -= self.factor
                # print(self.colour)

        return self.colour
