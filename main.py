import argparse, sys, glob, time
from preprocessing import *
from solver import *
from testing import *

# here are the arguments that you want to give to the program from the terminal/command line
parser = argparse.ArgumentParser(description='sudoku SAT solver')
parser.add_argument('-S1', '--sudoku1', metavar='', help='input puzzle: file or directory')
parser.add_argument('-S2', '--sudoku2', metavar='', help='input puzzle: file or directory')
parser.add_argument('-S3', '--sudoku3', metavar='', help='input puzzle: file or directory')
parser.add_argument('-S4', '--sudoku4', metavar='', help='input puzzle: file or directory')
parser.add_argument('-S5', '--sudoku5', metavar='', help='input puzzle: file or directory')

call = parser.parse_args()


def run(heur, input1):
    # parse arguments
    full_argments = parseargs(input1)

    # initialize variables:
    (variables, varbsCount, varbs) = getVars(full_argments)
    total_states = len(varbs)

    arguments = tautology(full_argments)  # remove tautologies, just necessary once.

    # initialization of data structure
    DPLL = {
        "validity_check": True,
        "arguments": [arguments],
        "assignments": [],
        "backtrack": [],
        "units": [],
        "first_backtrack": 0,
        "backtrack_counter": [],
        "recursion_depth": 0,
        "all_assignments": []
    }

    sys.setrecursionlimit(10 ** 9)

    # iniitial unit propagation and simplification --> majority of clauses removed
    while any(len(clause) == 1 for clause in DPLL["arguments"][-1]) and DPLL["validity_check"]:
        # reset time
        last_time = time.time()
        print("[INFO]   ..INITIALIZING..")
        variables, DPLL["assignments"], DPLL["units"] = unit_propagation(variables, DPLL["arguments"][-1], DPLL["assignments"], DPLL["units"])
        DPLL["arguments"][-1], DPLL["assignments"], DPLL["validity_check"] = simplify(DPLL["arguments"][-1], DPLL["assignments"], DPLL["validity_check"])
        # measure time
        print(time.time() - last_time)

    units = DPLL["units"].copy()
    DPLL["init_assignments"] = DPLL["assignments"].copy()
    DPLL["all_assignments"] = DPLL["assignments"].copy()
    assignments = DPLL["init_assignments"].copy()
    DPLL["units"] = []
    DPLL["assignments"] = []

    # initialize variables again (after first round of simplification):
    (variables, varbsCount, varbs) = getVars(DPLL["arguments"][-1])

    # this is the random heuristic i.e. randomly predetermining the order of variables to search through
    variables = random_heuristic(variables)

    # start recursive function

    DPLL = solve(DPLL, variables, heur)

    if not DPLL["validity_check"]:
        message = 'Failure! This formula is not satisfiable.\n'
    else:
        message = 'Success! This formula is satisfiable, with the following assignments: \n'

    for atoms in DPLL["assignments"]:
        assignments.append(atoms)
    for unit in DPLL["units"]:
        units.append(unit)

    return DPLL["init_assignments"], assignments, message, DPLL["backtrack_counter"], units, DPLL["recursion_depth"], DPLL["all_assignments"], total_states 


if call.sudoku1:
    example = call.sudoku1
    version = 'S1'
elif call.sudoku2:
    example = call.sudoku2
    version = 'S2'
elif call.sudoku3:
    example = call.sudoku3
    version = 'S3'
elif call.sudoku4:
    example = call.sudoku4
    version = 'S4'
elif call.sudoku5:
    example = call.sudoku5
    version = 'S5'
else:
    example = os.getcwd()
    version = "S4"

if __name__ == "__main__":

    # initialize:
    tests = []
    times = []
    backtracks = []
    units = []
    inits = []
    sudoku_names = []
    recs = []
    combined_metric = []
    cd = os.getcwd()

    if os.path.isdir(example):
        dir_loc = example + "/sudoku*.txt"
    else:
        dir_loc = example

    for file in glob.glob(dir_loc): # ("*.txt") for single file, otherwise directory
        print(file)
        sudoku_name = os.path.basename(file)
        sudoku_names.append(sudoku_name)
        print(sudoku_name)

        # reset time
        last_time = time.time()

        initial_assignments, assignments, message, backtrack_counter, unit_literals, recursive_depth, all_assigns, total_states = run(version, file)
        all_assigns = set(all_assigns)
        percent_space_searched = len(all_assigns)/total_states
        perf_metric = (percent_space_searched + recursive_depth + len(backtrack_counter) + (len(assignments) - len(unit_literals))**2) / len(initial_assignments)

        path = create_output(assignments, sudoku_name, example, version)

        # measure time
        now_time = time.time() - last_time

        # record results and dependent variables
        tests.append(len(assignments))
        backtracks.append(len(backtrack_counter))
        inits.append(len(initial_assignments))
        units.append(len(unit_literals))
        times.append(now_time)
        recs.append(recursive_depth)
        combined_metric.append(perf_metric)

        print(message, sorted(assignments, reverse=True))
        print('Number of Initial Assignments:   ', len(initial_assignments))
        print('Number of Assignments:           ', len(assignments))
        print('Number of Backtracks:            ', len(backtrack_counter))
        print('Number of Unit Literals:         ', len(unit_literals))
        print('Recursive Depth:                 ', recursive_depth)
        print('Performance Metric:              ', perf_metric)
        print("--- %s seconds ---" % (now_time))

        os.chdir(cd)

    os.chdir(path)
    collect_test_results(tests, sudoku_names, example, inits, backtracks, units,
                         times, recs, combined_metric)
    # print(tests)
    print("Puzzle Times:                ", times)
    print("Nr. of Backtracks:           ", backtracks)
    print("Nr. of Initial Assignments:  ", inits)
    print("Nr. of Units Propagated:     ", units)
    print("Recursive Depths:            ", recs)
    print("Performance Metric:          ", combined_metric)
