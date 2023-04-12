from elasticsearch import Elasticsearch

# _es = Elasticsearch([{'host': 'localhost', 'port': 9200}], http_auth=("elastic", 'ricotest'))
_es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
# analyzer = ['standard']
index_name = 'rico'

# check all characters ascii
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# check if all charactes are whitespace
def is_allwhite(s):
    return all(c==' ' for c in s)

# validity check with ascii and whitespace
def isInValid(text):
    if text=="" or is_allwhite(text):
        return True
    if is_ascii(text)==False:
        return True
    return False

# parse to find fields. Find all 9 possible combinations.
def parseSearchString(text):
    # lt/tl -> left-top, rt/tr -> right-top
    # lb/bl -> left-bottom , rb/bl -> right-bottom
    # l -> left-top and left- bottom
    # r -> right-top and right- bottom
    # t -> left-top and right-top
    # b -> left-bottom and right-bottom
    if "lt:" in text:
        index = text.index('lt:')
        text = text[index+3:]
        return ["lt"], text

    elif "tl:" in text:
        index = text.index('tl:')
        text = text[index+3:]
        return ["lt"], text

    elif "rt:" in text:
        index = text.index('rt:')
        text = text[index + 3:]
        return ["rt"], text

    elif "tr:" in text:
        index = text.index('tr:')
        text = text[index + 3:]
        return ["rt"], text

    elif "rb:" in text:
        index = text.index('rb:')
        text = text[index + 3:]
        return ["rb"], text

    elif "br:" in text:
        index = text.index('br:')
        text = text[index + 3:]
        return ["rb"], text

    elif "lb:" in text:
        index = text.index('lb:')
        text = text[index + 3:]
        return ["lb"], text

    elif "bl:" in text:
        index = text.index('bl:')
        text = text[index + 3:]
        return ["lb"], text

    elif "t:" in text:
        index = text.index('t:')
        text = text[index + 2:]
        return ["lt","rt"], text
    
    elif "b:"  in text:
        index = text.index('b:')
        text = text[index + 2:]
        return ["lb","rb"], text
    elif "r:"  in text:
        index = text.index('r:')
        text = text[index + 2:]
        return ["rt","rb"], text
    elif "l:"  in text:
        index = text.index('l:')
        text = text[index + 2:]
        return ["lt","lb"], text

    else:
        return ["lt", "rt","rb","lb"], text

# search in elastic search with the field and text
def search_all_field(text,fields):

    search_object = {    "size": 10000,
                        "query": {
                                "multi_match": {
                                    "query": text,
                                    "fields": fields,
                                    "analyzer": "regular_analyzer"

                                }
                        }
                    }
    res = _es.search(index=index_name, body=search_object)
    return res

def scroll_search_bool_fuzzy_synonym(text,fields):
    # create elastic fields from text field (s for synonym field)
    noSynonymField = [x for x in fields]
    synonymFields = [x+'s' for x in fields]
    # create search analyzer with fuzzy logic and weighted synonym
    search_object = { "size":1000,
                       "query": {
                           "function_score": {
                               "query": { "match_all": {} },
                               "functions": [{
                                   "filter": {
                                       "multi_match": {
                                           "query": text,
                                           "fields":noSynonymField,
                                           "analyzer": "regular_analyzer"
                                       }
                                   },
                                   "weight": 10
                               },
                                   {"filter": {
                                       "multi_match": {
                                           "query": text,
                                           "fields": synonymFields,
                                           "analyzer": "synonym_analyzer"
                                       } },
                                    "weight": 4
                                    },
                                   {"filter": {
                                       "multi_match": {
                                           "query": text,
                                           "fields": noSynonymField,
                                           "analyzer": "regular_analyzer",
                                           "fuzziness": "AUTO",
                                       }},
                                       "weight": 4
                                   }
                               ],
                               "score_mode": "max",
                               "min_score": 4
                           }
                       }
                      }



    data = _es.search(
        index=index_name,
        scroll='2m',
        size=1000,
        body=search_object
    )

    # Get the scroll ID
    sid = data['_scroll_id']
    scroll_size = len(data['hits']['hits'])
    if (scroll_size > 0):
        max_score = data['hits']['hits'][0]['_score']

    result = {x['_id']: x['_score'] / max_score for x in data['hits']['hits']}
    while scroll_size > 0:
        "Scrolling..."

        data = _es.scroll(scroll_id=sid, scroll='2m')
        # Update the scroll ID
        sid = data['_scroll_id']
        # Get the number of results that returned from the last scroll
        result.update({x['_id']: x['_score'] / max_score for x in data['hits']['hits']})
        scroll_size = len(data['hits']['hits'])

    return result


# search elastic index created from Rico and parse result to find the Rico ids
def textSearchRicoIndex(text, weight):
    fields,text = parseSearchString(text)
    results = scroll_search_bool_fuzzy_synonym(text,fields)
    hasResult = len(results)!=0
    return  hasResult,results

# Search all previous texts and current text. Called for text search and also validate the result
def searchAllText(allPrevTexts, curText,weight=1):
    hasCurRes , similarUI = textSearchRicoIndex(curText,weight)
    for text in allPrevTexts:
        _, curRes = textSearchRicoIndex(text, weight)
        for key in curRes:
            if key in similarUI:
                similarUI[key] += curRes[key]
            else:
                similarUI[key]=curRes[key]
    # resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]
    return hasCurRes, similarUI

# Called for removed text. Search based on all old text stack.
def removeTextSearch(allPrevTexts,weight=1):
    similarUI = {}
    for text in allPrevTexts:
        hasCurRes, curRes = textSearchRicoIndex(text, weight)
        for key in curRes:
            if key in similarUI:
                similarUI[key] += curRes[key]
            else:
                similarUI[key]=curRes[key]
    # resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]
    return similarUI


if __name__ == '__main__':
    # print("Damn it")
    res = _es.get(index=index_name, id='10050')
    print(res)
    # print(textSearchRicoIndex("setting",1))
