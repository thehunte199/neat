#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Stephen Bunn <r>
# GNU GPLv3 <https://www.gnu.org/licenses/gpl-3.0.en.html>

"""
obvious.py
.. module:: neat
    :platform: Linux, MacOSX, Win32
    :synopsis:
    :created: 02-16-2017 15:16:44
    :modified: 02-16-2017 15:16:44
.. moduleauthor:: Stephen Bunn <r>
"""

import importlib

from .. import const
from ..models import Record, RecordPoint
from ._common import AbstractTranslator

import bs4
import pint
import dateutil.parser


class ObviousTranslator(AbstractTranslator):
    _parser_pref = ['lxml', 'html.parser']

    def __init__(self, **kwargs: dict) -> None:
        self._meta = kwargs
        self._unit_reg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
        self._expression_unit_map = {
            # energy
            'kWh': 'kilowatthour',
            'Wh': 'watthour',
            'MWh': 'megawatthour',
            'VAh': 'volt_ampere * hour',
            'kVAh': 'kilovolt_ampere * hour',
            'MVAh': 'megavolt_ampere * hour',
            'VARh': '',
            'kVARh': '',
            'MVARh': '',
            'Btu': 'btu',
            'kBtu': 'kilobtu',
            'MBtu': 'megabtu',
            'MMBtu': 'megabtu',
            'BtuE6': 'megabtu',
            'Ton-Hrs': 'ton * hour',
            'therms': 'thm',
            # power
            'W': 'watt',
            'mW': 'milliwatt',
            'kW': 'kilowatt',
            'MW': 'megawatt',
            'VA': 'volt_ampere',
            'kVA': 'kilovolt_ampere',
            'MVA': 'megavolt_ampere',
            'VAR': '',
            'kVAR': '',
            'MVAR': '',
            'Btu/hr': 'btu/hr',
            # voltage
            'Volts': 'volt',
            'mV': 'millivolt',
            'kV': 'kilovolt',
            'MV': 'megavolt',
            # current
            'Amps': 'amp',
            'mA': 'milliamp',
            # event counting
            'cycles': 'cycles',
            'pulses': '',
            'revolutions': 'revolution',
            'starts': '',
            # frequency
            'Hz': 'hertz',
            'kHz': 'kilohertz',
            'RPM': 'rpm',
            # resistance
            'Ohms': 'ohm',
            'kohms': 'kiloohm',
            # mass
            'kgs': 'kilogram',
            'Lbs': 'pound',
            'Tons': 'ton',
            # mass flow
            'kg/hr': 'kilogram/hour',
            'Lb/hr': 'pound/hour',
            # volume
            'Gallons': 'gallon',
            'Cubic Feet': 'foot ** 3',
            'Cubic Meters': 'meter ** 3',
            'Liters': 'liter',
            # volume flow
            'Cubic Feet/sec': 'foot ** 3/second',
            'Cubic Feet/min': 'foot ** 3/minute',
            'CFm': 'foot ** 3/minute',
            'Cubic Feet/hr': 'foot ** 3/hour',
            'CFH': 'foot ** 3/hour',
            'Cubic Meters/hr': 'meter ** 3 / hour',
            'Gpm': 'gallon/minute',
            'Gph': 'gallon/hour',
            'MGD': 'megagallon/day',
            'Liters/sec': 'liter/second',
            'Liters/min': 'liter/minute',
            'Liters/hr': 'liter/hour',
            # velocity
            'MPH': 'mph',
            'KPH': 'kph',
            # temperature
            'Degrees C': 'degC',
            'Degrees F': 'degF',
            # humidity
            '%RH': '',
            # phase
            'Degrees': 'degree',
            # electrical
            'PF': '',
            'aPF': '',
            'dPF': '',
            # intensity
            'W/m^2': 'watt / meter ** 2',
            # dimensionless
            '%': '',
            'PPM': '',
            '': '',
            # time
            'days': 'day',
            'hours': 'hour',
            'minutes': 'minute',
            'seconds': 'second',
            'ms': 'millisecond',
            # pressure
            'Pa': 'pascal',
            'kPa': 'kilopascal',
            'inWC': '',
            'inAq': '',
            'inHg': 'inHg',
            'cmHg': 'cmHg',
            'mmHg': 'mmHg',
        }

    @property
    def parser(self) -> str:
        if not hasattr(self, '_parser') or \
                self._parser not in self._parser_pref:
            for parser in self._parser_pref:
                if importlib.util.find_spec(parser):
                    self._parser = parser
                    break
        return self._parser

    @property
    def unit_map(self) -> dict:
        if not hasattr(self, '_unit_map'):
            self._unit_map = {}
            for (k, v) in self._expression_unit_map.items():
                self._unit_map[k] = self._unit_reg.parse_expression(v)
        return self._unit_map

    def validate(self, data: str) -> bool:
        return bs4.BeautifulSoup(data, self.parser)\
            .find('error').text == '0'

    def translate(self, data: str) -> dict:
        record = Record()
        soup = bs4.BeautifulSoup(data, self.parser)
        for device in soup.find_all('devices'):
            record.name = device.find('name').text
            for rec in device.find_all('record'):
                record.timestamp = dateutil.parser.parse(
                    rec.find('time').text
                ).timestamp()
                rec_error = rec.find('error').text
                for point in rec.find_all('point'):
                    record_point = RecordPoint()
                    record_point.name = point.attrs['name']
                    record_point.value = float(point.attrs['value'])
                    record_point.unit = self.unit_map[point.attrs['units']]
                    record.data.append(record_point)

        print(record.to_json())
