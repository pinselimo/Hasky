"""Utility functions for parsing Haskell."""

def lmap(f,xs):
    """Like map but returns a list instead of a generator."""
    return [f(x) for x in xs]

def apply(fs,t):
    """Weirdly similar to Haskell's ap for subscriptable types.

    Parameters
    ----------
    fs : iterable
        List of tuples which have a `callable` as second member.
    t : iterable
        Arguments for the `callable`.

    Returns
    -------
    applied : tuple
        Results of the application of the callables
        to the arguments in `t` with the same index.
    """
    return tuple(f[1](x) for f,x in zip(fs,t))

def strip_io(tp):
    """IO is somewhat disregarded in the FFI exports. IO CDouble
    looks the same as CDouble from Python's side. So we remove
    the monadic part from our type to process the rest.

    Parameters
    ----------
    tp : str
        Haskell type statement.

    Returns
    -------
    stripped : (str, str)
        Tuple of `'IO '` if there was an IO statement or
        the empty string if there was none and the rest of the type statement.
    """
    io = tp.find('IO ')
    if io < 0:
        return '', tp
    else:
        return 'IO ',tp[io+3:]

def tuple_types(hs_type):
    """Extracts the types declarations inside a Haskell tuple type statement.

    Parameters
    ----------
    hs_type : str
        Haskell type statement for a tuple.

    Returns
    -------
    types : list(str)
        Haskell type statements inside the tuple.
    """
    match = lambda x: match_parens(hs_type,x)

    openp = hs_type.find('(')
    closep = match(openp)
    parens = [(openp, closep)]

    while 1:
        openp = hs_type.find('(',parens[-1][-1])

        if openp == -1:
            break
        else:
            closep = match(openp)
            parens.append((openp, closep))

    return [hs_type[start:end] for start,end in parens]

def match_parens(s, i):
    """Given a string and the index of the opening
    parenthesis returns the index of the closing one.

    Parameters
    ----------
    s : str
        The string to match parentheses on.
    i : int
        The initial index to start from.

    Returns
    -------
    closing : int
        Index of the next matching closing paranthesis.
    """
    x = 0
    for it in range(i,len(s)):
        c = s[it]
        if c == '(':
            x += 1

        elif c == ')':
            x -= 1

        if x == 0:
            return it
    else:
        return len(s)

def parse_generator(f_llist, f_carray, f_tuple, f_string, f_default):
    """Parser generator for parsing Haskell type statements.

    Parameters
    ----------
    f_llist : callable
        Function to call in case of linked lists.
    f_carray : callable
        Function to call in case of arrays.
    f_tuple : callable
        Function to call in case of tuples.
    f_string : callable
        Function to call in case of string.
    f_default : callable
        Function to call in case of string.

    Returns
    -------
    parser : callable
        Function taking a string object with a Haskell type statement
        and parsing it using the appropriate function.
    """
    def parser(hs_type):
        """Parser for Haskell type statements.

        Parameters
        ----------
        hs_type : str
            Haskell type statement.

        See also
        --------
        parse_generator
        """
        ll = hs_type.find('CList ')
        arr = hs_type.find('CArray ')
        tup = hs_type.find('CTuple')
        st = hs_type.find('CWString')
        ## Linked List first
        if ll+1 and (ll < arr or arr < 0) and (ll < tup or tup < 0):
            return f_llist(hs_type[ll+len('CList '):])
        ## Array first
        elif arr+1 and (arr < tup or tup < 0):
            return f_carray(hs_type[arr+len('CArray '):])
        ## Tuple first
        elif tup+1:
            return f_tuple(hs_type[tup+len('CTupleX '):])
        ## String first
        elif st+1:
            return f_string(hs_type[st+len('CWString '):])
        else:
            return f_default(hs_type)

    return parser
