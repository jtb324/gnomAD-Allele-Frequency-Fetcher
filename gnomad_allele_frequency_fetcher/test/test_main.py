# test_main.py
import pandas as pd
import collections

import logging
import sys

sys.path.append("../")

import main
from analysis_functions.allele_frequency_analysis import get_allele_counts


print(sys.path)
print("running unit test")

# setting a global variable that can be used through the test
# This variable is a dataframe of the initial snp list
# also has columns for other test output values
variant_file: str = "./data/variant_test_freq.xlsx"
snp_df: pd.DataFrame = pd.read_excel(variant_file)

expected_snp_list: list = snp_df.SNP.values.tolist()

response: list = [{"id": "NFE", "ac": 4, "an": 12}, {"id": "AFR", "ac": 12, "an": 25}]
pop_code: str = "NFE"


def test_check_variants_len():
    """Unit test to check if the outputted variant list is the same length as the len of the expected snp list"""
    program_snp_list: list = main.variant_getter(variant_file)
    assert len(program_snp_list) == len(expected_snp_list)


def test_check_variants_lists():
    """Unit test to check if the same values are in the outputted snp list and the expected snp list"""
    program_snp_list: list = main.variant_getter(variant_file)

    assert collections.Counter(program_snp_list) == collections.Counter(
        expected_snp_list
    )


def test_check_query_size():
    """function to make sure the query size is 2"""
    logger = logging.getLogger(__name__)
    query_dict: dict = main.get_query(expected_snp_list[0], "exome", 1)

    assert len(query_dict) == 2


def test_check_allele_counts():
    """function to check that the allele counts are not the correct number"""
    allele_count_tuple: tuple = get_allele_counts(response, pop_code)

    assert allele_count_tuple[0] == 4 and allele_count_tuple[1] == 12

