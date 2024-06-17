from utils.words import read_and_process_file
import concurrent.futures

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def filter_words_by_length(word, word_list, max_distance=2):
    len_word = len(word)
    return [w for w in word_list if abs(len(w) - len_word) <= max_distance]

def distance_calculation(word, w):
    return (w, levenshtein_distance(word, w))

def find_closest_word(word, word_list, max_distance=2, batch_size=1000):
    all_words = read_and_process_file()
    all_words = all_words + word_list
    filtered_words = filter_words_by_length(word, all_words, max_distance)

    closest_word = None
    min_distance = max_distance + 1

    batches = [filtered_words[i:i+batch_size] for i in range(0, len(filtered_words), batch_size)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for batch in batches:
            results = list(executor.map(lambda w: distance_calculation(word, w), batch))
            for w, distance in results:
                if distance == 0:  # Se a distância for zero, as palavras são idênticas
                    return w
                elif distance < min_distance:
                    min_distance = distance
                    closest_word = w
    
    return closest_word if min_distance <= max_distance else word