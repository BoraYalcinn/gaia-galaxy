"""Generate an illustrative barred spiral galaxy as a binary star file.

This is NOT real data. Gaia only covers a few kiloparsecs around the Sun, so
this procedural layer fills in a plausible Milky-Way-like galaxy around it.
The galaxy has a central bar, two major and two minor spiral arms, and is
large enough that the Gaia region (a few kpc around the Sun, ~8 kpc from the
center) looks like a small patch of it.

Output: data/galaxy.bin  (same layout as stars.bin: 7 float32 per star)
    x, y, z, r, g, b, abs_mag
Coordinates are in parsecs, origin at the galactic center, +Y is up and the
disk lies in the XZ plane (same convention as tools/convert_gaia.py).
"""

import numpy as np

OUTPUT_PATH = "data/galaxy.bin"
N_STARS = 5_000_000
SEED = 42

# --- Population shares ---
BULGE_FRACTION = 0.14       # share of all stars in the central region (bar + bulge)
BAR_SHARE = 0.60            # share of the central stars that form the bar
ARM_FRACTION = 0.70         # share of disk stars that sit in spiral arms

# --- Disk ---
DISK_SCALE_LENGTH = 5000.0  # pc, exponential disk (interarm stars)
ARM_SCALE_LENGTH = 7000.0   # pc, arms reach farther out than the smooth disk
MAX_RADIUS = 32000.0        # pc
DISK_SCALE_HEIGHT = 300.0   # pc (interarm disk)
ARM_SCALE_HEIGHT = 150.0    # pc (arms are thinner)

# --- Spiral arms ---
N_ARMS = 4
ARM_WEIGHTS = np.array([0.32, 0.18, 0.32, 0.18])  # arms 0 and 2 are the major arms
ARM_PITCH_DEG = 15.0        # how tightly the arms wind (bigger = more open)
ARM_R0 = 3500.0             # pc, radius where the arm phase starts (bar ends)
ARM_MIN_RADIUS = 3500.0     # pc, no arm stars closer to the center than this
ARM_SCATTER_RAD = 0.2      # angular scatter of stars around an arm

# --- Bar and bulge ---
BAR_ANGLE_DEG = 27.0        # bar orientation in the disk plane
BAR_SIGMA_LONG = 1800.0     # pc, along the bar
BAR_SIGMA_SHORT = 500.0     # pc, across the bar
BAR_SIGMA_Y = 350.0         # pc, thickness
BULGE_SIGMA_XZ = 600.0      # pc, small round bulge inside the bar
BULGE_SIGMA_Y = 450.0       # pc

# --- Visibility: brighten outer stars so the far disk does not vanish ---
OUTER_BOOST = 1.0           # 0 = off; brightness grows like (R / R0)^OUTER_BOOST
OUTER_BOOST_R0 = 4000.0     # pc

COLOR_ARM = np.array([0.65, 0.75, 1.00])      # young, blue-white
COLOR_DISK = np.array([1.00, 0.92, 0.75])     # older, yellow-white
COLOR_BULGE = np.array([1.00, 0.75, 0.45])    # old, orange


def sample_radius(rng, n, scale_length, min_radius=0.0):
    """Radii for an exponential disk: pdf ~ R * exp(-R/h) = Gamma(2, h).

    Values outside [min_radius, MAX_RADIUS] are resampled (not clipped, which
    would pile stars up on a ring).
    """
    r = rng.gamma(2.0, scale_length, n)
    bad = (r < min_radius) | (r > MAX_RADIUS)
    while bad.any():
        r[bad] = rng.gamma(2.0, scale_length, bad.sum())
        bad = (r < min_radius) | (r > MAX_RADIUS)
    return r


def colors(rng, base, n):
    """Base color with a little per-star variation."""
    noise = rng.normal(0.0, 0.06, (n, 3))
    return np.clip(base + noise, 0.0, 1.0)


def main():
    rng = np.random.default_rng(SEED)
    bar_angle = np.radians(BAR_ANGLE_DEG)

    n_central = int(N_STARS * BULGE_FRACTION)
    n_bar = int(n_central * BAR_SHARE)
    n_bulge = n_central - n_bar
    n_disk = N_STARS - n_central
    n_arm = int(n_disk * ARM_FRACTION)
    n_inter = n_disk - n_arm

    # --- Spiral arms: logarithmic spiral  theta = ln(R/R0) / tan(pitch) ---
    # The arms start at the bar angle, so they appear to leave the bar ends.
    r_arm = sample_radius(rng, n_arm, ARM_SCALE_LENGTH, ARM_MIN_RADIUS)
    arm_index = rng.choice(N_ARMS, size=n_arm, p=ARM_WEIGHTS / ARM_WEIGHTS.sum())
    theta_arm = (bar_angle
                 + arm_index * (2.0 * np.pi / N_ARMS)
                 + np.log(r_arm / ARM_R0) / np.tan(np.radians(ARM_PITCH_DEG))
                 + rng.normal(0.0, ARM_SCATTER_RAD, n_arm))
    y_arm = rng.laplace(0.0, ARM_SCALE_HEIGHT, n_arm)

    # --- Interarm disk: uniform angle ---
    r_inter = sample_radius(rng, n_inter, DISK_SCALE_LENGTH)
    theta_inter = rng.uniform(0.0, 2.0 * np.pi, n_inter)
    y_inter = rng.laplace(0.0, DISK_SCALE_HEIGHT, n_inter)

    # --- Bar: elongated gaussian, rotated by the bar angle ---
    u = rng.normal(0.0, BAR_SIGMA_LONG, n_bar)    # along the bar
    v = rng.normal(0.0, BAR_SIGMA_SHORT, n_bar)   # across the bar
    bar_x = u * np.cos(bar_angle) - v * np.sin(bar_angle)
    bar_z = u * np.sin(bar_angle) + v * np.cos(bar_angle)
    bar_y = rng.normal(0.0, BAR_SIGMA_Y, n_bar)

    # --- Small round bulge ---
    bx = rng.normal(0.0, BULGE_SIGMA_XZ, n_bulge)
    bz = rng.normal(0.0, BULGE_SIGMA_XZ, n_bulge)
    by = rng.normal(0.0, BULGE_SIGMA_Y, n_bulge)

    # Polar -> cartesian in the XZ plane, then stack all components.
    x = np.concatenate([r_arm * np.cos(theta_arm), r_inter * np.cos(theta_inter), bar_x, bx])
    z = np.concatenate([r_arm * np.sin(theta_arm), r_inter * np.sin(theta_inter), bar_z, bz])
    y = np.concatenate([y_arm, y_inter, bar_y, by])

    rgb = np.concatenate([
        colors(rng, COLOR_ARM, n_arm),
        colors(rng, COLOR_DISK, n_inter),
        colors(rng, COLOR_BULGE, n_bar),
        colors(rng, COLOR_BULGE, n_bulge),
    ])

    # Pseudo absolute magnitudes. The renderer scales these layers separately
    # (uFluxScale), so only the spread matters here. Outer stars get a boost:
    # flux grows like (R / R0)^OUTER_BOOST, i.e. 2.5 * boost * log10 magnitudes.
    radius = np.hypot(x, z)
    abs_mag = rng.normal(10.0, 1.5, N_STARS)
    abs_mag -= 2.5 * OUTER_BOOST * np.log10(np.maximum(radius, OUTER_BOOST_R0) / OUTER_BOOST_R0)

    stars = np.column_stack([x, y, z, rgb, abs_mag]).astype(np.float32)
    stars.tofile(OUTPUT_PATH)

    print(f"stars written : {len(stars)}")
    print(f"x range (pc)  : {x.min():.0f} .. {x.max():.0f}")
    print(f"y range (pc)  : {y.min():.0f} .. {y.max():.0f}")
    print(f"z range (pc)  : {z.min():.0f} .. {z.max():.0f}")
    print(f"radius pct    : 50%={np.percentile(radius, 50):.0f}  "
          f"90%={np.percentile(radius, 90):.0f}  99%={np.percentile(radius, 99):.0f} pc")
    print(f"file size     : {stars.nbytes} bytes")


if __name__ == "__main__":
    main()