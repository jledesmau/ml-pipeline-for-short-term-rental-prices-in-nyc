#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning,
exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info(f"Downloading input artifact {args.input_artifact}")
    local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)

    # Drop outliers
    logger.info(f"Keeping prices between {args.min_price} and {args.max_price}")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    logger.info("Converting 'last_review' column to datetime format")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Ensuring proper geolocation
    logger.info("Ensuring propoer geolocation")
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Save clean data
    logger.info("Saving clean data as 'clean_sample.csv'")
    df.to_csv("clean_sample.csv", index=False)

    # Uploading output artifact to W&B
    logger.info(f"Uploading output artifact to W&B as {args.output_artifact}")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Output artifact description",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum value for price column",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum value for price column",
        required=True
    )


    args = parser.parse_args()

    go(args)
