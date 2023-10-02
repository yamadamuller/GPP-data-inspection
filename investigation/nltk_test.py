import nltk
from nltk.corpus import wordnet as wn
from unidecode import unidecode

#nltk.download("wordnet")
#nltk.download('omw-1.4')

lng = "por"
words = ["ambiental", "sustentável", "emissão", "ciclo", "poluente",
         "eficiência", "energia", "renovável"]
variants = []

for words in words:
    related = wn.synsets(words, lang=lng)
    for related in related:
        for lemma in related.lemmas(lang=lng):
            variants.extend(lemma.synset().lemma_names(lang=lng))

variants = list(set(variants))
for i in range(len(variants)):
    variants[i] = unidecode(variants[i])
