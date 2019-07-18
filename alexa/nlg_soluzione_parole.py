from nltk.parse.generate import generate #, demo_grammar
from nltk import CFG

demo_grammar = \
'''
S -> V_give_me N_solution PP
S -> V_solve NP

V_give_me -> \
    "voglio" | "vorrei" | "voglio avere" | "vorrei avere" | \
    "dammi" | "mi dai" | "mi daresti" | \    
    "trovami" | "trova" |

N_solution -> "la soluzione" | "soluzione"

V_solve -> 'risolvi' | 'risolvere' | 'risolvermi'

PP -> PP_pref PP_post

NP -> NP_pref PP_post

NP_pref -> \
    "la ghigliottina" | "ghigliottina" | \
    "il gioco" | "gioco" | 

PP_pref -> \
    "della ghigliottina" | "ghigliottina" | \
    "del gioco" | "gioco" |  

PP_post -> \
    "per le parole" WORDS | "con le parole" WORDS | "parole" WORDS
    

WORDS -> "{word_one} {word_two} {word_three} {word_four} {word_five}"
'''

grammar = CFG.fromstring(demo_grammar)
# print(grammar)

generated_setences = sorted([" ".join(words) for words in generate(grammar, n=10000)])
total = 0

with open('list_soluzione_parole.txt', 'w') as f_out:
    for sentence in generated_setences:    
        f_out.write(sentence + "\n")

print(len(generated_setences))



