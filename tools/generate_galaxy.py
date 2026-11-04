"""Generate an illustrative spiral galaxy as a binary star file.

This is NOT real data. Gaia only covers a few kiloparsecs around the Sun, so
this procedural layer fills in a plausible Milky-Way-like galaxy around it.

Output: data/galaxy.bin  (same layout as stars.bin: 7 float32 per star)
    x, y, z, r, g, b, abs_mag
Coordinates are in parsecs, origin at the galactic center, +Y is up and the
disk lies in the XZ plane (same convention as tools/convert_gaia.py).
"""

import numpy as np

OUTPUT_PATH = "data/galaxy.bin"
N_STARS = 1_500_000
SEED = 42

BULGE_FRACTION = 0.12       # share of stars in the central bulge
ARM_FRACTION = 0.55         # share of disk stars that sit in spiral arms

DISK_SCALE_LENGTH = 2600.0  # pc, exponential disk
MAX_RADIUS = 16000.0        # pc
DISK_SCALE_HEIGHT = 300.0   # pc (interarm disk)
ARM_SCALE_HEIGHT = 150.0    # pc (arms are thinner)

N_ARMS = 4
ARM_FRACTION = 0.70         # share of disk stars that sit in spiral arms
ARM_PITCH_DEG = 15.0        # how tightly the arms wind (bigger = more open)
ARM_R0 = 3000.0             # pc, radius where the arm phase starts
ARM_MIN_RADIUS = 3000.0     # pc, no arm stars closer to the center than this
ARM_SCATTER_RAD = 0.18      # angular scatter of stars around an arm

BULGE_SIGMA_XZ = 800.0      # pc
BULGE_SIGMA_Y = 500.0       # pc

COLOR_ARM = np.array([0.65, 0.75, 1.00])      # young, blue-white
COLOR_DISK = np.array([1.00, 0.92, 0.75])     # older, yellow-white
COLOR_BULGE = np.array([1.00, 0.75, 0.45])    # old, orange


def sample_disk_radius(rng, n):
    """Radii for an exponential disk: pdf ~ R * exp(-R/h) = Gamma(2, h)."""
    r = rng.gamma(2.0, DISK_SCALE_LENGTH, n)
    too_far = r > MAX_RADIUS
    while too_far.any():                      # resample instead of clipping
        r[too_far] = rng.gamma(2.0, DISK_SCALE_LENGTH, too_far.sum())
        too_far = r > MAX_RADIUS
    return r

def sample_arm_radius(rng, n):
    """Like the disk radius, but keeps arms out of the inner region."""
    r = sample_disk_radius(rng, n)
    too_close = r < ARM_MIN_RADIUS
    while too_close.any():
        r[too_close] = sample_disk_radius(rng, too_close.sum())
        too_close = r < ARM_MIN_RADIUS
    return r

def colors(rng, base, n):
    """Base color with a little per-star variation."""
    noise = rng.normal(0.0, 0.06, (n, 3))
    return np.clip(base + noise, 0.0, 1.0)


def main():
    rng = np.random.default_rng(SEED)

    n_bulge = int(N_STARS * BULGE_FRACTION)
    n_disk = N_STARS - n_bulge
    n_arm = int(n_disk * ARM_FRACTION)
    n_inter = n_disk - n_arm

    # --- Spiral arms: logarithmic spiral  theta = ln(R/R0) / tan(pitch) ---
    r_arm = sample_arm_radius(rng, n_arm)
    arm_index = rng.integers(0, N_ARMS, n_arm)
    theta_arm = (arm_index * (2.0 * np.pi / N_ARMS)+ np.log(r_arm / ARM_R0) / np.tan(np.radians(ARM_PITCH_DEG))+ rng.normal(0.0, ARM_SCATTER_RAD, n_arm))
    y_arm = rng.laplace(0.0, ARM_SCALE_HEIGHT, n_arm)

    # --- Interarm disk: uniform angle ---
    r_inter = sample_disk_radius(rng, n_inter)
    theta_inter = rng.uniform(0.0, 2.0 * np.pi, n_inter)
    y_inter = rng.laplace(0.0, DISK_SCALE_HEIGHT, n_inter)

    # --- Bulge: flattened gaussian blob ---
    bx = rng.normal(0.0, BULGE_SIGMA_XZ, n_bulge)
    bz = rng.normal(0.0, BULGE_SIGMA_XZ, n_bulge)
    by = rng.normal(0.0, BULGE_SIGMA_Y, n_bulge)

    # Polar -> cartesian in the XZ plane.
    x = np.concatenate([r_arm * np.cos(theta_arm), r_inter * np.cos(theta_inter), bx])
    z = np.concatenate([r_arm * np.sin(theta_arm), r_inter * np.sin(theta_inter), bz])
    y = np.concatenate([y_arm, y_inter, by])

    rgb = np.concatenate([
        colors(rng, COLOR_ARM, n_arm),
        colors(rng, COLOR_DISK, n_inter),
        colors(rng, COLOR_BULGE, n_bulge),
    ])

    # Pseudo absolute magnitudes. The renderer scales these layers separately
    # (uFluxScale), so only the spread matters here.
    abs_mag = rng.normal(10.0, 1.5, N_STARS)

    stars = np.column_stack([x, y, z, rgb, abs_mag]).astype(np.float32)
    stars.tofile(OUTPUT_PATH)

    print(f"stars written : {len(stars)}")
    print(f"x range (pc)  : {x.min():.0f} .. {x.max():.0f}")
    print(f"y range (pc)  : {y.min():.0f} .. {y.max():.0f}")
    print(f"z range (pc)  : {z.min():.0f} .. {z.max():.0f}")
    print(f"file size     : {stars.nbytes} bytes")


if __name__ == "__main__":
    main()