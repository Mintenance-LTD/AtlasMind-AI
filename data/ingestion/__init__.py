"""Ingestion jobs land raw payloads in gs://atlasmind-raw/, then MERGE into
atlasmind_warehouse.* via BigQuery. Each loader writes one ingest_runs row.
"""
