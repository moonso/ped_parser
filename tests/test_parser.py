# -*- coding: utf-8 -*-
import codecs

from ped_parser import parser


def test_alternative_parser():
    """Test parsing a ped file with alternative formatting."""
    # test default
    with codecs.open('tests/fixtures/alternative.ped', 'r') as handle:
        family_parser = parser.FamilyParser(handle, family_type='alt')

    # we've only loaded one family
    ped = family_parser.families.values()[0]

    assert ped.family_id == 'family_id'
    assert len(ped.individuals) == 1

    sample = ped.individuals.values()[0]
    assert sample.extra_info['Capture_kit'] == 'Agilent_SureSelect.V5'

    # TODO: test with optional CMMS check
