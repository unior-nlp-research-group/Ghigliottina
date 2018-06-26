#! /usr/bin/env python3

GAME_SET_100_FILE = "/Users/fedja/scratch/Ghigliottina/annotated_game_words.txt"

# CORPORA

PAISA_CONLL_INFO = {
    'name': 'PAISA_CONLL',
    'file': '/Users/fedja/scratch/CORPORA/PAISA/paisa.annotated.CoNLL.utf8.gz',
    'words': 242958792,
    'compressed': True,
    'encoding': 'utf-8',
    'exlude_pattern': '^(:?<text|#)'
}

PAISA_RAW_INFO = {
    'name': 'PAISA_RAW',
    'file': '/Users/fedja/scratch/CORPORA/PAISA/paisa.raw.utf8.gz',
    'lines': 7943592,
    'words': 225292817,
    'compressed': True,
    'encoding': 'utf-8',
    'exlude_pattern': '^(:?<text|#)'
}

WIKI_IT_TITLES_INFO = {
    'name': 'WIKI_IT_TITLES',
    'file': '/Users/fedja/scratch/CORPORA/Wiki_IT/itwiki-latest-all-titles.processed',
    'lines': 5333296,
    'compressed': False,
    'encoding': 'utf-8',
    'exlude_pattern': False
}

WIKI_IT_TEXT_INFO = {
    'name': 'WIKI_IT_TEXT',
    'file': '/Users/fedja/scratch/CORPORA/Wiki_IT/Wiki_IT_Text.xml',
    'lines': 23996595,
    'compressed': False,
    'encoding': 'utf-8',
    'exlude_pattern': '^(:?<)'    
}

PROVERBI_INFO = {
    'name': 'PROVERBI',
    'file': '/Users/fedja/scratch/CORPORA/Proverbi/proverbi_merged.txt',
    'lines': 2241,
    'compressed': False,
    'encoding': 'utf-8',
    'exlude_pattern': False
}

PAISA_LEX_FREQ_FILE = PAISA_RAW_INFO['file'] + '_lex_freq.txt'
PAISA_SOSTANTIVI_FREQ_FILE = '/Users/fedja/scratch/CORPORA/PAISA/sostantivi_freq.txt'
PAISA_AGGETTIVI_FREQ_FILE = '/Users/fedja/scratch/CORPORA/PAISA/aggettivi_freq.txt'

ITWAC_RAW_INFO = {
    'name': 'ITWAC_RAW',
    'file': '/Users/fedja/scratch/CORPORA/ITWAC/raw/more.filtered.pre.pos.corpus.gz',
    'lines': 1871819,
    'words': 1619326044,
    'compressed': True,
    'encoding': 'iso-8859-1',
    'exlude_pattern': '^CURRENT URL'
}

DE_MAURO_POLIREMATICHE_INFO = {
    'name': 'DE_MAURO_POLIREMATICHE',
    'file': '/Users/fedja/scratch/CORPORA/DE_MAURO/polirematiche_sorted.txt',
    'lines': 30633,
    'words': 75917,
    'compressed': False,
    'encoding': 'utf-8',
    'exlude_pattern': False
}

# LEMMATIZATION
LAEMMAS_INFLECIONS_FILE = '/Users/fedja/scratch/CORPORA/Lemmatization/lemmatization-it.txt'

# DE DEMAURO
DE_MAURO_PATH = '/Users/fedja/scratch/CORPORA/DE_MAURO/'
POLIREMATICHE_SORTED_FILE = DE_MAURO_PATH + 'polirematiche_sorted.txt' # 30633
DIZIONARIO_BASE_SORTED_FILE = DE_MAURO_PATH + 'diz_base_sorted.txt' # 7179
DIZ_POLI_WORD_SORTED_FILE = DE_MAURO_PATH + 'diz_poli_sorted.txt' # 18035
DIZIONARIO_BASE_SOSTANTIVI_FILE = DE_MAURO_PATH + 'diz_base_sostantivi.txt' # 5055 only singular
DIZIONARIO_BASE_AGGETTIVI_FILE = DE_MAURO_PATH + 'diz_base_aggettivi.txt' # 1514
DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE = DE_MAURO_PATH + 'diz_paisa_sostantivi.txt' # 6684 -- singular + 1000 most freq sost. paisa conll (plurals check)
DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE = DE_MAURO_PATH + 'diz_paisa_aggettivi.txt' # 2484 -- singular + 1000 most freq agg. paisa conll (plurals check)
DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_INFLECTED_FILE = DE_MAURO_PATH + 'diz_paisa_sostantivi_inflected.txt' # 16416 -- DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE + inflections
DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_INFLECTED_FILE = DE_MAURO_PATH + 'diz_paisa_aggettivi_inflected.txt' # 8196 -- DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE + inflections

# WIKI_IT
WIKI_IT_TITLES = '/Users/fedja/scratch/CORPORA/Wiki_IT/itwiki-latest-all-titles' # page_namespace	page_title
WIKI_IT_TITLES_PROCESSED = '/Users/fedja/scratch/CORPORA/Wiki_IT/itwiki-latest-all-titles.processed'

# WIKI_DATA
WIKI_DATA_PEOPLE_FILE = "/Users/fedja/scratch/CORPORA/WikiData/people_it.json" # 7984 (7361 unique if splitting names)
# [{'human':'url', 'name': 'first middle last'}, {...}]

def analizeFreq(corpus_info):
    import core
    from collections import defaultdict
    lines_extractor = core.extract_lines(corpus_info)
    lex_freq = defaultdict(int)
    for line in lines_extractor:
        tokens = core.tokenizeLineReplaceWordCats(line)
        for t in tokens:
            lex_freq[t] += 1
    for CAT in core.ALL_CATS:
        if CAT in lex_freq:
            del lex_freq[CAT]  
    with open(PAISA_LEX_FREQ_FILE, 'w') as f_out:
        for w,f in sorted(lex_freq.items(), key=lambda x: -x[1]):
            f_out.write('{}\t{}\n'.format(f,w))

def buildPaisaPosLexFile(pos):   
    import core 
    from collections import defaultdict
    lines_extractor = core.extract_lines(PAISA_CONLL_INFO, report_every=1000000)
    pos_lex_freq = defaultdict(int)
    token_count = 0
    for line in lines_extractor:
        fields = line.split()
        if len(fields)!=8:
            continue
        token_count += 1
        word = fields[1].lower()
        if fields[3]==pos and core.VALID_WORD_PATTERN.match(word):            
            pos_lex_freq[word] += 1
    print('Read tokens: {}'.format(token_count))
    return pos_lex_freq

def buildPaisaSostantiviFile():
    import core
    sost_lex_freq = buildPaisaPosLexFile('S')
    core.printLexFreqToFile(sost_lex_freq, PAISA_SOSTANTIVI_FREQ_FILE)    

def buildPaisaAggettiviFile():
    import core
    sost_lex_freq = buildPaisaPosLexFile('A')
    core.printLexFreqToFile(sost_lex_freq, PAISA_AGGETTIVI_FREQ_FILE)    

def builDizAugmentedPaisa(lexPosFreqFile, lexPosBaseFile, min_freq, output_file):    
    import core
    vowels = [v for v in 'aeiou']    
    output_file_log = output_file + '_log'
    paisa_pos_lex_freq = core.loadLexFreqFromFile(lexPosFreqFile)
    diz_base = core.loadLexiconFromFile(lexPosBaseFile)
    diz_sostantivi_prefix = set()
    for w in diz_base:
        if len(w)>1 and w[-1] in vowels:
            diz_sostantivi_prefix.add(w[:-1])
    with open(output_file_log, 'w') as f_out:
        for w,f in sorted(paisa_pos_lex_freq.items(), key=lambda x: -x[1]):
            if f>=min_freq and len(w)>1 and w not in diz_base and w[:-1] in diz_sostantivi_prefix and w[-1] in vowels:
                diz_base.add(w)
                origin = next(o for o in diz_base if o[:-1]==w[:-1] and o!=w and len(o)==len(w) and o[-1] in vowels)
                f_out.write('{}->{}\n'.format(origin, w))
    core.printLexiconToFile(diz_base, output_file)

def builDizSostantiviAugmentedPaisa():
    min_freq = 1000
    lexPosFreqFile = PAISA_SOSTANTIVI_FREQ_FILE
    lexPosBaseFile = DIZIONARIO_BASE_SOSTANTIVI_FILE
    builDizAugmentedPaisa(lexPosFreqFile, lexPosBaseFile, min_freq, DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE)

def builDizAggettiviAugmentedPaisa():
    min_freq = 1000
    lexPosFreqFile = PAISA_AGGETTIVI_FREQ_FILE
    lexPosBaseFile = DIZIONARIO_BASE_AGGETTIVI_FILE
    builDizAugmentedPaisa(lexPosFreqFile, lexPosBaseFile, min_freq, DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE)

def getLemmasInflectionDict():
    from collections import defaultdict
    dict = defaultdict(list)
    with open(LAEMMAS_INFLECIONS_FILE) as f_in:
        for line in f_in:
            lemma, inflection = line.split('\t')
            dict[lemma].append(inflection)
    return dict

def buildDizSostantiviAugmentedPaisaInflected():
    import core     
    lemma_inflections_dict = getLemmasInflectionDict()
    diz_base_inflected = [
        [DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE, DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_INFLECTED_FILE],
        [DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE, DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_INFLECTED_FILE]
    ]
    for diz_base_file, diz_inflected_file in diz_base_inflected:
        word_set = core.loadLexiconFromFile(diz_base_file) # set
        inflected_words = set()
        for lemma in word_set:
            if lemma in lemma_inflections_dict:
                inflected_words.update(lemma_inflections_dict[lemma])
        word_set.update(inflected_words)
        core.printLexiconToFile(inflected_words, diz_inflected_file)

def post_process_wiki_it_titles():
    with open(WIKI_IT_TITLES, 'r') as f_in, open(WIKI_IT_TITLES_PROCESSED, 'w') as f_out:
        for line in f_in:
            title = line.split()[1].replace('_',' ')
            f_out.write(title + '\n')

def getWikiDataPeople(split_names):
    import json
    with open(WIKI_DATA_PEOPLE_FILE) as f_in:
        people_dict = json.load(f_in)
        people_name_set = set()
        for item in people_dict:
            if split_names:
                people_name_set.update(item['name'].split())          
            else:
                people_name_set.add(item['name'])
        return people_name_set

def extractCompundsInLexicon(lexicon_set):
    from collections import defaultdict
    dict = defaultdict(list)
    compounds_dict = defaultdict(list) # radio -> [attività attivo], contro -> figura
    for w in lexicon_set:
        for i in range(1, len(w)):
            first, second = w[:i], w[i:]
            if first in lexicon_set and second in lexicon_set:
                compounds_dict[first].append(second)
    return compounds_dict     
    # json.dump(compounds_dict, open('/Users/fedja/scratch/CORPORA/DE_MAURO/compunds.txt','w'), indent=3, ensure_ascii=False)
    