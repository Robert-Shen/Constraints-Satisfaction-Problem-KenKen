from cspbase import *
import itertools

'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = kenken_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the KenKen puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. kenken_csp_model (worth 20/100 marks)
    - A model built using your choice of (1) binary binary not-equal, or (2)
      n-ary all-different constraints for the grid.
    - Together with KenKen cage constraints.

'''

def binary_ne_grid(kenken_grid):
    # kenken grid dimension
    size = kenken_grid[0][0]

    # define domain
    dom = [i+1 for i in range(size)]

    # define Variables
    vars = []
    for vRow in dom:
        row = []
        for vCol in dom:
            row.append(Variable('V{}{}'.format(vRow, vCol), dom))
        vars.append(row)

    # define constraints
    cons = []
    for index in range(size):
        # add row binary not-equal constraints
        rowCons = helper_binary_ne_constraint(index, size, vars, True)
        cons.extend(rowCons)
        # add column binary not-equal constraints
        colCons = helper_binary_ne_constraint(index, size, vars, False)
        cons.extend(colCons)

    # construct CSP problem
    csp = CSP('{}-Kenken'.format(size))
    for vRow in vars:
        for v in vRow:
            csp.add_var(v)
    for c in cons:
        csp.add_constraint(c)

    return csp, vars

# return list of row/column constraints w.r.t. itself
def helper_binary_ne_constraint(index, size, vars, isRowConstraints):
    # produce the list of (rowIndex, colIndex) coordinate of each item w.r.t row/column
    if isRowConstraints:
        items = itertools.product([index], range(size))
    else:
        items = itertools.product(range(size), [index])

    cons = []
    # combine each item with each other to generate all binary combinations
    combinations = itertools.combinations(items, r=2)
    for comb in combinations:
        firstV = comb[0] # a tuple
        secondV = comb[1] # a tuple
        v1 = vars[firstV[0]][firstV[1]]
        v2 = vars[secondV[0]][secondV[1]]
        con = Constraint('C(V{}{},V{}{})'.format(firstV[0]+1, firstV[1]+1, secondV[0]+1, secondV[1]+1), [v1, v2])

        # check satisfiction condition
        satTuples = []
        for t in itertools.product(v1.domain(), v2.domain()):
            if t[0] != t[1]: # each two values must be different
                satTuples.append(t)
        con.add_satisfying_tuples(satTuples)
        cons.append(con)

    return cons

def nary_ad_grid(kenken_grid):
    # kenken grid dimension
    size = kenken_grid[0][0]

    # define domain
    dom = [i+1 for i in range(size)]

    # define Variables
    vars = []
    for vRow in dom:
        row = []
        for vCol in dom:
            row.append(Variable('V{}{}'.format(vRow, vCol), dom))
        vars.append(row)

    # define constraints
    cons = []
    for index in range(size):
        # add row n-ary all diff constraints
        rowCon = helper_nary_ad_constraint(index, size, vars, True)
        cons.append(rowCon)
        # add column n-ary all diff constraints
        colCon = helper_nary_ad_constraint(index, size, vars, False)
        cons.append(colCon)

    # construct CSP problem
    csp = CSP('{}-Kenken'.format(size))
    for vRow in vars:
        for v in vRow:
            csp.add_var(v)
    for c in cons:
        csp.add_constraint(c)

    return csp, vars

# return a single row/column constraint w.r.t. itself
def helper_nary_ad_constraint(index, size, vars, isRowConstraints):
    # produce the list of (rowIndex, colIndex) coordinate of each item w.r.t row/column
    if isRowConstraints:
        items = itertools.product([index], range(size))
    else:
        items = itertools.product(range(size), [index])

    # get list of vars in this row/col
    curVars = [vars[v[0]][v[1]] for v in items]
    # construct the name of constraint
    conNameVars = [str(v)[-3:] for v in curVars]
    conName = ','.join(conNameVars)
    # define constraint
    con = Constraint('C({})'.format(conName), curVars)

    # check satisfiction condition
    satTuples = []
    varsDom = [v.domain() for v in curVars]
    for t in itertools.product(*varsDom):
        if len(t) == len(set(t)): # all values in current row/col must be different
            satTuples.append(t)
    con.add_satisfying_tuples(satTuples)
    return con

def kenken_csp_model(kenken_grid):
    # kenken grid dimension
    size = kenken_grid[0][0]

    # define domain
    dom = [i+1 for i in range(size)]

    # define Variables
    vars = []
    for vRow in dom:
        row = []
        for vCol in dom:
            row.append(Variable('V{}{}'.format(vRow, vCol), dom))
        vars.append(row)

    # define constraints
    cons = []

    # add cage constraints
    for cage in kenken_grid:
        if len(cage) == 1: # board size specification
            continue
        if len(cage) == 2: # forced value to a cell
            val = cage[1]
            cell_i = (cage[0] // 10)-1
            cell_j = (cage[0] % 10)-1
            vars[cell_i][cell_j] = Variable('V{}{}'.format(cell_i+1, cell_j+1), [val])
        if len(cage) > 2: # larger cage
            val = cage[-2]
            op = cage[-1]
            cageVars = []
            for v in cage[:-2]: # get vars in cage
                cell_i = (v // 10)-1
                cell_j = (v % 10)-1
                cageVars.append(vars[cell_i][cell_j])

            # construct the name of constraint
            conNameVars = [str(v)[-3:] for v in cageVars]
            conName = ','.join(conNameVars)
            # define constraint
            con = Constraint('Cage({})'.format(conName), cageVars)

            # add satisfaction condition
            satTuples = []
            varsDom = [v.domain() for v in cageVars]
            for t in itertools.product(*varsDom):
                if op == 0: # addition
                    res = sum(t)
                    if res == val:
                        satTuples.append(t)
                elif op == 1: # subtraction
                    for r in itertools.permutations(t):
                        res = r[0]
                        for i in r[1:]:
                            res -= i
                        if res == val:
                            satTuples.append(t)
                elif op == 2: # division
                    for r in itertools.permutations(t):
                        res = r[0]
                        for i in r[1:]:
                            res /= i
                        if res == val:
                            satTuples.append(t)
                elif op ==3: # multiplication
                    res = 1
                    for r in t:
                        res *= r
                    if res == val:
                        satTuples.append(t)
            con.add_satisfying_tuples(satTuples)
            cons.append(con)

    # add n-ary all diff constraints
    for index in range(size):
        # add row n-ary all diff constraints
        rowCon = helper_nary_ad_constraint(index, size, vars, True)
        cons.append(rowCon)
        # add column n-ary all diff constraints
        colCon = helper_nary_ad_constraint(index, size, vars, False)
        cons.append(colCon)

    # construct CSP problem
    csp = CSP('{}-Kenken'.format(size))
    for vRow in vars:
        for v in vRow:
            csp.add_var(v)
    for con in cons:
        csp.add_constraint(con)

    return csp, vars
