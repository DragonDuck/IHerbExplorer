import DatabaseAPI
# pip install python-Levenshtein
from Levenshtein.StringMatcher import StringMatcher


def calc_string_similarity(string1, string2):
    """
    Computes the similarity between two strings. This is a separate function to allow for easy replacement of the
    similarity metric.

    The current implementation uses the Levenshtein distance as a ratio of the total word length
    :param string1:
    :param string2:
    :return:
    """
    return StringMatcher(seq1=string1, seq2=string2).ratio()


def search_similar(query, items, return_threshold=0):
    """
    This function searches for products based on a search query. The search performs string matching to identify the
    most likely matches. Optionally, a category can be given to limit searches.

    To determine the similarity of a search query with the items in the database, this function calculates the
    similarity of the search query to all substrings of the item names/descriptions of the same length. The greatest
    similarity is set as the "score" of that item. If the query consists of multiple words separated by a space then
    each of the words is treated independently and the net similarity score is the weighted (by character count)
    mean for each word.

    The function returns only those items with a similarity greater than or equal to 'return_threshold'. By default,
    all items will be returned but sorted by relevance.

    The function ignores upper- and lower case differences.

    :param query: A search string to compare to item names.
    :param items: Items to search through
    :param return_threshold: An integer indicating the threshold of item similarities to return
    :return:
    """

    query = query.lower()

    if items is None:
        items = DatabaseAPI.get_items()

    item_similarities = []
    for index, item in items.iterrows():

        item_name = item.loc["name"].lower()

        word_similarities = []
        for query_word in query.split():
            max_word_similarity = 0
            for ii in range(len(item_name) - len(query_word) + 1):
                substr = item_name[ii:ii+len(query_word)]
                sim = calc_string_similarity(query_word, substr)
                if sim > max_word_similarity:
                    max_word_similarity = sim
                # This speeds things up a bit as the largest similarity for a single word is 1
                if max_word_similarity == 1:
                    break
            word_similarities.append((max_word_similarity, len(query_word)))

        total_len = sum([entry[1] for entry in word_similarities])
        max_similarity = sum([entry[0] * entry[1] / total_len for entry in word_similarities])
        item_similarities.append(max_similarity)

    items["similarity_to_query"] = item_similarities
    items = items.sort_values("similarity_to_query", ascending=False)
    items = items.loc[items["similarity_to_query"] >= return_threshold]

    return items
