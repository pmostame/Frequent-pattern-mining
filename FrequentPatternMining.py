# ------------------------------------------------------------------------------------------------------ initialize
import csv
support_min = 1264


# ------------------------------------------------------------------------------------------------------ define functions
def load_data():
    df = []
    with open('purchase_hisotry.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            df.append( set(row) )
    return df


def extract_len1_elements(df):
    """ loads the data as a list of sets each containing the items 
    """
    l1_elements = set()
    # extract a set of all len-1 elements
    for transaction in df:
        l1_elements = l1_elements | set(transaction)
    # reformat output to list of sets
    output = [set( [item] ) for item in l1_elements]
    return output


def extract_frequents(dataset, itemset_list, s_min = None): 
    """ dataset is a list of sets. 
    # itemset is a list of sets.
    """
    # set min support
    if s_min == None:
        s_min = round(0.5 * len(dataset))
    # initialize output
    results = {'itemset': itemset_list, 'is_frequent': [False] * len(itemset_list), 'support': [0] * len(itemset_list)}
    # iterate over items
    for ind, itemset in enumerate(itemset_list):
        for transaction in dataset:
            contains = 1
            for item in itemset:
                if (item not in transaction):
                    contains = 0
                    break
            results['support'][ind] = results['support'][ind] + contains
        results['is_frequent'][ind] = (results['support'][ind] >= s_min)
    results = drop_nonfrequents(results)
    return results


def create_candidates(itemset_list, item_dict):
    """ input is a list of len-K sets coming from extract_frequents['itemset']
    # item_dict is used to keep items of an itemset ordered.
    # output is a list of sets with k+1 length
    """
    K = len(itemset_list[0])
    new_itemset_list = []
    for ind1, itemset1 in enumerate(itemset_list):
        itemset1 = convert_to_ordered_lists(itemset1, item_dict)
        for ind2, itemset2 in enumerate(itemset_list):
            itemset2 = convert_to_ordered_lists(itemset2, item_dict)
            if ind1 < ind2:
                # self-join
                if can_self_join(itemset1, itemset2) or (K < 2):
                    new_itemset = convert_to_ordered_lists( set( itemset1 + itemset2 ), item_dict)
                    # pruning
                    if is_in_F(new_itemset, itemset_list) or (K < 2):
                        new_itemset_list.append( set(new_itemset) )
    return new_itemset_list



def drop_nonfrequents(results):
    """ Drops items with frequency less than min_support"""
    for key in results.keys():
        results[key] = [ results[key][ind] for ind in range(len(results['is_frequent'])) if results['is_frequent'][ind] ]
    return results


def can_self_join(itemset1, itemset2):
    """ checks whether two itemsets are appropriate to join for candidate generation"""
    join_flag = 1  
    # check if you can merge the two items
    for item_ind in range(len(itemset1)-1):
        if (itemset1[item_ind] != itemset2[item_ind]):
            join_flag = 0
            break
    return join_flag


def is_in_F(new_itemset, itemset_list): 
    """ for pruning in A-priori algorithm
    # c is a list
    # itemset is a list of sets
    """
    is_in = 0
    K = len(itemset_list[0])
    new_itemset_dummy = set(new_itemset[-K:])
    for itemset in itemset_list:
        if new_itemset_dummy == itemset:
            is_in = 1
            break
    return is_in


def convert_to_ordered_lists(itemset, item_dict):
    """ sorts the items within an itemset given the order in item_dict"""
    itemset_ordered = []
    itemset = list( itemset )
    for ind in item_dict['item_codes']:
        item = item_dict['item_labels'][ind]
        if item in itemset:
            itemset_ordered.append( item )
            itemset.pop( itemset.index(item) )
    return itemset_ordered


def extract_item_dict(df):
    """ creates a global dictionary of all 1-length items to use for sorting the itemsets."""
    item_labels_list = []
    for transaction in df:
        for item in transaction:
            item_labels_list.append( item )
    item_labels = [item for item in set( item_labels_list )]
    item_codes = [ind for ind in range(len(item_labels))]
    item_dict = {'item_codes': item_codes, 'item_labels': item_labels}
    return item_dict

    



# ------------------------------------------------------------------------------------------------------ Run the algorithm
df = load_data()
item_dict = extract_item_dict(df)

F_all_length = []

# extract len-1 frequent items 
itemset = extract_len1_elements(df)
F = extract_frequents(df, itemset, s_min=support_min)

# repeat until no more frequent items are found
while len(F['itemset']):
    # assign frequent patterns to output
    F_all_length.extend( F['itemset'] )

    # create candidates from previous frequent patterns
    C = create_candidates(F['itemset'], item_dict)

    # create new frequebt pattern for next iteration
    F = extract_frequents(df, C, s_min=support_min)

# print the results
print(F_all_length)
