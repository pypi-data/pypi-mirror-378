# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import abel
import matplotlib.pyplot as plt

# Dribinski sample image
IM = abel.tools.analytical.SampleImage(n=501).func

# split into quadrants
origQ = abel.tools.symmetry.get_image_quadrants(IM)

# speed distribution
orig_speed = abel.tools.vmi.angular_integration_3D(origQ[0], origin=(-1, 0))

# forward Abel projection
fIM = abel.Transform(IM, direction="forward", method="hansenlaw").transform

# split projected image into quadrants
Q = abel.tools.symmetry.get_image_quadrants(fIM)
Q0 = Q[0].copy()

# onion_bordas inverse Abel transform
borQ0 = abel.onion_bordas.onion_bordas_transform(Q0)
# speed distribution
bor_speed = abel.tools.vmi.angular_integration_3D(borQ0, origin=(-1, 0))

plt.plot(*orig_speed, linestyle='dashed', label="Dribinski sample")
plt.plot(bor_speed[0], bor_speed[1], label="onion_bordas")
plt.xlim((0, 300))
plt.legend(loc=0)
plt.tight_layout()
# plt.savefig("plot_example_onion_bordas.png",dpi=100)
plt.show()
