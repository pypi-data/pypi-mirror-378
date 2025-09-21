def extract_characters(s):
    """
    Extract alphanumeric characters from a string.

    This function takes a string and returns a Counter object 
    containing the count of each alphanumeric character in the string. 
    The string is converted to lowercase before counting.

    Args:
        s (str): The input string from which to extract characters.

    Returns:
        Counter: A Counter object with alphanumeric characters as keys 
                 and their counts as values.
    """
    from collections import Counter
    return Counter(filter(str.isalnum, s.lower()))

def character_match_score(user_input, feature_value):
    """
    Calculate the character match score between two strings.

    This function compares two strings by extracting alphanumeric 
    characters from each and computing a match score based on the 
    intersection of their character counts.

    Args:
        user_input (str): The user input string.
        feature_value (str): The string from the dataset to compare against.

    Returns:
        int: The match score indicating how many characters match 
             between the two strings.
    """
    user_chars = extract_characters(user_input)
    feature_chars = extract_characters(feature_value)
    
    match_score = sum((user_chars & feature_chars).values())  # intersection of counters
    return match_score

def find_closest_match(user_input, feature_values):
    """
    Find the closest matching value from a list of feature values.

    This function compares a user input string against a list of feature 
    values and finds the closest match based on the character match score.

    Args:
        user_input (str): The user input string to match.
        feature_values (list): A list of feature values to compare against.

    Returns:
        str: The feature value that has the highest match score.
    """
    match_scores = [(character_match_score(user_input, value), value) for value in feature_values]
    highest_score_value = max(match_scores, key=lambda x: x[0])[1]
    return highest_score_value

def find_matching(dataset, requirements):
    """
    Compare a dataset with specified requirements and add matching results.

    This function takes a dataset and a dictionary of requirements, then 
    creates a new DataFrame where each row is checked against the given 
    requirements. It adds new columns to the DataFrame indicating whether 
    each row matches the requirements.

    Args:
        dataset (pd.DataFrame): The original dataset to be checked.
        requirements (dict): A dictionary where keys are column names 
                             and values are the required values for matching.

    Returns:
        pd.DataFrame: A new DataFrame with additional columns showing 
                      the match results for each requirement.
    """
    results = dataset.copy()
    
    for spec, value in requirements.items():
        if value not in results[spec].values:
            closest_match = find_closest_match(value, results[spec].values.tolist())
            print(f"No exact match for {value} in {spec}. Closest match: {closest_match}")
            value = closest_match
        # Create a column indicating if the row matches the requirement
        results[f'Match_{spec}'] = results[spec] == value
    
    return results

def find_top_matching(dataset, requirements, top_n, g=None):
    """
    Find the top N matching rows based on specified requirements.

    This function identifies rows in the dataset that best match the 
    specified requirements. It ranks the rows based on a total match 
    score and returns the top N results. Optionally, it can return a 
    specific column along with the match score.

    Args:
        dataset (pd.DataFrame): The dataset containing data.
        requirements (dict): A dictionary where keys are column names and 
                             values are the required values for matching.
        top_n (int): The number of top matching rows to return.
        g (str, optional): A specific column to return along with the match score.

    Returns:
        pd.DataFrame: A DataFrame containing the top N matching rows. 
                      If g is provided, returns the g column along with the 
                      match score; otherwise, returns the entire matching 
                      rows dataset.
    """
    results = find_matching(dataset, requirements)
    
    # Calculate total match score for each row
    results['Total_Match_Score'] = results[[f'Match_{spec}' for spec in requirements.keys()]].sum(axis=1)
    
    # Sort the rows by total match score in descending order
    sorted_results = results.sort_values(by='Total_Match_Score', ascending=False)
    
    # Select the top N rows
    top_results = sorted_results.head(top_n)
    
    # If g is provided and is a valid column, return that column along with the Total_Match_Score
    if g and g in top_results.columns:
        return top_results[[g, 'Total_Match_Score']]
    
    # Otherwise, return the entire top matching rows dataset
    return top_results
