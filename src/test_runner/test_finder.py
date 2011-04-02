# This is the object that locates all *.enzo_test directories

import os.path
import optparse
import sys

varspec = dict(
    name = (str, ''),
    answer_testing_script = (str, None),
    nprocs = (int, 1),
    runtime = (str, 'short'),
    critical = (bool, True),
    cadence = (str, 'nightly'),
    hydro = (bool, False),
    mhd = (bool, False),
    gravity = (bool, False),
    cosmology = (bool, False),
    chemistry = (bool, False),
    cooling = (bool, False),
    AMR = (bool, False),
    dimensionality = (int, 1),
    author = (str, ''),
    fullpath = (str, '.'),
    run_par_file = (str, None),
    fulldir = (str, '.'),
    max_time_minutes = (float, 1),
    radiation = (str, None),
)

known_variables = dict( [(k, v[0]) for k, v in varspec.items()] )
variable_defaults = dict( [(k, v[1]) for k, v in varspec.items()] )

def add_files(my_list, dirname, fns):
    my_list += [os.path.join(dirname, fn) for
                fn in fns if fn.endswith(".enzotest")]

class EnzoTestCollection(object):
    def __init__(self, tests = None):
        if tests is None:
            # Now we look for all our *.enzo_test files
            fns = []
            os.path.walk(".", add_files, fns)
            self.tests = []
            for fn in sorted(fns):
                print "HANDLING", fn
                self.add_test(fn)
        else:
            self.tests = tests

    def add_test(self, fn):
        # We now do something dangerous: we exec the file directly and grab
        # its environment variables from it.
        local_vars = {}
        execfile(fn, {}, local_vars)
        test_spec = variable_defaults.copy()
        test_spec['fullpath'] = fn
        test_spec['fulldir'] = os.path.dirname(fn)
        test_spec['run_par_file'] = os.path.basename(test_spec['fulldir'])
        for var, val in local_vars.items():
            if var in known_variables:
                caster = known_variables[var]
                if val == "False": val = False
                test_spec[var] = caster(val)
                if val == "None": test_spec[var] = None
            else:
                print "%s UNRECOGNIZED VARIABLE %s" % ( fn, var)
        self.tests.append(test_spec)

    def unique(self, param):
        pp = set()
        for t in self.tests:
            pp.add(t.get(param, "Key Missing"))
        return pp

    def params(self):
        pp = set()
        for t in self.tests:
            pp.update(set(t.keys()))
        return pp

    def select(self, **kwargs):
        pp = []
        for t in self.tests:
            include = True
            for param, value in kwargs.items():
                if value == "None": value = None
                if value == "False": value = False
                if t.get(param, "Key Missing") != value:
                    include = False
                    break
            if include == True: pp.append(t)
        return EnzoTestCollection(tests = pp)

    def summary(self):
        for param in sorted(self.params()):
            if param.startswith("full"): continue
            print param
            for v in self.unique(param):
                print "     %s" % (v)
            print
        print
        print "NUMBER OF TESTS", len(self.tests)

class UnspecifiedParameter(object):
    pass
unknown = UnspecifiedParameter()

if __name__ == "__main__":
    etc = EnzoTestCollection()
    parser = optparse.OptionParser()
    parser.add_option("-o", "--output-dir", dest='outputdir',
                      help="Where to place the run directory")
    for var, caster in sorted(known_variables.items()):
        parser.add_option("", "--%s" % (var),
                          type=str, default = unknown)
    options, args = parser.parse_args()
    construct_selection = {}
    for var, caster in known_variables.items():
        if getattr(options, var) != unknown:
            val = getattr(options, var)
            if val == 'None': val = None
            if val == "False": val = False
            construct_selection[var] = caster(val)
    print
    print "Selecting with:"
    for k, v in sorted(construct_selection.items()):
        print "     %s = %s" % (k, v)
    etc2 = etc.select(**construct_selection)
    print
    print "\n".join(list(etc2.unique('name')))
    print "Total: %s" % len(etc2.tests)
