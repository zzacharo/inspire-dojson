# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON model definition for HEP."""

from __future__ import absolute_import, division, print_function

from inspire_utils.helpers import force_list
from inspire_utils.record import get_value

from ..model import FilterOverdo, add_schema, clean_record
from ..utils.arxiv import normalize_arxiv_category, classify_field


def add_arxiv_categories(record, blob):
    if not record.get('arxiv_eprints') or not blob.get('65017'):
        return record

    for category in force_list(get_value(blob, '65017')):
        if category.get('2') == 'arXiv' and category.get('a'):
            record['arxiv_eprints'][0]['categories'].append(
                normalize_arxiv_category(category['a'])
            )

    return record


def add_inspire_categories(record, blob):
    if not record.get('arxiv_eprints') or record.get('inspire_categories'):
        return record

    for arxiv_category in force_list(get_value(record, 'arxiv_eprints.categories')):
        inspire_category = classify_field(arxiv_category)
        if inspire_category:
            record['inspire_category'] = [
                {
                    'source': 'arxiv',
                    'term': inspire_category,
                },
            ]

    return record


def ensure_document_type(record, blob):
    if not record.get('document_type'):
        record['document_type'] = ['article']

    return record


def ensure_curated(record, blob):
    if 'curated' not in record:
        record['curated'] = True

    return record


def convert_curated(record, blob):
    if blob.get('curated') is False:
        a_value = '* Temporary entry *' if blob.get('core') else '* Brief entry *'
        record.setdefault('500', []).insert(0, {'a': a_value})

    return record


hep_filters = [
    add_schema('hep.json'),
    add_arxiv_categories,
    add_inspire_categories,
    ensure_curated,
    ensure_document_type,
    clean_record,
]

hep2marc_filters = [
    convert_curated,
    clean_record,
]

hep = FilterOverdo(filters=hep_filters)
hep2marc = FilterOverdo(filters=hep2marc_filters)
