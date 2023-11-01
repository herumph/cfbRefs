import spacy

nlp = spacy.load('en_core_web_sm')
nlp.get_pipe("attribute_ruler").add([[{"TEXT": "Frisco"}]], {"LEMMA": "San Francisco"})

doc = nlp(u'I have flown to LA. Now I am flying to Frisco.')
for sent in doc.sents:
    goodBits = ['','']
    for w in sent:
        if w.dep_ == 'ROOT':
            goodBits[0] = w
        elif w.dep_ == 'pobj':
            goodBits[1] = w

    # making sure the verb is the correct tense
    if goodBits[0].tag_== 'VBG' or goodBits[1].tag_== 'VB':
        print([w.lemma_ for w in goodBits])
