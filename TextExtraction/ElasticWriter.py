from elasticsearch import Elasticsearch
data_folder = r"curatedtexts"
import os

from ast import  literal_eval
_es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index_name = 'rico'


def create_index(es_object, index_name):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards":1,
            "number_of_replicas": 0,
            "similarity": {
                "default": {
                    "type": "boolean"
                }
            },
                "analysis": {
                  "analyzer": {
                    "regular_analyzer": {
                      "tokenizer": "punctuation",
                      "filter": [
                        "lowercase",
                        "kstem"
                      ]
                    },
                    "synonym_analyzer": {
                          "tokenizer": "punctuation",
                          "filter": [
                              "lowercase",
                              "kstem",
                              "synonym1"
                          ]
                    }
                  },
                  "tokenizer": {
                    "punctuation": {
                      "type": "pattern",
                      "pattern": "[ .,!?]"
                    }
                  },
                  "filter": {
                    "synonym1": {
                          "type": "synonym",
                          "synonyms_path": "Synonym.txt"
                    }
                  }
                }
        },
        "mappings": {
            "properties": {
                "lt": {
                    "type": "text",  # formerly "string"
                    "analyzer": "regular_analyzer",
                    "search_analyzer": "regular_analyzer"
                },
                "lb": {
                    "type": "text",  # formerly "string"
                    "analyzer": "regular_analyzer",
                    "search_analyzer": "regular_analyzer"
                },
                "rt": {
                    "type": "text",  # formerly "string"
                    "analyzer": "regular_analyzer",
                    "search_analyzer": "regular_analyzer"
                },
                "rb": {
                    "type": "text",  # formerly "string"
                    "analyzer": "regular_analyzer",
                    "search_analyzer": "regular_analyzer"
                },
                "lts": {
                    "type": "text",  # formerly "string"
                    "analyzer": "synonym_analyzer",
                    "search_analyzer": "synonym_analyzer"
                },
                "lbs": {
                    "type": "text",  # formerly "string"
                    "analyzer": "synonym_analyzer",
                    "search_analyzer": "synonym_analyzer"
                },
                "rts": {
                    "type": "text",  # formerly "string"
                    "analyzer": "synonym_analyzer",
                    "search_analyzer": "synonym_analyzer"
                },
                "rbs": {
                    "type": "text",  # formerly "string"
                    "analyzer": "synonym_analyzer",
                    "search_analyzer": "synonym_analyzer"
                }
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            res = es_object.indices.create(index=index_name, ignore=400, body=settings)
            print(res)
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created

# to delete the whole index_name
def deteteIndex(elastic_object, index_name):
    try:
       res= elastic_object.indices.delete(index=index_name, ignore=[400, 404])
       print(res)
    except Exception as ex:
        print(str(ex))

# prints the current index mapping
def getMaping(elastic_object, index_name):
    res = elastic_object.indices.get_mapping(index=index_name)
    print(res)

# store it in the index_name of elastic object with the rico_id and docString
def store_record(elastic_object, index_name, rico_id, docString):
    try:
        outcome = elastic_object.index(index=index_name,id=rico_id, body=docString)
        print(outcome)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))

# see the result of the current analyzer
def analyze(elastic_object, index_name):
    res = elastic_object.indices.analyze(index=index_name, body={
        "analyzer": "my_custom_analyzer",
        "text": ["HELLO WORLD. Today is the 2nd day of the week!!!!  jumping   it is Monday."]
    })
    for i in res['tokens']:
        print(i['token'])

# print an index_id
def getIndex(elastic_object,index_name, index_id):
    res = elastic_object.get(index=index_name, id=index_id)
    print(res)

# search a test
def search(es_object, index_name, text):
    search_object = {'query': {'match': {'bl':text}}}

    res = es_object.search(index=index_name, body=search_object)
    print(res)

def indexOne(filename):
    # modify json with synonym field
    absFol = os.path.join(data_folder,filename)
    f = open(absFol, "r")
    contents = f.read()
    singleJSON = literal_eval(contents)
    modified_json ={}
    modified_json['lt']=singleJSON['lt']
    modified_json['lts']=singleJSON['lt']
    modified_json['rt']=singleJSON['rt']
    modified_json['rts']=singleJSON['rt']
    modified_json['rb']=singleJSON['rb']
    modified_json['rbs']=singleJSON['rb']
    modified_json['lb']=singleJSON['lb']
    modified_json['lbs']=singleJSON['lb']

    filename = filename.split('.')[0]
    store_record(_es,index_name,filename,modified_json)
    return

def IndexAll():
    for fileName in os.listdir(data_folder):
        indexOne(fileName)
    return


if __name__ == '__main__':

      create_index(_es,index_name)
      IndexAll()
