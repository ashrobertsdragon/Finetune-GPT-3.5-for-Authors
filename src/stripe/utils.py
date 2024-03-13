import json

def get_id(file_path, num_credits):
    """
    Extracts the SKU value from a JSON file based on the num_credits key.

    Parameters:
    - file_path: The path to the JSON file.
    - num_credits: The key to look for in the 'stripeIDs' dictionary.

    Returns:
    - The SKU value associated with the given num_credits key.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    price_id = data.get('stripeIDs', {}).get(num_credits)
    
    return price_id

