import os


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
