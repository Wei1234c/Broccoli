from tasks import *
from canvas import *


def getWordsFromText(file = 'test.txt'):
    with open(file) as f:
        lines = f.readlines()        
    return ' '.join(lines).replace(',', '').replace('.', '').split()


def reduce(word_counts):    
    wordCounts = {}
    
    for word_count in word_counts:
        if word_count is not None: 
            wordCounts[word_count[0]] = wordCounts.get(word_count[0], 0) + word_count[1]
        
    result = sorted(list(wordCounts.items()), 
                    key = lambda x: (x[1], x[0]), 
                    reverse = True)    
    return result


def count_words(file = 'test.txt'):

    words = getWordsFromText(file)

    try:
        # 發送給 Broccoli 執行
        # async_results = [mapper.s(word=word).delay() for word in words]  # mapper 是定義在 tasks.py 中
        # results = [async_result.get() for async_result in async_results]
        # return len(words), reduce(results)
        # return len(words), reduce(ResultSet(async_results).get())

        gp = group([mapper.s(word) for word in words])
        return len(words), reduce(gp.get())

    except Exception as e:
        print(e)



# if len(word) > 0
# ********** result:
# words count: 2190
#
# [('the', 120), ('and', 90), ('a', 72), ('to', 55), ('his', 44), ('The', 42), ('of', 39), ('in', 37), ('you', 32), ('he', 32)]
# **********


# # if len(word) > 3
# ********** result:
# words count: 2190
#
# [('that', 19), ('with', 14), ('have', 14), ('your', 13), ('would', 12), ('said', 12), ('them', 10), ('from', 10), ('which', 8), ('their', 8)]
# **********
