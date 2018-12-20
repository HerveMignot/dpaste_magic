# -*- coding: utf-8 -*-
import pytest

"""
Test paste 1 ligne : contenu + délai
Test paste 1 cellule : contenu + délai
Test affichage URL 1 ligne dans NB : récupération output ?
Test affichage URL 1 cellule dans NB : idem ?

Test get (avec une URL de test forever ?)

"""

import requests
import dpaste_magic


def test_dpaste_line():
    line = 'print(42)'
    url = dpaste_magic.dpaste(line=line, cell=None, return_url=True)
    content = requests.get(url + '/raw')
    assert line == content.text


def test_dpaste_cell():
    cell = 'print(42)'
    url = dpaste_magic.dpaste(line='', cell=cell, return_url=True)
    content = requests.get(url + '/raw')
    assert cell == content.text
    pass


# def test_dpaste_expires_once():
#     line = 'print(42)'
#     url = dpaste_magic.dpaste(line=line, cell=None, return_url=True)
#     content = requests.get(url + '/raw')
#     # run two times for 404
#     pass
