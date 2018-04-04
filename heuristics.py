'''
This file will contain different variable ordering heuristics to be used within
bt_search.

1. ord_dh(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the DH heuristic.
2. ord_mrv(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the MRV heuristic.
3. val_lcv(csp, var)
    - Takes in a CSP object (csp), and a Variable object (var)
    - Returns a list of all of var's potential values, ordered from best value
      choice to worst value choice according to the LCV heuristic.

The heuristics can use the csp argument (CSP object) to get access to the
variables and constraints of the problem. The assigned variables and values can
be accessed via methods.
'''

import random
from copy import deepcopy

def ord_dh(csp):
    maxDegree = -1
    var = None

    for v in csp.get_all_unasgn_vars():
        curDegree = 0
        for c in csp.get_cons_with_var(v):
            unasgnVars = c.get_unasgn_vars()
            seenVars = []
            for unasgnV in unasgnVars:
                if (not unasgnV is v) and (unasgnV not in seenVars):
                    seenVars.append(unasgnV)
                    curDegree += 1

        if curDegree > maxDegree:
            maxDegree = curDegree
            var = v

    return var

def ord_mrv(csp):
    mrv = float('inf')
    var = None

    for v in csp.get_all_unasgn_vars():
        rv = v.cur_domain_size()
        if rv < mrv:
            mrv = rv
            var = v
    return var

def val_lcv(csp, var):
    valOrder = [] # store tuple (value, numPruned)
    for d in var.cur_domain():
        var.assign(d)
        
        numPruned = 0
        for c in csp.get_cons_with_var(var):
            for adjV in c.get_unasgn_vars():
                for adjVal in adjV.cur_domain():
                    if not c.has_support(adjV, adjVal):
                        numPruned += 1

        var.unassign(d)
        valOrder.append((d, numPruned))

    sortedValOrder = sorted(valOrder, key=lambda x: x[1]) # ASCE order
    return [val for val, n in sortedValOrder]
