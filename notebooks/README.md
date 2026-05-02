# Colab Enterprise notebooks

Analyst workspace for ad-hoc exploration. Notebooks here run in Colab Enterprise with the `analyst-sa@` service account, scoped to read-only access on `atlasmind_warehouse`.

Conventions:

- Filename: `<area>_<topic>.ipynb` (e.g. `africa_urban_growth.ipynb`).
- First cell sets `PROJECT_ID` and prints the connected env.
- Save outputs as Sheets/Docs in the analyst's Drive — never to BigQuery from here.
- Anything that becomes recurring should graduate into `data/ingestion/` or a Looker Studio report.
