def word_compare(str1, str2):
    lens = [len(str1), len(str2)]
    diff = max(lens) - min(lens)
    for index in range(min(lens)):
        if not str1[index].lower() == str2[index].lower():
            diff += 1
    return diff


def compare(str1, str2):
    words1 = str1.strip().split(' ')
    words2 = str2.strip().split(' ')
    lens = [len(words1), len(words2)]
    diff = sum([len(word) for word in words2[min(lens):] + words1[min(lens):]])
    for index in range(max(lens)):
        word1 = words1[index] if len(words1) > index else ''
        word2 = words2[index] if len(words2) > index else ''
        diff += word_compare(word1, word2)
    return 100 - diff * (100 / max([len(str1), len(str2)]))