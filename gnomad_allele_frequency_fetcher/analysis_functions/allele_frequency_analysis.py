import logging
import sys

sys.path.append("../")

from writer_functions.allele_frequency_writers import write_freq_to_file


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


def analysis(
    response_subset: list,
    population_code: str,
    output: str,
    variant_id: str,
    filter_value: str,
):
    """function to analyze the response_subset to get the variant frequency
    Parameters
    __________
    response_subset: list
        list of dictionaries that contains information about the allele counts for
        specified variants in a specified population
    population_code : str 
        this is the population of interest
    output : str
        string listing the output path
    variant_id : str
        SNP id
    filter_value : str
        This will be either exome or genome     
    """

    logger = logging.getLogger(__name__)

    allele_tuple: tuple = get_allele_counts(response_subset, population_code)

    if allele_tuple[0] == 0 and allele_tuple[1] == 0:
        logger.warning(
            f"no allele counts found for the {population_code} population for the variant, {variant_id}"
        )

        write_freq_to_file(output, variant_id, "N/A", filter_value, "N/A")

    else:
        var_allele_freq: float = get_variant_freq(allele_tuple[0], allele_tuple[1])

        write_freq_to_file(
            output, variant_id, var_allele_freq, filter_value, population_code
        )
