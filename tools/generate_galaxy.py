"""Generate an illustrative Milky Way plus its neighbor galaxies as a star file.

This is NOT real data. Gaia only covers a few kiloparsecs around the Sun, so
this procedural layer fills in a plausible Milky-Way-like galaxy around it
(central bar, two major and two minor spiral arms), and places neighbor
galaxies at their real positions and distances: Sagittarius dwarf, the
Magellanic Clouds, several dwarf spheroidals, Andromeda (M31) and Triangulum
(M33). Beyond them, hundreds of procedural field galaxies (spirals, ellipticals,
irregulars) are scattered between a few and ~20 Mpc, with the real Virgo,
Fornax, M81, Centaurus A, Sculptor and Leo groups as clusters. Their internal
structure and the field population are only a rough, illustrative model.

Output: data/galaxy.bin  (same layout as stars.bin: 7 float32 per star)
    x, y, z, r, g, b, abs_mag
Coordinates are in parsecs, origin at the galactic center, +Y is up and the
disk lies in the XZ plane (same convention as tools/convert_gaia.py).
"""

import numpy as np

OUTPUT_PATH = "data/galaxy.bin"
N_STARS = 5_000_000
SEED = 42

# --- Population shares (Milky Way) ---
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
ARM_SCATTER_RAD = 0.2       # angular scatter of stars around an arm

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

# --- Neighbor galaxies ---
# The galaxy layer is drawn with distance falloff off, so a neighbor star is as
# bright as a Milky Way star. Neighbors are squeezed into a tiny angular size,
# so their stars pile up; this makes them fainter (magnitudes, bigger = dimmer).
NEIGHBOR_DIM_MAG = 3.0

SUN_X = -8122.0             # pc, Sun position in the galactocentric frame
SUN_Z_UP = 21.0             # pc

COLOR_ARM = np.array([0.65, 0.75, 1.00])      # young, blue-white
COLOR_DISK = np.array([1.00, 0.92, 0.75])     # older, yellow-white
COLOR_BULGE = np.array([1.00, 0.75, 0.45])    # old, orange
COLOR_DWARF = np.array([1.00, 0.85, 0.60])    # old population, yellow-orange
COLOR_IRREGULAR = np.array([0.80, 0.85, 1.00])  # bluish, star-forming

# name, galactic l (deg), galactic b (deg), distance (kpc), kind, parameters
#   spiral    : n_stars, scale_length_pc, max_r_pc, thickness_pc, n_arms,
#               pitch_deg, inclination_deg, position_angle_deg
#   irregular : n_stars, scale_length_pc, max_r_pc, thickness_pc, bar_sigma_pc,
#               inclination_deg, position_angle_deg
#   dwarf     : n_stars, sigma_x_pc, sigma_y_pc, sigma_z_pc
NEIGHBORS = [
    ("Sagittarius dSph", 5.6, -14.2, 26.0, "dwarf", (100_000, 2500.0, 700.0, 700.0)),
    ("LMC", 280.5, -32.9, 50.0, "irregular", (300_000, 1500.0, 7000.0, 400.0, 1000.0, 25.0, 130.0)),
    ("SMC", 302.8, -44.3, 62.0, "irregular", (100_000, 1000.0, 4000.0, 600.0, 0.0, 40.0, 45.0)),
    ("Draco", 86.4, 34.7, 76.0, "dwarf", (25_000, 500.0, 300.0, 300.0)),
    ("Ursa Minor", 104.9, 44.8, 76.0, "dwarf", (25_000, 500.0, 250.0, 250.0)),
    ("Sculptor", 287.5, -83.2, 86.0, "dwarf", (30_000, 600.0, 350.0, 350.0)),
    ("Sextans", 243.5, 42.3, 86.0, "dwarf", (25_000, 800.0, 500.0, 500.0)),
    ("Carina", 260.1, -22.2, 105.0, "dwarf", (25_000, 450.0, 300.0, 300.0)),
    ("Fornax", 237.1, -65.7, 147.0, "dwarf", (40_000, 700.0, 500.0, 500.0)),
    ("Andromeda (M31)", 121.2, -21.6, 780.0, "spiral", (800_000, 5300.0, 30000.0, 500.0, 2, 12.0, 77.0, 38.0)),
    ("Triangulum (M33)", 133.6, -31.3, 840.0, "spiral", (200_000, 1800.0, 9000.0, 300.0, 2, 20.0, 55.0, 20.0)),
]


# --- Procedural field galaxies (hundreds of them, beyond the Local Group) ---
N_FIELD_GALAXIES = 600
FIELD_MIN_MPC = 1.5             # nothing closer than this to the Sun
FIELD_MAX_MPC = 20.0
FIELD_CLUSTERED_FRACTION = 0.45 # share of galaxies that sit in the known groups below
FIELD_STARS_PER_GALAXY = (10000, 50000)  # min / max stars (scales with galaxy size)
FIELD_TYPE_SHARES = (0.50, 0.32, 0.18)  # spiral, elliptical, irregular
FIELD_BASE_DIM = 4.0            # magnitudes; the field stars are very compressed
FIELD_DISTANCE_DIM = 3.0        # extra dimming per decade of distance (far = fainter)

# name, galactic l, galactic b, distance (Mpc), spread (Mpc), relative weight
FIELD_GROUPS = [
    ("M81 group", 142.1, 40.9, 3.6, 0.4, 1.0),
    ("Sculptor group", 97.4, -87.9, 3.5, 0.4, 1.0),
    ("Centaurus A group", 309.5, 19.4, 3.8, 0.5, 1.0),
    ("Leo I group", 234.0, 57.0, 10.0, 0.6, 1.5),
    ("Virgo cluster", 283.8, 74.5, 16.5, 1.2, 4.0),
    ("Fornax cluster", 236.7, -53.6, 19.0, 0.9, 2.5),
]


def sample_radius(rng, n, scale_length, min_radius=0.0, max_radius=MAX_RADIUS):
    """Radii for an exponential disk: pdf ~ R * exp(-R/h) = Gamma(2, h).

    Values outside [min_radius, max_radius] are resampled (not clipped, which
    would pile stars up on a ring).
    """
    r = rng.gamma(2.0, scale_length, n)
    bad = (r < min_radius) | (r > max_radius)
    while bad.any():
        r[bad] = rng.gamma(2.0, scale_length, bad.sum())
        bad = (r < min_radius) | (r > max_radius)
    return r


def colors(rng, base, n):
    """Base color with a little per-star variation."""
    noise = rng.normal(0.0, 0.06, (n, 3))
    return np.clip(base + noise, 0.0, 1.0)


def sun_frame_to_scene(l_deg, b_deg, dist_kpc):
    """Galactic (l, b, distance from the Sun) -> scene coordinates in parsecs.

    Same convention as convert_gaia.py: galactocentric (gx, gy, gz) is remapped
    to (x, y, z) = (gx, gz, -gy), so +Y is galactic north.
    """
    l, b, d = np.radians(l_deg), np.radians(b_deg), dist_kpc * 1000.0
    gx = d * np.cos(b) * np.cos(l) + SUN_X
    gy = d * np.cos(b) * np.sin(l)
    gz = d * np.sin(b) + SUN_Z_UP
    return np.array([gx, gz, -gy])


def orient(points, inclination_deg, position_angle_deg):
    """Tilt a flat XZ-plane galaxy (about X), then spin it (about Y)."""
    inc, pa = np.radians(inclination_deg), np.radians(position_angle_deg)
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    y2 = y * np.cos(inc) - z * np.sin(inc)
    z2 = y * np.sin(inc) + z * np.cos(inc)
    x3 = x * np.cos(pa) + z2 * np.sin(pa)
    z3 = -x * np.sin(pa) + z2 * np.cos(pa)
    return np.column_stack([x3, y2, z3])


def make_milky_way(rng):
    """Barred spiral Milky Way. Returns positions (N,3), rgb (N,3), abs_mag (N,)."""
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

    return np.column_stack([x, y, z]), rgb, abs_mag


def make_galaxy(rng, center, kind, params, dim):
    """One galaxy around `center` (scene pc). Returns positions, rgb, abs_mag.

    `dim` is added to the absolute magnitudes (bigger = fainter).
    """
    n = params[0]

    if kind == "dwarf":
        # Gaussian blob (dwarf spheroidal / elliptical). Optional orientation.
        sx, sy, sz = params[1:4]
        local = np.column_stack([rng.normal(0, sx, n), rng.normal(0, sy, n), rng.normal(0, sz, n)])
        if len(params) > 4:
            local = orient(local, params[4], params[5])
        rgb = colors(rng, COLOR_DWARF, n)

    elif kind == "irregular":
        _, scale, max_r, thick, bar_sigma, inc, pa = params
        n_bar = int(n * 0.35) if bar_sigma > 0 else 0
        n_disk = n - n_bar
        r = sample_radius(rng, n_disk, scale, 0.0, max_r)
        th = rng.uniform(0.0, 2.0 * np.pi, n_disk)
        disk = np.column_stack([r * np.cos(th), rng.laplace(0, thick, n_disk), r * np.sin(th)])
        bar = np.column_stack([rng.normal(0, bar_sigma, n_bar),
                               rng.normal(0, thick, n_bar),
                               rng.normal(0, bar_sigma * 0.35, n_bar)]) if n_bar else np.empty((0, 3))
        local = orient(np.vstack([disk, bar]), inc, pa)
        rgb = colors(rng, COLOR_IRREGULAR, n)

    elif kind == "spiral":
        _, scale, max_r, thick, n_arms, pitch, inc, pa = params
        n_arm = int(n * 0.65)
        n_disk = n - n_arm
        r0 = scale * 0.5
        r_arm = sample_radius(rng, n_arm, scale * 1.3, r0, max_r)
        arm_index = rng.integers(0, n_arms, n_arm)
        th_arm = (arm_index * (2.0 * np.pi / n_arms)
                  + np.log(r_arm / r0) / np.tan(np.radians(pitch))
                  + rng.normal(0.0, 0.2, n_arm))
        r_disk = sample_radius(rng, n_disk, scale, 0.0, max_r)
        th_disk = rng.uniform(0.0, 2.0 * np.pi, n_disk)
        r_all = np.concatenate([r_arm, r_disk])
        th_all = np.concatenate([th_arm, th_disk])
        y_all = rng.laplace(0.0, thick, n)
        local = orient(np.column_stack([r_all * np.cos(th_all), y_all, r_all * np.sin(th_all)]), inc, pa)
        rgb = np.concatenate([colors(rng, COLOR_ARM, n_arm), colors(rng, COLOR_DISK, n_disk)])
        # Dense old bulge in the middle
        n_bulge = int(n * 0.12)
        bulge = rng.normal(0.0, scale * 0.25, (n_bulge, 3))
        local = np.vstack([local[:n - n_bulge], bulge])
        rgb = np.vstack([rgb[:n - n_bulge], colors(rng, COLOR_BULGE, n_bulge)])
    else:
        raise ValueError(kind)

    abs_mag = rng.normal(10.0, 1.5, n) + dim
    return local + center, rgb, abs_mag


def random_field_galaxy_params(rng):
    """Random galaxy type, size and orientation -> (kind, params)."""
    kind_index = rng.choice(3, p=np.array(FIELD_TYPE_SHARES) / sum(FIELD_TYPE_SHARES))
    scale = float(np.clip(rng.lognormal(np.log(2500.0), 0.4), 800.0, 8000.0))  # pc
    n_min, n_max = FIELD_STARS_PER_GALAXY
    n = int(np.clip(n_min + (n_max - n_min) * (scale - 800.0) / 5200.0, n_min, n_max))
    inc = float(np.degrees(np.arccos(rng.uniform(0.0, 1.0))))   # random viewing angle
    pa = float(rng.uniform(0.0, 180.0))

    if kind_index == 0:      # spiral
        n_arms = 2 if rng.random() < 0.7 else 4
        pitch = float(rng.uniform(10.0, 25.0))
        return "spiral", (n, scale, scale * 6.0, scale * 0.12, n_arms, pitch, inc, pa)
    if kind_index == 1:      # elliptical: triaxial blob
        flat_b, flat_c = rng.uniform(0.6, 1.0), rng.uniform(0.5, 1.0)
        return "dwarf", (n, scale * 1.2, scale * 1.2 * flat_b, scale * 1.2 * flat_c, inc, pa)
    bar = float(scale * rng.uniform(0.0, 0.8))   # irregular, sometimes with a bar
    return "irregular", (n, scale * 0.8, scale * 5.0, scale * 0.25, bar, inc, pa)


def make_field_galaxies(rng):
    """Hundreds of galaxies at believable distances, partly in known groups.

    Returns a list of (positions, rgb, abs_mag).
    """
    sun = np.array([SUN_X, SUN_Z_UP, 0.0])
    weights = np.array([g[5] for g in FIELD_GROUPS])
    weights = weights / weights.sum()
    result = []

    for _ in range(N_FIELD_GALAXIES):
        while True:
            if rng.random() < FIELD_CLUSTERED_FRACTION:
                _, l, b, d, spread, _ = FIELD_GROUPS[rng.choice(len(FIELD_GROUPS), p=weights)]
                center = sun_frame_to_scene(l, b, d * 1000.0) + rng.normal(0.0, spread * 1.0e6, 3)
            else:
                # Uniform in volume between the min and max distance.
                d_mpc = (rng.uniform(FIELD_MIN_MPC ** 3, FIELD_MAX_MPC ** 3)) ** (1.0 / 3.0)
                direction = rng.normal(size=3)
                direction /= np.linalg.norm(direction)
                center = sun + direction * d_mpc * 1.0e6
            dist_mpc = np.linalg.norm(center - sun) / 1.0e6
            if FIELD_MIN_MPC * 0.8 <= dist_mpc <= FIELD_MAX_MPC * 1.1:
                break

        kind, params = random_field_galaxy_params(rng)
        n = params[0]
        # Far galaxies are fainter; more stars squeezed into one spot need more dimming.
        dim = (FIELD_BASE_DIM
               + 2.5 * np.log10(n / 5000.0)
               + FIELD_DISTANCE_DIM * np.log10(max(dist_mpc, 0.1) / 5.0))
        result.append(make_galaxy(rng, center, kind, params, dim))
    return result


def main():
    rng = np.random.default_rng(SEED)

    parts = [make_milky_way(rng)]

    # Named neighbors at their real positions.
    for name, l, b, d, kind, params in NEIGHBORS:
        center = sun_frame_to_scene(l, b, d)
        parts.append(make_galaxy(rng, center, kind, params, NEIGHBOR_DIM_MAG))
        print(f"{name:18s} {params[0]:>8d} stars  distance {d:.0f} kpc")

    # Hundreds of procedural field galaxies.
    field = make_field_galaxies(rng)
    parts.extend(field)
    n_field_stars = sum(len(p[0]) for p in field)
    print(f"\nfield galaxies: {len(field)} ({n_field_stars} stars)")

    pos = np.vstack([p[0] for p in parts])
    rgb = np.vstack([p[1] for p in parts])
    abs_mag = np.concatenate([p[2] for p in parts])

    stars = np.column_stack([pos, rgb, abs_mag]).astype(np.float32)
    stars.tofile(OUTPUT_PATH)

    radius = np.hypot(pos[:, 0], pos[:, 2])
    print(f"stars written : {len(stars)}")
    print(f"max distance from center : {np.linalg.norm(pos, axis=1).max() / 1.0e6:.1f} Mpc")
    print(f"radius pct    : 50%={np.percentile(radius, 50):.0f}  "
          f"90%={np.percentile(radius, 90):.0f}  99%={np.percentile(radius, 99):.0f} pc")
    print(f"file size     : {stars.nbytes / 1e6:.0f} MB")


if __name__ == "__main__":
    main()