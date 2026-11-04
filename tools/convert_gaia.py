"""Convert the raw Gaia table into a flat binary file the renderer can load.

Input : data/gaia_raw.fits  (from tools/fetch_gaia.py)
Output: data/stars.bin      (float32, 7 values per star)

Layout of one star (28 bytes):
    x, y, z      position in parsecs, Sun at the origin (galactic frame)
    r, g, b      display color in 0..1
    abs_mag      absolute G magnitude (smaller = intrinsically brighter)
"""

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, Galactocentric
from astropy.table import Table

INPUT_PATH = "data/gaia_raw.fits"
OUTPUT_PATH = "data/stars.bin"

# Color ramp: (bp_rp value) -> (r, g, b). Small bp_rp = hot blue star,
# large bp_rp = cool red star. The Sun is around bp_rp = 0.82.
RAMP_BP_RP = np.array([-0.5, 0.3, 0.8, 1.5, 3.0])
RAMP_RGB = np.array([
    [0.60, 0.70, 1.00],  # blue
    [0.85, 0.90, 1.00],  # blue-white
    [1.00, 0.95, 0.80],  # yellow-white
    [1.00, 0.70, 0.40],  # orange
    [1.00, 0.40, 0.25],  # red
])


def bp_rp_to_rgb(bp_rp):
    """Map the BP-RP color index to RGB by interpolating the ramp above.

    np.interp clamps values outside the ramp to the end colors.
    """
    channels = [np.interp(bp_rp, RAMP_BP_RP, RAMP_RGB[:, c]) for c in range(3)]
    return np.column_stack(channels)


def main():
    table = Table.read(INPUT_PATH)

    # Pull the columns out as plain float64 numpy arrays.
    ra = np.asarray(table["ra"], dtype=np.float64)              # degrees
    dec = np.asarray(table["dec"], dtype=np.float64)            # degrees
    parallax = np.asarray(table["parallax"], dtype=np.float64)  # milliarcseconds
    g_mag = np.asarray(table["phot_g_mean_mag"], dtype=np.float64)
    bp_rp = np.asarray(table["bp_rp"], dtype=np.float64)

    # Distance in parsecs: d = 1000 / parallax(mas).
    # Safe here because the query kept only parallax_over_error > 5.
    distance_pc = 1000.0 / parallax

    # Sky position + distance -> a point in 3D space.
    # ICRS is the frame Gaia reports in; .galactic converts it to the
    # galactic frame (x toward the galactic center, z toward the north
    # galactic pole). .cartesian gives x, y, z instead of angles.
    coords = SkyCoord(ra=ra * u.deg, dec=dec * u.deg,distance=distance_pc * u.pc, frame="icrs")
    xyz = coords.galactic.cartesian
    
    # Galactocentric frame: origin at the galactic center, Sun about 8.1 kpc away.
    gc = coords.transform_to(Galactocentric())
    gx = gc.x.to_value(u.pc)
    gy = gc.y.to_value(u.pc)
    gz = gc.z.to_value(u.pc)

    # The renderer uses +Y as "up". Remap so galactic north is up and the disk
    # lies flat in the XZ plane:  (x, y, z) -> (x, z, -y)  (still right-handed).
    x = gx
    y = gz
    z = -gy

    # Absolute magnitude: how bright the star would look from 10 pc.
    # M = G + 5*log10(parallax_mas) - 10
    abs_mag = g_mag + 5.0 * np.log10(parallax) - 10.0

    rgb = bp_rp_to_rgb(bp_rp)

    # Pack everything into one (N, 7) float32 array and dump the raw bytes.
    stars = np.column_stack([x, y, z, rgb, abs_mag]).astype(np.float32)
    stars.tofile(OUTPUT_PATH)

    print(f"stars written : {len(stars)}")
    print(f"bytes per star: {stars.shape[1] * 4}")
    print(f"x range (pc)  : {x.min():.0f} .. {x.max():.0f}")
    print(f"y range (pc)  : {y.min():.0f} .. {y.max():.0f}")
    print(f"z range (pc)  : {z.min():.0f} .. {z.max():.0f}")
    print(f"max distance  : {distance_pc.max():.0f} pc")
    print(f"abs mag range : {abs_mag.min():.1f} .. {abs_mag.max():.1f}")


if __name__ == "__main__":
    main()