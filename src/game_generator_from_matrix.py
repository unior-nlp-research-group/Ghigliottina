def interactive_generator(matrix):
    while True:
        clues, solution, scores = matrix.genererate_game()
        print('Ecco la prossima ghigliottina:')
        print('\n'.join(clues))
        text = input('\nProva a indovinare --> ')
        guess = text.strip().lower()
        if not guess:
            print('exitig')
            return        
        if guess == solution:
            print('Indovinato!')        
        else:
            print('Sbagliato. La soluzione era {}'.format(solution))
        scores_str = ', '.join(['{0:.1f}'.format(s) for s in scores])
        print('Scores: {}'.format(scores_str))
        print('Sum: {0:.1f}'.format(sum(scores)))
        text = input('\nVuoi continuare? (y/n)')
        if not text or text!='y':
            print('exitig')
            return        

if __name__=='__main__':  
    from matrix_dict import Matrix_Dict
    import path
    OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_06_evalita_split/"
    MATRIX_REVERSED_FILE = OUTPUT_DIR + 'matrix_reversed.pkl' #solution in keys
    print('Loading matrix')
    matrix = Matrix_Dict()    
    matrix.read_matrix_from_file(MATRIX_REVERSED_FILE)
    print('Number of rows: {}'.format(matrix.size()))
    #unfound_pair_score = matrix.get_min_association_score()
    #print("Min association score: {0:.1f}".format(unfound_pair_score)) 
    interactive_generator(matrix)