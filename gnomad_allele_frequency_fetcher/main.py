import requests
import argparse
import pandas as pd
import os
import time
import logging
from loggers.log_formatter import create_logger
import sys


def variant_getter(var_file: str) -> list:

    var_df: pd.DataFrame = pd.read_excel(var_file)

    snp_list: list = var_df["SNP"].values.tolist()

    return snp_list


def fetch(jsondata):
    """function to fetch a json response from graphql
    Parameters
    __________
    jsondata
        dictionary contain the query parameters

    Returns
    _______
    json
        returns a json object containing the query parameters
    int
        if the program encounters an error then it will return -1
    """
    gnomad_website: str = "https://gnomad.broadinstitute.org/api"
    headers: dict = {"Content-Type": "application/json"}
    response = requests.post(gnomad_website, json=jsondata, headers=headers)
    json = response.json()
    if "errors" in json:

        # raise Exception(str(json["errors"]))
        return -1
    return json


def get_query(variant_id: str, genome: str, dataset_choice) -> dict:
    """Function to get the query string that will be passed to the graphQL api
    Parameters
    __________
    variant_id : str
        string that contains the SNP as it is on the MEGA array 

    Returns
    _______
    dict
        returns a dictionary that contains the query parameters
    """
    # getting the logger object
    logger = logging.getLogger(__name__)

    dataset_dict: dict = {1: "gnomad_r2_1", 2: "gnomad_r3_1"}

    dataset_str: str = dataset_dict[dataset_choice]

    logger.info(f"using the build corresponding to: {dataset_str}")
    fmt_graphql = """
    {
        variant(variantId: "%s", dataset: %s) {
            variantId: variantId
            rsid
            chrom
            alt
            ref
		    %s {
            populations{
                id
      	        ac
                an
                homozygote_count
                hemizygote_count
            }
			af 
            ac
            an
        }
    }
    }
    """
    req_variant_dict: dict = {
        "query": fmt_graphql % (variant_id, dataset_str, genome),
        "variables": {"withFriends": False},
    }

    return req_variant_dict


def get_allele_counts(response_subset: list, pop_code: str) -> tuple:
    """function to get the allele count and the total allele count for the specified subpopulation
    Parameters
    __________
    response_subset : list
        list of dictionaries that contain information about the allele counts for each population in gnomAD
    pop_code: str
        The population code that the user wants to find the frequency for
    """
    for response in response_subset:
        if response["id"] == pop_code:
            var_allele_count: int = int(response["ac"])
            total_allele_count: int = int(response["an"])
            return (var_allele_count, total_allele_count)
    return (0, 0)


def get_variant_freq(var_allele_count: int, total_allele_count: int) -> float:
    """function to get the allele frequency for the population
    Parameters
    __________
    var_allele_count : int
        allele count for the specific variant as reported in gnomAD 
    total_allele_count : int
        total allele count as report by gnomAD for the specified variant
    
    Returns
    _______
    float
        returns the variant allele frequency
    """
    return round(var_allele_count / total_allele_count, 6)


def write_freq_to_file(
    output_path: str,
    variant: str,
    allele_freq: float,
    filter_str: str,
    population_code: str,
):
    """function to write the variants allele frequency to a file\
    Parameters
    __________
    output_path : str
        string listing the output path
    variant : str
        SNP id
    allele_freq : float
        The allele frequency for the specified variant in the specified population
    filter : str
        This will be either exome or genome 
    population_code : str 
        this is the population of interest   
    """
    # writing the variants and their frequency to a file
    with open(
        os.path.join(output_path, "variant_gnomAD_frequencies.txt"), "a+"
    ) as output_file:
        # adding a header to the file if it is empty
        if (
            os.path.getsize(os.path.join(output_path, "variant_gnomAD_frequencies.txt"))
            == 0
        ):
            output_file.write(
                f"variant\tfilter\tpopulation\tvariant_allele_frequency\n"
            )

        output_file.write(
            f"{variant}\t{filter_str}\t{population_code}\t{allele_freq}\n"
        )


def run(args):
    """function that will run and get request from the gnomad website with"""
    print(__name__)
    logger: object = create_logger(__name__, args.output)

    # removing any previous output file
    if os.path.exists(os.path.join(args.output, "variant_gnomAD_frequencies.txt")):

        os.remove(os.path.join(args.output, "variant_gnomAD_frequencies.txt"))

    # getting a list of snps of interest
    snp_list: list = variant_getter(args.var_file)

    logger.info(f"generating a list of snps from the file: {args.var_file}")

    # asking the user if they want to use the build based on
    # GRch37 or GRCh38
    dataset_choice: int = int(
        input("which data set would you like to use. (1:gnomad_r2_1, 2:gnomad_r3): ")
    )

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

        # getting
        allele_tuple: tuple = get_allele_counts(response_subset, args.pop_code)

        if allele_tuple[0] == 0 and allele_tuple[1] == 0:
            logger.warning(
                f"no allele counts found for the {args.pop_code} population for the variant, {variant}"
            )

            write_freq_to_file(args.output, variant, "N/A", filter_value, "N/A")

            continue

        else:
            var_allele_freq: float = get_variant_freq(allele_tuple[0], allele_tuple[1])

            write_freq_to_file(
                args.output, variant, var_allele_freq, filter_value, args.pop_code
            )

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
