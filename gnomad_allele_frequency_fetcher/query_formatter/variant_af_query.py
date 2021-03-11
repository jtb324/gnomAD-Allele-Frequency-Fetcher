import logging


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

    logger.info(
        f"searching for variant, {variant_id}, in the dataset for the build corresponding to: {dataset_str}"
    )
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
