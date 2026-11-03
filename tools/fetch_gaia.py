from astroquery.gaia import Gaia

query = """
SELECT source_id, ra, dec, parallax, parallax_over_error,
       phot_g_mean_mag, bp_rp
FROM gaiadr3.gaia_source
WHERE random_index < 5000000    
    AND parallax_over_error > 5
    AND bp_rp IS NOT NULL
    ORDER BY random_index
"""
Gaia.ROW_LIMIT = -1
Gaia.login()
job = Gaia.launch_job_async(query)
table = job.get_results()
print(len(table))
print("ra :", table["ra"].min(), table["ra"].max())
print("dec:", table["dec"].min(), table["dec"].max())
table.write("data/gaia_raw.fits", overwrite=True)