#! /usr/bin/env python3

import utility

###################
## main
###################

if __name__=='__main__':  
    import argparse
    parser = argparse.ArgumentParser()    
    parser.add_argument("-m", "--model", help="the path to the model file")    
    args = parser.parse_args()
    print('Loading association matrix')
    matrix = utility.loadObjFromPklFile(args.model)
    solver(matrix)

