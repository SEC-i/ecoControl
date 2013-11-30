# returns dictionary[a].values()[2][c] if path="a/{2}/c"
def extract_data(dictionary, path):
    for item in path.split("/"):
        try:
            if item[:1]=="{" and item[-1:]=="}":
                dictionary = dictionary.values()[int(item[1:-1])]
            else:
                dictionary = dictionary[item]
        except:
            return ""
    return dictionary