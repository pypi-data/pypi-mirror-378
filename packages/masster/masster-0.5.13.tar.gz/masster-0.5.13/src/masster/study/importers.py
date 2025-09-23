"""
import.py

Module providing import functionality for Study class, specifically for importing
oracle identification data into consensus features.
"""

from __future__ import annotations

import os
import pandas as pd
import polars as pl


def import_oracle(
    self,
    folder,
    min_id_level=None,
    max_id_level=None,
):
    """
    Import oracle identification data and map it to consensus features.
    
    This method reads oracle identification results from folder/diag/summary_by_feature.csv
    and maps them to consensus features using the 'uit' (feature_uid) column. The oracle
    data is used to populate identification columns in consensus_df.
    
    Parameters:
        folder (str): Path to oracle folder containing diag/summary_by_feature.csv
        min_id_level (int, optional): Minimum identification level to include
        max_id_level (int, optional): Maximum identification level to include
        
    Returns:
        None: Updates consensus_df in-place with oracle identification data
        
    Raises:
        FileNotFoundError: If the oracle summary file doesn't exist
        ValueError: If consensus_df is empty or doesn't have required columns
        
    Example:
        >>> study.import_oracle(
        ...     folder="path/to/oracle_results",
        ...     min_id_level=2,
        ...     max_id_level=4
        ... )
    """
    
    self.logger.info(f"Starting oracle import from folder: {folder}")
    
    # Validate inputs
    if self.consensus_df is None or self.consensus_df.is_empty():
        raise ValueError("consensus_df is empty or not available. Run merge() first.")
    
    if "consensus_uid" not in self.consensus_df.columns:
        raise ValueError("consensus_df must contain 'consensus_uid' column")
    
    # Check if oracle file exists
    oracle_file_path = os.path.join(folder, "diag", "summary_by_feature.csv")
    if not os.path.exists(oracle_file_path):
        raise FileNotFoundError(f"Oracle summary file not found: {oracle_file_path}")
    
    self.logger.debug(f"Loading oracle data from: {oracle_file_path}")
    
    try:
        # Read oracle data using pandas first for easier processing
        oracle_data = pd.read_csv(oracle_file_path)
        self.logger.info(f"Oracle data loaded successfully with {len(oracle_data)} rows")
    except Exception as e:
        self.logger.error(f"Could not read {oracle_file_path}: {e}")
        raise
    
    # Select relevant columns from oracle data
    required_oracle_cols = ["title", "id_level", "id_label", "id_ion", "id_class", "score"]
    missing_cols = [col for col in required_oracle_cols if col not in oracle_data.columns]
    if missing_cols:
        raise ValueError(f"Oracle data missing required columns: {missing_cols}")
    
    oracle_subset = oracle_data[required_oracle_cols].copy()
    
    # Extract consensus_uid from title column (format: "uid:XYZ, ...")
    self.logger.debug("Extracting consensus UIDs from oracle titles using pattern 'uid:(\\d+)'")
    oracle_subset["consensus_uid"] = oracle_subset["title"].str.extract(r"uid:(\d+)")
    
    # Remove rows where consensus_uid extraction failed
    oracle_subset = oracle_subset.dropna(subset=["consensus_uid"])
    oracle_subset["consensus_uid"] = oracle_subset["consensus_uid"].astype(int)
    
    self.logger.debug(f"Extracted consensus UIDs for {len(oracle_subset)} oracle entries")
    
    # Apply id_level filters if specified
    initial_count = len(oracle_subset)
    if min_id_level is not None:
        oracle_subset = oracle_subset[oracle_subset["id_level"] >= min_id_level]
        self.logger.debug(f"After min_id_level filter ({min_id_level}): {len(oracle_subset)} entries")
    
    if max_id_level is not None:
        oracle_subset = oracle_subset[oracle_subset["id_level"] <= max_id_level]
        self.logger.debug(f"After max_id_level filter ({max_id_level}): {len(oracle_subset)} entries")
    
    if len(oracle_subset) == 0:
        self.logger.warning("No oracle entries remain after filtering")
        return
    
    # Sort by id_level (descending) to prioritize higher confidence identifications
    # and remove duplicates by consensus_uid, keeping the first (highest id_level)
    oracle_subset = oracle_subset.sort_values(by=["id_level"], ascending=False)
    oracle_subset = oracle_subset.drop_duplicates(subset=["consensus_uid"], keep="first")
    
    self.logger.debug(f"After deduplication by consensus_uid: {len(oracle_subset)} unique identifications")
    
    # Convert to polars for efficient joining
    oracle_pl = pl.DataFrame(oracle_subset)
    
    self.logger.debug(f"Oracle data ready for consensus mapping: {len(oracle_pl)} entries")
    
    if oracle_pl.is_empty():
        self.logger.warning("No oracle entries could be processed")
        return
    
    # Group by consensus_uid and select the best identification (highest id_level)
    # In case of ties, take the first one
    best_ids = (
        oracle_pl
        .group_by("consensus_uid")
        .agg([
            pl.col("id_level").max().alias("max_id_level")
        ])
        .join(oracle_pl, on="consensus_uid")
        .filter(pl.col("id_level") == pl.col("max_id_level"))
        .group_by("consensus_uid")
        .first()  # In case of ties, take the first
    )
    
    self.logger.debug(f"Selected best identifications for {len(best_ids)} consensus features")
    
    # Prepare the identification columns
    id_columns = {
        "id_top_name": best_ids.select("consensus_uid", "id_label"),
        "id_top_adduct": best_ids.select("consensus_uid", "id_ion"), 
        "id_top_class": best_ids.select("consensus_uid", "id_class"),
        "id_top_score": best_ids.select("consensus_uid", pl.col("score").round(3).alias("score")),
        "id_source": best_ids.select(
            "consensus_uid", 
            pl.when(pl.col("id_level") == 1)
            .then(pl.lit("lipidoracle ms1"))
            .otherwise(pl.lit("lipidoracle ms2"))
            .alias("id_source")
        )
    }
    
    # Initialize identification columns in consensus_df if they don't exist
    for col_name in id_columns.keys():
        if col_name not in self.consensus_df.columns:
            if col_name == "id_top_score":
                self.consensus_df = self.consensus_df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias(col_name)
                )
            else:
                self.consensus_df = self.consensus_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias(col_name)
                )
    
    # Update consensus_df with oracle identifications
    for col_name, id_data in id_columns.items():
        oracle_column = id_data.columns[1]  # second column (after consensus_uid)
        
        # Create update dataframe
        update_data = id_data.rename({oracle_column: col_name})
        
        # Join and update
        self.consensus_df = (
            self.consensus_df
            .join(update_data, on="consensus_uid", how="left", suffix="_oracle")
            .with_columns(
                pl.coalesce([f"{col_name}_oracle", col_name]).alias(col_name)
            )
            .drop(f"{col_name}_oracle")
        )
    
    # Replace NaN values with None in identification columns
    id_col_names = ["id_top_name", "id_top_adduct", "id_top_class", "id_top_score", "id_source"]
    for col_name in id_col_names:
        if col_name in self.consensus_df.columns:
            # For string columns, replace empty strings and "nan" with None
            if col_name != "id_top_score":
                self.consensus_df = self.consensus_df.with_columns(
                    pl.when(
                        pl.col(col_name).is_null() | 
                        (pl.col(col_name) == "") |
                        (pl.col(col_name) == "nan") |
                        (pl.col(col_name) == "NaN")
                    )
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name)
                )
            # For numeric columns, replace NaN with None
            else:
                self.consensus_df = self.consensus_df.with_columns(
                    pl.when(pl.col(col_name).is_null() | pl.col(col_name).is_nan())
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name)
                )
    
    # Count how many consensus features were updated
    updated_count = self.consensus_df.filter(pl.col("id_top_name").is_not_null()).height
    total_consensus = len(self.consensus_df)
    
    self.logger.info(
        f"Oracle import complete: {updated_count}/{total_consensus} "
        f"consensus features now have identifications ({updated_count/total_consensus*100:.1f}%)"
    )
    
    # Update history
    self.update_history(["import_oracle"], {
        "folder": folder,
        "min_id_level": min_id_level,
        "max_id_level": max_id_level,
        "updated_features": updated_count,
        "total_features": total_consensus
    })