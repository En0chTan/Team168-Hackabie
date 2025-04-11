#Combining Schematics similarity and Phonetic similarity 
from sentence_transformers import SentenceTransformer, util
from metaphone import doublemetaphone

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

known_phrases = {
    "call_passenger": ["call passenger", "panggil passenger", "reach out to rider"],
    "say_hi": ["hi","hello","ni hao","Helo"]
}

known_phonetics = {}
    
def phonetic_match(word):
    word_code = doublemetaphone(word)
    for each in word_code:
        if each != "":
            for x in known_phonetics: #keys
                for y in known_phonetics[x]: #values
                    if each == y[0] or each == y[1]:
                        print(f"Matched phonetic, likely Intent = {x}")


def schematics_match(input_phrase):
    input_vec = model.encode(input_phrase)

    for intent, phrases in known_phrases.items():
        for phrase in phrases:
            score = util.cos_sim(input_vec, model.encode(phrase))
            if score > 0.7:
                print(f"Matched intent: {intent} (score: {score.item():.2f})")
            else:
                print(f"UnMatched intent: {intent} (score: {score.item():.2f})")
                

for each in known_phrases:
    known_phonetics[each] = list()
        
for each in known_phrases:
    for every in known_phrases[each]:
        known_phonetics[each].append(doublemetaphone(every))
        
input_phrase = "hell"
phonetic_match(input_phrase)
schematics_match(input_phrase)