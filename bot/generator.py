import gzip
import pickle

def get_matrix_generator():
    pkl_file = 'matrix_generator.pkl'
    with gzip.open(pkl_file, "rb") as pkl_in:        
        return pickle.load(pkl_in)    

matrix = get_matrix_generator()

def get_ghigliottina():
    import random
    solution = random.choice(list(matrix.keys()))
    clues = random.sample(list(matrix[solution].keys()), 5)
    explanations = [matrix[solution][c] for c in clues ]
    solution = solution.upper()        
    clues = [x.upper() for x in clues]
    return clues, solution, explanations
