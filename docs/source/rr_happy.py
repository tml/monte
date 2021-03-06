'''rr_happy -- generate haskell parser from railroad diagrams

TODO:
  1. lexical stuff
  2. grammar actions

'''

from sys import stderr  # poor-man's logging
from pprint import pformat

import railroad_diagrams as rrd

ok = [
    'NounExpr', 'name',
    'HideExpr',
    'CharExpr', 'charConstant', 'StrExpr', 'stringLiteral',
    'decLiteral', 'hexLiteral', 'digit', 'digits', 'hexDigits', 'hexDigit',
    'floatLiteral', 'floatExpn',
    'LiteralExpr', 'StrExpr', 'IntExpr', 'DoubleExpr', 'CharExpr']

todo = ['interface', 'InterfaceExpr', 'FunctionExpr',
        'comp', 'logical',
        'auditors',
        'ObjectExpr', 'objectExpr2', 'objectScript', 'matchers', 'doco']


def gen_rule(name, body, expr):
    if ok and name not in ok:
        return

    yield ''
    yield '{-'
    yield name + ' ::= ' + expr
    yield '-}'

    if name in todo:
        yield '{name} = failure -- TODO'.format(name=unCtor(name))
        return

    def fmtRule(items, lhs=None):
        pfx, sep = ('', ' ')

        if items and '<$>' in items[0]:
            pfx, sep, items = (items[0], ' <*> ', items[1:])
        rhs = sep.join(items) if items else 'return'

        # fixup: a *> <*> b to a *> b
        rhs = rhs.replace('*> <*>', '*>').replace('<*> <*', '<*')

        return (lhs + ' = ' if lhs else '  <|> ') + pfx + rhs

    def doRules(name, choices, indent=''):
        if choices:
            firstSeq, rest = choices[0], choices[1:]

            yield indent + fmtRule(firstSeq, lhs=name)
            for seq in rest:
                yield indent + fmtRule(map(unCtor, seq), lhs='')

    rules = expand(body, hint=unCtor(name))

    if rules:
        (_, choices), more = rules[0], rules[1:]

        for chunk in doRules(unCtor(name), choices):
            yield chunk
        if more:
            yield '  where'
            for name, choices in more:
                for chunk in doRules(unCtor(name), choices, indent='    '):
                    yield chunk


def unCtor(name):
    # IntExpr -> intExpr
    return name[0].lower() + name[1:]


def logged(label, val, logging=False):
    if logging:
        print >>stderr, '::', label, pformat(val)
    return val


RAW = {'IDENTIFIER': '(IT.identifier tokP)',
       'QUASI_TEXT': 'parseQuasiText'}


def expand(expr, hint=''):
    '''Expand expression, if necessary, to further choice-of-sequences rules.
    '''

    def mkName():
        ix[0] += 1
        return '%s_%s' % (hint, ix[0])
    ix = [0]
    recur = lambda items: logged('recur',
                                 [expand(item, mkName())
                                  for item in items
                                  if type(item) != rrd.Comment])
    more = lambda first, rest, exclude=[]: logged('more', (
        [first] +
        [(name, rule)
         for rules in rest
         for (name, rule) in rules
         if rule is not None
         and name not in exclude]))

    logged("expr class of " + hint, expr.__class__.__name__)

    if isinstance(expr, rrd.Terminal):
        if isinstance(expr, rrd.Char):
            c = expr.text
            lit = "'{c}'".format(
                c=(r"\'" if c == "'" else
                   r"\\" if c == '\\' else c))

            p = '(P.char {LIT})'.format(LIT=lit)
        else:
            tag = expr.text
            p = (RAW[tag] if tag in RAW
                 else '(IT.symbol tokP "{tag}")'.format(tag=tag))

        return logged('terminal ' + hint + ' =>',
                      [(unCtor(p), None)])

    elif isinstance(expr, rrd.Comment):
        if isinstance(expr, rrd.OneOf):
            p = '(P.oneOf {LIT})'.format(LIT=hStr(expr.elts))
        elif isinstance(expr, rrd.NoneOf):
            p = '(P.noneOf {LIT})'.format(LIT=hStr(expr.elts))
        else:
            raise NotImplementedError(expr.__class__.__name__, expr.text)

        thisRule = (hint, [[p]])
        return logged('comment ' + hint + ' =>',
                      [thisRule])

    elif isinstance(expr, rrd.NonTerminal):
        return logged('nonterminal ' + hint + ' =>',
                      [(unCtor(expr.text), None)])

    elif isinstance(expr, rrd.Skip):
        thisRule = (hint, [['(return ())']])
        return logged('Skip', [thisRule])

    elif isinstance(expr, rrd.Choice):
        expanded = recur(expr.items)
        exclude = []

        rhs = [[name]
               for rules in expanded
               for (name, _) in [rules[0]]]

        if isinstance(expr, rrd.SepBy):
            itemplus = expr.items[0]
            item = expand(itemplus.item, hint + '_1_1')[0][0]
            if not isinstance(itemplus.rep, rrd.Skip):
                rep = expand(itemplus.rep, hint + '_1_2')[0][0]
                rhs = [['({fun} {item} {rep})'
                        .format(fun=expr.fun, item=item, rep=rep)]]
                exclude = [hint + '_1', hint + '_2']
            else:
                rhs = [['(many0 {item})'.format(item=item)]]
            exclude = [hint + '_1', hint + '_2', hint + '_1_2']
        elif isinstance(expr, rrd.Maybe):
            item = expand(expr.items[0], hint + '_1')[0][0]
            rhs = [['P.optionMaybe', item]]
            exclude = [hint + '_2']
        elif isinstance(expr, rrd.Optional):
            item = expand(expr.items[0], hint + '_1')[0][0]
            rhs = [['P.option', expr.x, item]]
            exclude = [hint + '_2']

        elif isinstance(expr, rrd.Many):
            itemplus = expr.items[0]
            item = expand(itemplus.item, hint + '_1_1')[0][0]
            rhs = [['P.many', item]]
            exclude = [hint + '_1', hint + '_2']

        thisRule = (hint, rhs)

        return more(thisRule, expanded, exclude)

    elif isinstance(expr, rrd.Sequence):
        expanded = recur(expr.items)
        choices = [[name
                    for rules in expanded
                    for (name, _) in [rules[0]]]]
        if isinstance(expr, rrd.Sigil):
            rhs = choices[0]
            rhs = (
                ['(' + rhs[0] + ' *>'] +
                ((rhs[1:-1] + ['<* ' + rhs[-1]]) if expr.tail
                 else rhs[1:])
                + [')'])
            choices = [rhs]
        elif isinstance(expr, rrd.Ap):
            rhs = [expr.fun + " <$> "] + choices[0]
            choices = [rhs]
        elif isinstance(expr, rrd.Count):
            rhs = ["P.count", str(expr.qty)] + choices[0]
            choices = [rhs]
        elif isinstance(expr, rrd.String):
            rhs = ["P.string", hStr(expr.string)]
            choices = [rhs]
        elif isinstance(expr, rrd.Brackets):
            rhs = choices[0]
            op = 'IPC.betweenBlock' if '{' in rhs[0] else 'IPC.between'
            rhs = [op, rhs[0], rhs[-1]] + rhs[1:-1]
            choices = [rhs]
        elif isinstance(expr, rrd.ManyTill):
            rhs = choices[0]
            item = expanded[0][0][1][0][1]
            expanded = []
            rhs = ['P.manyTill', item, rhs[1]]
            choices = [rhs]

        thisRule = (hint, choices)

        return more(thisRule, expanded)

    elif isinstance(expr, rrd.OneOrMore):
        expanded = recur([expr.item, expr.rep])
        item = expand(expr.item, hint + '_1')[0][0]
        rep = expand(expr.rep, hint + '_2')[0][0]
        rhs = [['({fun} {item} {rep})'
                .format(fun='sepBy1', item=item, rep=rep)]]
        exclude = [hint + '_2']

        thisRule = (hint, rhs)

        return more(thisRule, expanded, exclude)
    else:
        raise NotImplementedError(expr)


def hStr(s,
         esc={'\n': '\\n',
              '\t': '\\t',
              '\\': '\\\\',
              '"': '\\"',
              "'": "\\'"}):
    r"""haskell string expression for s: "..." only; never '...'
    >>> print hStr("\\\n")
    "\\\n"
    >>> print hStr(r'''btnfr\'"''')
    "btnfr\\\'\""
    """
    return '"' + ''.join(esc.get(c, c) for c in s) + '"'


'''

Monte Syntax Builder
--------------------

stuff from `monte_parser.mt`:

AndExpr(lhs, rhs
AssignExpr(lval, assign(ej)
AugAssignExpr(op, lval, assign(ej)
BinaryExpr(lhs, opName, rhs
BindingExpr(noun(ej)
BindingExpr(noun(ej)
BindingPattern(n
BindPattern(n, g
BindPattern(n, null
Catcher(cp, cb
CatchExpr(n, cp, cb
CoerceExpr(base, guard(ej)
CompareExpr(lhs, opName, rhs
DefExpr(patt, ex, assign(ej)
DefExpr(patt, null, assign(ej)
EscapeExpr(p1, e1, null, null
EscapeExpr(p1, e1, p2, e2
ExitExpr(ex, null
ExitExpr(ex, val
FinallyExpr(n, finallyblock
FinalPattern(
FinalPattern(noun(ej), null
ForExpr(it, k, v, body, catchPattern, catchBody
ForwardExpr(name
FunctionExpr(patt, body
FunctionInterfaceExpr(doco, name, guards_, extends_, implements_,
FunctionScript(patts, namedPatts, resultguard, body, span), span)
GetExpr(n, g
HideExpr(e
IfExpr(test, consq, alt
IgnorePattern(g
IgnorePattern(null
InterfaceExpr(doco, name, guards_, extends_, implements_, msgs,
ListComprehensionExpr(it, filt, k, v, body,
ListExpr(items
ListPattern(items, tail
LiteralExpr(sub.getName(), null)
LiteralExpr("&" + sub.getNoun().getName(), null)
LiteralExpr("&&" + sub.getNoun().getName(), null)
LiteralExpr(t[1], t[2])
MapComprehensionExpr(it, filt, k, v, body, vbody,
MapExprAssoc, ej)
MapExpr(items
MapPatternImport, ej)
MapPattern(items, tail
MatchBindExpr(lhs, rhs
Matcher(pp, bl
MessageDesc(doco, "run", params, resultguard
MessageDesc(doco, verb, params, resultguard
MetaContextExpr(
MetaStateExpr(
"Method"
MismatchExpr(lhs, rhs
"Module"(importsList, exportsList, body,
NamedArg, ej)
NamedParamImport, ej)
NamedParam(null, p, null
NounExpr(t[1]
NounExpr(t[1], t[2])
ObjectExpr(doco, name, oAs, oImplements,
OrExpr(lhs, rhs
ParamDesc(name, g
PatternHoleExpr(advance(ej)[1]
PrefixExpr(op, call(ej)
PrefixExpr("-", prim(ej)
QuasiExprHole(
QuasiExprHole(subexpr
QuasiParserExpr(name, parts.snapshot()
QuasiParserPattern(name, parts.snapshot()
QuasiPatternHole(patt, t[2]))
QuasiPatternHole(subpatt
QuasiText(t[1], t[2]))
RangeExpr(lhs, opName, rhs
SameExpr(lhs, rhs, false
SameExpr(lhs, rhs, true
SamePattern(prim(ej), false
SamePattern(prim(ej), true
Script(oExtends, methods, matchers
SeqExpr([], advance(ej)[2])
SeqExpr(exprs.snapshot()
SeqExpr([], null)
SeqExpr([], null)
SlotExpr(noun(ej)
SlotExpr(noun(ej)
SlotPattern(n, g
SuchThatPattern(p, e
SwitchExpr(
"To"
ValueHoleExpr(advance(ej)[1]
ValueHoleExpr(advance(ej)[1]
ValueHolePattern(advance(ej)[1]
VarPattern(n, g
VerbAssignExpr(verb, lval, acceptList(expr),
ViaPattern(e, pattern(ej)
WhenExpr(exprs, whenblock, catchers.snapshot(),
WhileExpr(test, whileblock, catchblock
'''
