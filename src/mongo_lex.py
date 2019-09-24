from mongoengine import connect, Document, IntField, StringField, DictField

connect('Lexicon')

class Pattern(Document):
    surface = StringField(primary_key = True, max_length=100)
    abstract = StringField(max_length=100)  # with <<<CAT>>>
    word_1 = StringField(max_length=30)
    word_2 = StringField(max_length=30)
    source_count = DictField() # source -> count

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Pattern:{}".format(self.surface)

    @staticmethod
    def add_pattern(surface, abstract, word_1, word_2, source):
        objs = Pattern.objects(surface=surface)
        if objs:
            pattern = objs.get()
        else:
            pattern = Pattern(surface=surface, abstract=abstract, word_1=word_1, word_2=word_2, source_count={})
        if source in pattern.source_count:
            pattern.source_count[source] += 1
        else:
            pattern.source_count[source] = 1
        pattern.save()

def test_add_pattern():
    Pattern.add_pattern('surface', 'abstract', 'word_1', 'word_2', 'source')

def total_count():
    total_patterns = Pattern.objects().count()
    print("Total patterns: {}".format(total_patterns))

THRESHOLDS = {
    'ITWAC_RAW': 5,
    'WIKI_IT_TITLES':2,
    'PAISA_RAW': 20,
    'PROVERBI': 1,
    'DE_MAURO_POLIREMATICHE': 1
}

def get_patterns():
    casa_first_patterns = Pattern.objects(word_1='casa')
    total_patterns_casa_first = casa_first_patterns.count()
    print("Total patterns with casa as word_1: {}".format(total_patterns_casa_first))
    for p in casa_first_patterns:
        for source,freq in p.source_count.items():
            if freq >= THRESHOLDS[source]:
                print("{}: {} {}".format(p.surface, freq, source))

if __name__ == "__main__":    
    get_patterns()
    