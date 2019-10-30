# -*- coding: utf-8 -*-

from parameters import TWITTER_MAX_LEN
from key import TWITTER_BOT_SCREEN_NAME

INFO_QUESTIONS_LOWER = ['chi sei?', 'cosa fai?', 'come funzioni?']

def restrict_text_to_twitter_limit(reply, text):
    char_available = TWITTER_MAX_LEN - len(reply) - 22
    if len(text) > char_available:
        return text[:char_available] + '...'
    return text

def intro(from_twitter):
    if from_twitter:
        return "🤠 Ciao, sono un risolutore automatico della #ghigliottina, il gioco dell'#leredita di #rai1. Prova a scrivermi i 5 indizi separati da spazi o da virgole, ad esempio twitta: @{} oro argento previsione colazione punta (o mandami un'immagine della TV con i 5 indizi).".format(TWITTER_BOT_SCREEN_NAME)
    else:
        return "🤠 Ciao, sono un risolutore automatico della Ghigliottina del gioco dell'Eredità di Rai1. Prova a mettermi alla prova scrivendo 5 indizi separati da spazi o da virgole, ad esempio scrivi\n*oro argento previsione colazione punta*\n(oppure mandami un'immagine della TV con i 5 indizi)."

def wrong_input(from_twitter, text):
    reply = "🧐 La string inserita ({}) non contiene 5 indizi. Se un indizio contiene spazi mandami gli indizi separati da virgole."
    if from_twitter:
        text = restrict_text_to_twitter_limit(reply, text)
        return reply.format(text)    
    else:
        return reply.format(text)    
        
def no_solution_found(from_twitter, text, solution):
    if from_twitter:
        reply = "😫 Non ho trovato nessuna soluzione alle 5 parole inserite ({}). Provo comunque con {}\n#ghigliottina #leredita #rai1 #leredità #laghigliottina".format('{}',solution)
        text = restrict_text_to_twitter_limit(reply, text)
        return reply.format(text)
    else:
        reply = "😫 Non ho trovato nessuna soluzione alle 5 parole inserite ({})."
        return reply.format(text)

def high_confidence_solution(from_twitter, text, solution):
    solution = solution.upper()
    text = text.upper()
    if from_twitter:
        reply = "😎 Sono quasi certo che la soluzione della #ghigliottina per (gli indizi {}) sia {}\n#leredita #rai1 #leredità #laghigliottina".format('{}',solution)
        text = restrict_text_to_twitter_limit(reply, text)
        return reply.format(text)        
    else:    
        reply = "😎 Sono quasi certo che la soluzione della Ghigliottina per gli indizi *{}* sia *{}*."
        return reply.format(text, solution)

def good_confidence_solution(from_twitter, text, solution):
    solution = solution.upper()
    text = text.upper()
    if from_twitter:
        reply = "🤔 Sono abbastanza convinto che la soluzione della #ghigliottina #leredita (per gli indizi {}) sia {}\n#leredita #rai1 #leredità #laghigliottina".format('{}',solution)
        text = restrict_text_to_twitter_limit(reply, text)
        return reply.format(text)
    else:    
        reply = "🤔 Sono abbastanza convinto che la soluzione della Ghigliottina per gli indizi *{}* sia *{}*."
        return reply.format(text, solution)

def average_confidence_solution(from_twitter, text, solution):
    solution = solution.upper()
    text = text.upper()
    if from_twitter:
        reply = "🤨 Credo che la soluzione della #ghigliottina #leredita (per gli indizi {}) sia {}\n#leredita #rai1 #leredità #laghigliottina".format('{}',solution)
        text = restrict_text_to_twitter_limit(reply, text)
        return reply.format(text)
    else:    
        reply = "🤨 Credo che la soluzione della Ghigliottina per gli indizi *{}* sia *{}*."
        return reply.format(text, solution)

def low_confidence_solution(from_twitter, text, solution):
    solution = solution.upper()
    text = text.upper()
    if from_twitter:
        reply = "😜 Non sono sicuro, ma credo che la soluzione della #ghigliottina #leredita (per gli indizi {}) sia {}\n#leredita #rai1 #leredità #laghigliottina".format('{}',solution)
        text = restrict_text_to_twitter_limit(reply, text)
        return reply.format(text)
    else:    
        reply = "😜 Non sono sicuro, ma credo che la soluzione della Ghigliottina per gli indizi *{}* sia *{}*."
        return reply.format(text, solution)

def getImgProblemText():
    return "😮 Non sono riuscito a trovare gli indizi nell'immagine che mi hai inviato."