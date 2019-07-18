from nltk.parse.generate import generate #, demo_grammar
from nltk import CFG

demo_grammar = \
'''
S -> V_give_me N_solution PP
S -> V_solve NP

V_give_me -> \
    "voglio" | "vorrei" | "voglio avere" | "vorrei avere" | \
    "darmi" | "dare" | "dammi" | "mi dai" | "mi daresti" | \    
    "trovarmi" | "trovare" | "trovami" | "trova" |

N_solution -> "la soluzione" | "soluzione" | "l'ultima soluzione"

V_solve -> 'risolvi' | 'risolvere' | 'risolvermi'

PP -> PP_pref PP_post

NP -> NP_pref PP_post

NP_pref -> \
    "la ghigliottina" | "ghigliottina" | "l'ultima ghigliottina" | "ultima ghigliottina" | \
    "il gioco" | "gioco" | "l'ultimo gioco" | "ultimo gioco" | \
    "la puntata" | "puntata" | "l'ultima puntata" | "ultima puntata" | \
    "le parole" | "parole" | "le ultime parole" | "ultime parole" | \
    "gli indizi" | "indizi" | "gli ultimi indizi" | "ultimi indizi" |

PP_pref -> \
    "della ghigliottina" | "ghigliottina" | "dell'ultima ghigliottina" | "ultima ghigliottina" | \
    "del gioco" | "gioco" | "dell'ultimo gioco" | "ultimo gioco" | \
    "della puntata" | "puntata" | "dell'ultima puntata" | "ultima puntata" | \
    "delle parole" | "parole" | "delle ultime parole" | "ultime parole" | \
    "degli indizi" | "indizi" |"degli ultimi indizi" | "ultimi indizi" |

PP_post -> "di questa sera" |
'''

grammar = CFG.fromstring(demo_grammar)
# print(grammar)

generated_setences = sorted([" ".join(words) for words in generate(grammar, n=10000)])
total = 0

with open('list_ultima_ghigliottina.txt', 'w') as f_out:
    for sentence in generated_setences:    
        f_out.write(sentence + "\n")

print(len(generated_setences))



