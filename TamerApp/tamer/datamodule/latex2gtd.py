# from: https://github.com/yqingli123/TDv2/blob/main/utils/latex2gtd_v2_2.py

import random

import numpy as np
from dataclasses import dataclass


@dataclass
class Symbol:
    idx: int
    token: str

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, str)
        return self.token == __value


class Node:
    def __init__(self, x=0):
        self.x = x
        self.childs = []
        self.relations = []


def findnextbracket(latex: list, leftbracket="{"):
    if leftbracket == "{":
        rightbracket = "}"
    elif leftbracket == "[":
        rightbracket = "]"
    else:
        raise AssertionError("Unkown Bracket!")

    num = 0
    for li, l in enumerate(latex):
        if l == leftbracket:
            num += 1
        if l == rightbracket:
            num -= 1
            if num == 0:
                return li
    return -1


def findendmatrix(latex):
    num = 1
    for li, l in enumerate(latex):
        if l == "\\begin{matrix}":
            num += 1
        if l == "\\end{matrix}":
            num -= 1
            if num == 0:
                return li
    return -1


def latex2Tree(latex: list):
    if len(latex) == 0:
        return Node("<eol>")

    cur_node = Node(latex[0])
    symbol = latex.pop(0)

    if symbol == "<bol>":
        if len(latex) > 0 and latex[0] == "_":
            latex.pop(0)
            assert latex[0] == "{", "_ not with {"
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("sub")
            for _ in range(li + 1):
                latex.pop(0)
        if len(latex) > 0 and latex[0] == "^":
            latex.pop(0)
            assert latex[0] == "{", "^ not with {"
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("sup")
            for _ in range(li + 1):
                latex.pop(0)
            li = findnextbracket(latex, leftbracket="{")

    elif symbol == "\\begin{matrix}":
        li = findendmatrix(latex)
        sub_latex = latex[:li]
        node = latex2Tree(sub_latex)
        cur_node.childs.append(node)
        cur_node.relations.append("Mstart")
        for _ in range(li + 1):
            latex.pop(0)

    elif symbol in ["\\iint", "\\bigcup", "\\sum", "\\lim", "\\coprod"]:
        if len(latex) > 0 and latex[0] == "_":
            latex.pop(0)
            assert latex[0] == "{", "_ not with {"
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("below")
            for _ in range(li + 1):
                latex.pop(0)
        if len(latex) > 0 and latex[0] == "^":
            latex.pop(0)
            assert latex[0] == "{", "^ not with {"
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("above")
            for _ in range(li + 1):
                latex.pop(0)

    elif symbol in [
        "\\dot",
        "\\ddot",
        "\\hat",
        "\\check",
        "\\grave",
        "\\acute",
        "\\tilde",
        "\\breve",
        "\\bar",
        "\\vec",
        "\\widehat",
        "\\overbrace",
        "\\widetilde",
        "\\overleftarrow",
        "\\overrightarrow",
        "\\overline",
    ]:
        assert latex[0] == "{", "CASE 3 above not with {"
        li = findnextbracket(latex, leftbracket="{")
        sub_latex = latex[1:li]
        node = latex2Tree(sub_latex)
        cur_node.childs.append(node)
        cur_node.relations.append("below")
        for _ in range(li + 1):
            latex.pop(0)

    elif symbol in ["\\underline", "\\underbrace"]:
        assert latex[0] == "{", "CASE 3 above not with {"
        li = findnextbracket(latex, leftbracket="{")
        sub_latex = latex[1:li]
        node = latex2Tree(sub_latex)
        cur_node.childs.append(node)
        cur_node.relations.append("above")
        for _ in range(li + 1):
            latex.pop(0)

    elif symbol in ["\\xrightarrow", "\\xleftarrow"]:
        if latex[0] == "[":
            li = findnextbracket(latex, leftbracket="[")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("below")
            for _ in range(li + 1):
                latex.pop(0)
        if latex[0] == "{":
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("above")
            for _ in range(li + 1):
                latex.pop(0)

    elif symbol == "\\frac":
        assert latex[0] == "{", "\\frac above not with {"
        li = findnextbracket(latex, leftbracket="{")
        sub_latex = latex[1:li]
        node = latex2Tree(sub_latex)
        cur_node.childs.append(node)
        cur_node.relations.append("above")
        for _ in range(li + 1):
            latex.pop(0)
        assert latex[0] == "{", "\\frac below not with {"
        li = findnextbracket(latex, leftbracket="{")
        sub_latex = latex[1:li]
        node = latex2Tree(sub_latex)
        cur_node.childs.insert(-1, node)
        cur_node.relations.insert(-1, "below")
        for _ in range(li + 1):
            latex.pop(0)

    elif symbol == "\\sqrt":
        if latex[0] == "[":
            li = findnextbracket(latex, leftbracket="[")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("leftup")
            for _ in range(li + 1):
                latex.pop(0)
        assert latex[0] == "{", "\\sqrt inside not with {"
        li = findnextbracket(latex, leftbracket="{")
        sub_latex = latex[1:li]
        node = latex2Tree(sub_latex)
        cur_node.childs.append(node)
        cur_node.relations.append("inside")
        for _ in range(li + 1):
            latex.pop(0)

    else:
        if len(latex) > 0 and latex[0] == "_":
            latex.pop(0)
            assert latex[0] == "{", "_ not with {"
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("sub")
            for _ in range(li + 1):
                latex.pop(0)
        if len(latex) > 0 and latex[0] == "^":
            latex.pop(0)
            assert latex[0] == "{", "^ not with {"
            li = findnextbracket(latex, leftbracket="{")
            sub_latex = latex[1:li]
            node = latex2Tree(sub_latex)
            cur_node.childs.append(node)
            cur_node.relations.append("sup")
            for _ in range(li + 1):
                latex.pop(0)

    if len(latex) > 0 and latex[0] == "\\\\":
        latex.pop(0)
        relation = "nextline"
    elif len(latex) > 0:
        relation = "right"
    else:
        relation = "end"
    node = latex2Tree(latex)
    cur_node.childs.append(node)
    cur_node.relations.append(relation)

    return cur_node


def node2list(tree: Node, is_shuffle: bool = False):
    index = 0
    gtd = []

    def _node2list(parent, parent_index, relation, current, initial=None):
        if current is None or current.x == "<eol>":
            return
        nonlocal index
        if initial is not None:
            index = 1
        else:
            index = index + 1
        gtd.append([current.x, index, parent, parent_index, relation])
        parent_index = index
        zip_childs = list(zip(current.childs, current.relations))
        if is_shuffle:
            random.shuffle(zip_childs)
        for child, relation in zip_childs:
            _node2list(current.x, parent_index, relation, child)

    _node2list(Symbol(-1, "<sos>"), 0, "start", tree, initial=True)
    return gtd


def to_struct(latex_list):
    symbols = [Symbol(i, t) for i, t in enumerate(latex_list)]
    tree = latex2Tree(symbols)
    gtd = node2list(tree)
    d = {g[0].idx: g[2].idx for g in gtd}
    ret = [d[i] if i in d else -1 for i in range(len(latex_list))]
    return ret


