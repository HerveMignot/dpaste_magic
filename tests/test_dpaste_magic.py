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


def test_get_raw_dpaste_url():
    url = '"https://dpaste.de/gA8U"'
    assert dpaste_magic.get_raw_dpaste_url(url) == 'https://dpaste.de/gA8U/raw'


def test_post_to_dpaste():
    source = 'print(42)'

    # Post to dpaste.de
    url = dpaste_magic.post_to_dpaste(source)
    # Get from dpaste.de
    content = requests.get(dpaste_magic.get_raw_dpaste_url(url))

    assert source == content.text


def test_dpaste_line():
    pass


def test_dpaste_cell():
    pass


def test_dpaste_expires_once():
    # run two times for 404
    pass
