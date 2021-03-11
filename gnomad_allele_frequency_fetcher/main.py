import requests
import argparse
import pandas as pd
import os
import time
import logging
import sys

from json_fetcher.fetcher import fetch
from loggers.log_formatter import create_logger
from query_formatter.variant_af_query import get_query
from analysis_functions.allele_frequency_analysis import analysis, get_variant_freq
from writer_functions.allele_frequency_writers import write_freq_to_file


def variant_getter(var_file: str) -> list:

    var_df: pd.DataFrame = pd.read_excel(var_file)

    snp_list: list = var_df["SNP"].values.tolist()

    return snp_list


def run(args):
    """function that will run and get request from the gnomad website with"""
    logger: object = create_logger(__name__, args.output)

    # removing any previous output file
    if os.path.exists(os.path.join(args.output, "variant_gnomAD_frequencies.txt")):

        os.remove(os.path.join(args.output, "variant_gnomAD_frequencies.txt"))

    # getting a list of snps of interest
    snp_list: list = variant_getter(args.var_file)

    logger.info(f"generating a list of snps from the file: {args.var_file}")

    # asking the user if they want to use the build based on
    # GRch37 or GRCh38
    try:
        dataset_choice: int = int(
            input(
                "which data set would you like to use. (1 for gnomad_r2_1, 2 for gnomad_r3): "
            )
        )
    except ValueError:
        print("Value was not a valid integer. Program terminating...")
        logger.error("user input was not a valid integer")
        sys.exit(1)

    logger.info(f"Searching for frequencies in the {args.pop_code} population")
    # creating a counter so that I can pause the code every 10
    # requestand not overwhelm the api
    count = 0
    print("attempt to search for the variants in the gnomAD api")
    # iterating through each variant in the list
    for variant in snp_list:
        # getting the query string for the exome frequencies
        query_list: dict = get_query(variant, "exome", dataset_choice)
        # attempting to fetch a response. Response with -1 if the
        # variant is not found
        response = fetch(query_list)
        # This filter will either be exome or genome
        filter_value: None = None
        if response == -1:
            logger.warning(f"Variant not found: {variant}")

            write_freq_to_file(args.output, variant, "N/A", "N/A", "N/A")

            continue

        elif not response["data"]["variant"]["exome"] == None:

            response_subset = response["data"]["variant"]["exome"]["populations"]

            filter_value: str = "exome"

        # If the response from the exome data equals none then attempt to get the data for the genome filter
        else:
            genome_query_list = get_query(variant, "genome", dataset_choice)

            response = fetch(genome_query_list)

            # if there is response for the genome data then log this to a file and move on to the next variant
            if response["data"]["variant"]["genome"] == "None":

                print(
                    "There was no response for either the exome data or the genome data. Continuing to next variant..."
                )

                logger.error(
                    f"no api response for either the exome or the genome data for the variant: {variant}"
                )
                continue

            # subsetting the response just into the population data
            response_subset: list = response["data"]["variant"]["genome"]["populations"]

            # updating the filter value
            filter_value: str = "genome"

        # getting the count of the variant alleles and the total allele counts
        analysis(response_subset, args.pop_code, args.output, variant, filter_value)

        # updating the counter
        count += 1
        # pausing the program for 1 second after every ten api responses
        if count % 10 == 0:
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(
        description="cli to query the gnomAD api for specified SNPs"
    )

    parser.add_argument(
        "--var_input",
        help="This argument takes the initial input file which contains variants for multiple chromosomes and splits it into multiple files, one for each chromosome",
        dest="var_file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--output",
        help="This argument list the output directory for the file",
        dest="output",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--pop_code",
        help="This argument list population to get the frequencies for",
        dest="pop_code",
        type=str,
        required=True,
    )

    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
