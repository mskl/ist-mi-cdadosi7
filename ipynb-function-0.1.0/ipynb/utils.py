"""
Utility functions for dealing with manipulating notebooks.

Try to not put too many things here, nor to re-implement nbformat.
"""
import ast


PREAMBLE=\
"""
##############################################################################
# This source has been auto generated from an IPython/Jupyter notebook file. #
# Please modify the origin file                                              #
##############################################################################
"""

ALLOWED_NODES = set([
    ast.ClassDef,
    ast.FunctionDef,
    ast.Import,
    ast.ImportFrom
])


def validate_nb(nb):
    """
    Validate that given notebook JSON is importable

    - Check for nbformat == 4
    - Check that language is python

    Do not re-implement nbformat here :D
    """
    if nb['nbformat'] != 4:
        return False

    language_name = (nb.get('metadata', {})
        .get('kernelspec', {})
        .get('language', '').lower())
    return language_name == 'python'


def filter_ast(module_ast):
    """
    Filters a given module ast, removing non-whitelisted nodes

    It allows only the following top level items:
     - imports
     - function definitions
     - class definitions
     - top level assignments where all the targets on the LHS are all caps
    """
    def node_predicate(node):
        """
        Return true if given node is whitelisted
        """
        for an in ALLOWED_NODES:
            if isinstance(node, an):
                return True

        if isinstance(node, ast.Assign):
            return all([t.id.isupper() for t in node.targets])

        return False

    module_ast.body = [n for n in module_ast.body if node_predicate(n)]
    return module_ast


class IPynbParser(object):

    def __init__(self, filename, as_function=False):
        self.filename = filename
        self.params = []  # List[(name: str, doc: str)]
        self.ret = None
        self.code = []
        self.doc = []
        self.as_function = as_function

    def parse_code_block(self, lines):
        """
        Parse code block, handle #params, #return, #skip
        """
        iterator = enumerate(lines)

        for i, raw_line in iterator:
            line = raw_line.strip()
            parts = line.split(None, 2)
            if not self.as_function or \
                    len(parts) == 0 or \
                    parts[0] not in ['#param', '#return', '#skip'] or \
                    i + 1 >= len(lines): 
                self.code.append(raw_line)
                continue
            doc = parts[1] if len(parts) > 1 else None
            indent = raw_line[:raw_line.index('#')]
            if parts[0] == '#param':
                nextline = next(iterator)[1]
                code = ast.parse(nextline)
                if len(code.body) != 1 or not isinstance(code.body[0], ast.Assign):
                    raise Exception('params must be specified with an assignment')
                expr = code.body[0]
                name = expr.targets[0]
                if isinstance(name, ast.Tuple):
                    raise Exception('Tuple assignment is not supported for params')
                if not doc:
                    doc = 'Defaults to ' + nextline[nextline.index('=') + 1:]
                self.params.append((name.id, doc))
                self.code.append(indent + 'if {} is None:\n'.format(name.id))
                self.code.append(indent + '    {}\n'.format(nextline))
            elif parts[0] == '#return':
                ret = next(iterator)[1]
                self.ret = doc
                self.code.append(indent + 'return {}\n'.format(ret))
            elif parts[0] == '#skip':
                next(iterator)

        self.code.append('\n')

    def parse_markdown(self, source):
        if self.code:
            self.code.append('\n# ' + '# '.join(source) + '\n')
        else:
            self.doc.append(''.join(source))

    def parse(self, nb):
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                # transform the input to executable Python
                # IPython commands should be filtered out
                lines = [line for line in cell['source']
                    if not line.strip().startswith('%')]
                self.parse_code_block(lines)
            if cell['cell_type'] == 'markdown':
                self.parse_markdown(cell['source'])

    def get_func_name(self):
        return self.filename

    def get_doc(self):
        doc = ''.join(self.doc)
        doc += '\n'
        for name, desc in self.params:
            doc += ':param {}: {}\n'.format(name, desc or '')
        if self.ret:
            doc += ':return: {}\n'.format(self.ret)
        return doc

    def get_param_list(self):
        return [pair[0] for pair in self.params]

    def get_code(self):
        doc = self.get_doc()

        if self.as_function:
            code = 'def {}({}):\n'.format(
                self.get_func_name(),
                ', '.join(map('{}=None'.format, self.get_param_list())),
            )
            if doc.strip():
                code += '    """\n    {}\n    """\n'.format(
                    doc.replace('\n', '\n    '))

            code += ''.join(map('    {}'.format, self.code))
            return code

        code = '"""\n{}\n"""\n'.format(doc) if doc.strip() else ''
        code += ''.join(self.code)
        return code


def code_from_ipynb(nb, markdown=False, filename=None, as_function=False):
    """
    Get the code for a given notebook

    nb is passed in as a dictionary that's a parsed ipynb file
    """
    parser = IPynbParser(filename, as_function)
    parser.parse(nb)
    return parser.get_code()
