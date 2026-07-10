from jellyfish import levenshtein_distance

def find_nearest_sentence(txt):
    lst = ['i am using','i have','can you tell me','recommend me','suggest me','can i use']
    min_similarity = 999999
    word = ""
    for i in lst:
        similarity_score = levenshtein_distance(i,txt)
        if(similarity_score <= min_similarity):
            min_similarity = similarity_score
            word = i   
    return word 

