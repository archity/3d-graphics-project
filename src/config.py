"""
Just a small utility file for providing the same instance
of FogColour class available for sharing between all
classes.
"""

# Fog related
from fog import FogColour
fog_colour = FogColour()


# Enable/disable sound
sound = True
if sound==True:
    import simpleaudio as sa
