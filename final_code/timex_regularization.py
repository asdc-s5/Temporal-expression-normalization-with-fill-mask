import re
import copy
import csv
import os
from tqdm.auto import tqdm
import pandas as pd
import argparse

def create_csv(filename, fields):
    with open(filename, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the FIELDS_E3C 
        csvwriter.writerow(fields) 
        
def regularize_virs_date(attributes):
    vir_regularized = [''] * 9
    vir = attributes[len(attributes) - 1]
    rule = ''
    pad = '<pad>'
    millennium_parts = ['KA', 'MA', 'GA']
    year_parts = ['WE', 'SP', 'SU', 'WI', 'FA', 'Q', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'HALF1', 'HALF2']
    day_parts = ['TAF', 'TMO', 'TMI', 'TEV', 'NI', 'TDT', 'W']
    anchor_excluded = ['Ranchor']
    fuzzy_expressions = ['PRESENT', 'PAST', 'FUTURE']

    if attributes[1] == 'DATE':
        vir_millennium_parts = [element for element in millennium_parts if element in vir]
        vir_year_parts = [element for element in year_parts if str(element).lower() in str(vir).lower()]
        vir_day_parts = [element for element in day_parts if str(element).lower() in str(vir).lower()]
        vir_anchor_excluded = [element for element in anchor_excluded if str(element).lower() in str(vir).lower()]
        vir_fuzzy_expressions = [element for element in fuzzy_expressions if str(element).lower() in str(vir).lower()]

        if 'DWanchor' in vir:
            vir = vir.replace('DWanchor(', '').replace(')', '')
            parts = re.split(r',', vir)
            operation = parts[0]
            vir_regularized[5] = parts[-1].split('MONTHS')[0]
            vir_regularized[6] = 'MONTHS'
            if operation == '-':
                vir_regularized[4] = 'SUBTRACT'
                rule = 'dwanchor_subtract'
            if operation == '+':
                vir_regularized[4] = 'ADD'
                rule = 'dwanchor_add'
        elif 'Sanchor' in vir:
            vir = vir.replace('Sanchor(', '').replace(')', '')
            parts = re.split(r',', vir)
            operation = parts[0]
            vir_regularized[5] = parts[-1][0:4]
            vir_regularized[6] = parts[-1][5:]
            if operation == '-':
                vir_regularized[4] = 'SUBTRACT'
                rule = 'sanchor_subtract_' + str(vir_regularized[6])
            if operation == '+':
                vir_regularized[4] = 'ADD'
                rule = 'sanchor_add_' + str(vir_regularized[6])
        elif 'Danchor' in vir:
            vir = vir.replace('Danchor(', '').replace(')', '')
            parts = re.split(r',', vir)
            date_parts = re.split(r'-', parts[1])
            vir_regularized[3] = date_parts[2]
            if date_parts[1] != 'XX':
                vir_regularized[1] = date_parts[1]
            if parts[0] == '+':
                vir_regularized[4] = 'ADD'
                rule = 'danchor_add'
            elif parts[0] == '-':
                vir_regularized[4] = 'SUBTRACT'
                rule = 'danchor_subtract'
        elif 'anchor' in vir:
            vir = vir.replace('anchor(', '').replace(')', '')
            parts = re.split(r',', vir)
            operation = parts[1]
            if 'DAYW' in parts[-1]:
                vir_regularized[5] = parts[-1][0]
                vir_regularized[6] = parts[-1][1:]
            if operation == '-':
                vir_regularized[4] = 'SUBTRACT'
                rule = 'anchor_subtract_' + str(vir_regularized[6])
                vir_regularized[5] = parts[-1][0:len(parts[-1]) - 1]
                vir_regularized[6] = parts[-1][len(parts[-1]) - 1]
            if operation == '+':
                vir_regularized[4] = 'ADD'
                vir_regularized[5] = parts[-1][0:len(parts[-1]) - 1]
                vir_regularized[6] = parts[-1][len(parts[-1]) - 1]
                rule = 'anchor_add_' + str(vir_regularized[6])
            if operation == 'x':
                vir_regularized[4] = 'NEUTRAL'
                vir_regularized[5] = 0
                vir_regularized[6] = parts[-1]
                rule = 'anchor_no_modification_' + str(vir_regularized[6])
            if operation == 'z':
                vir_regularized[4] = 'NEUTRAL'
                rule = 'anchor_dayw' + str(vir_regularized[6])
        elif str.isdigit(vir):
            if len(vir) == 3:
                vir_regularized[7] = vir[0:2]
                vir_regularized[8] = vir[2]
                rule = 'century_decade'
            elif len(vir) < 3:
                rule = 'year_less_than_3_digits'
            elif len(vir) == 4:
                vir_regularized[0] = vir
                rule = 'only_year'
            elif len(vir) > 4:
                rule = 'year_more_than_4_digits'
        elif '-' in vir:
            parts = re.split(r'-', vir)
            if len(parts) == 2:
                if len(vir_year_parts) > 0 or re.search(r'^(\d+|X+|X+\d+)-T\d+$', vir) or re.search(r'^(\d+|X+|X+\d+)-HALF\d+$', vir):
                    if parts[0] != 'XXXX':
                        vir_regularized[0] = parts[0]
                    vir_regularized[6] = parts[1]
                    rule = 'year_part_of_year'
                elif 'W' in vir:
                    if parts[0] != 'XXXX':
                        vir_regularized[0] = parts[0]
                    vir_regularized[2] = parts[1].replace('W', '')
                    rule = 'year_week'
                else:
                    if parts[0] != 'XXXX':
                        vir_regularized[0] = parts[0]
                    if parts[1] != 'XX':
                        vir_regularized[1] = parts[1]
                    rule = 'year_month'
            elif len(parts) == 3:
                if len(vir_day_parts) > 0:
                    if 'W' in vir:
                        vir_regularized[0] = parts[0]
                        vir_regularized[2] = parts[1].replace('W', '')
                        if parts[2] != 'XX':
                            vir_regularized[3] = parts[2]
                        rule = 'year_month_day_week'
                    else:
                        vir_regularized[0] = parts[0]
                        vir_regularized[1] = parts[1]
                        vir_hour_parts_aux = copy.deepcopy(vir_day_parts)
                        vir_hour_parts_aux.append('TMI')
                        for part in vir_hour_parts_aux:
                            parts_unit = re.split(fr'({part})', parts[-1])
                            if len(parts) > 1:
                                break
                        if parts_unit[1] == 'NI':
                            vir_regularized[6] = 'T' + parts_unit[1]
                        else:
                            vir_regularized[6] = parts_unit[1]
                        vir_regularized[3] = parts_unit[0]
                        rule = 'year_month_day_part_of_day'
                else:
                    if parts[0] != 'XXXX':
                        vir_regularized[0] = parts[0]
                    if parts[1] != 'XX':
                        vir_regularized[1] = parts[1]
                    if parts[2] != 'XX':
                        vir_regularized[3] = parts[2]
                    rule = 'year_month_day'
        elif 'WE' in vir:
            vir_regularized[2] = vir.replace('WE', '')
            rule = 'only_week'
        elif len(vir_year_parts) > 0:
            for part in vir_year_parts:
                parts = re.split(fr'({part})', vir)
                if len(parts) > 1:
                    vir_regularized[5] = parts[0]
                    vir_regularized[6] = parts[1]
                    rule = 'cir_part_of_year'
                    break
        elif len(vir_fuzzy_expressions):
            vir_regularized[6] = vir.replace('_REF', '')
            rule = 'fuzzy'
        elif 'BC' in vir:
            rule = 'before_christ'
        elif vir == 'null':
            rule = 'vir_null'
        elif len(vir_millennium_parts) > 0:
            rule = 'part_of_millennium_' + str(vir_millennium_parts[0])
        elif 'fa' in vir:
            rule = 'fiscal_year'
        else:
            rule = 'vir_no_pattern'

    for i, vir_char in enumerate(vir_regularized):
        if vir_char == '':
            vir_regularized[i] = pad
    return vir_regularized, rule


def regularize_virs_time_present(attributes, text):
    vir_regularized_time = [''] * 10
    vir_regularized_date = [''] * 9
    vir = attributes[len(attributes) - 1]
    pad = '<pad>'
    day_parts = ['TAF', 'TMO', 'TMI', 'TEV', 'TNI', 'TDT', 'AF', 'MO', 'MI', 'EV', 'NI', 'DT', 'W']
    fuzzy_expressions = ['PRESENT', 'PAST', 'FUTURE']
    date_expressions = ['ahora', 'actualmente', 'el momento', 'recientemente', 'futuro']

    vir_fuzzy_expressions = [element for element in fuzzy_expressions if str(element).lower() in str(vir).lower()]
    vir_day_parts = [element for element in day_parts if str(element).lower() in str(vir).lower()]
    vir_date_expressions = [element for element in date_expressions if str(element).lower() in str(text).lower()]
    if len(vir_fuzzy_expressions) > 0:
        if len(text.split(',')) > 1 or len(text.split('.')) > 1:
            if len(text.split(',')) > 1:
                parts_text = text.split(',')
            elif len(text.split('.')) > 1:
                parts_text = text.split('.')
            parts_text_time = parts_text[0]
            parts_text_date = parts_text[1].replace(' ', '')
        elif len(vir_date_expressions):
            parts_text = text.lower().split(vir_date_expressions[0])
            parts_text_time = parts_text[0]
            parts_text_date = vir_date_expressions[0]
        else:
            return '', '', '', '', 'time_present_not_contemplated'

        parts = vir.split(vir_fuzzy_expressions[0] + '_REF')
        vir_regularized_date[6] = vir_fuzzy_expressions[0]
        if len(vir_day_parts) > 0:
            if 'T' in vir_day_parts[0]:
                vir_regularized_time[9] = vir_day_parts[0]
            else:
                vir_regularized_time[9] = 'T' + vir_day_parts[0]
        else:
            if 'anchor' in vir:
                parts_time = parts[1].split(')')[1].split(':')
            else:
                parts_time = parts[1].split(':')
            for i, part in enumerate(parts_time):
                vir_regularized_time[i+6] = part.replace('T', '')
        if 'anchor' in vir:
            anchor_parts = re.findall(r'\((.*?)\)', vir)[0].split(',')
            if anchor_parts[1] == 'z' or anchor_parts[1] == 'x':
                vir_regularized_time[3] = 'NEUTRAL'
            elif anchor_parts[1] == '+':
                vir_regularized_time[3] = 'ADD'
            elif anchor_parts[1] == '-':
                vir_regularized_time[3] = 'SUBTRACT'
            if 'DAYW' in anchor_parts[2]:
                vir_regularized_time[4] = 'DAYW'
                vir_regularized_time[5] = anchor_parts[2].split('DAYW')[0]
            elif len(anchor_parts[2]) == 1:
                vir_regularized_time[4] = 0
                vir_regularized_time[5] = anchor_parts[2]
        else:
            vir_regularized_time[3] = 'NEUTRAL'
            vir_regularized_time[4] = 0
            vir_regularized_time[5] = 'D'
    for i, vir_char in enumerate(vir_regularized_time):
        if vir_char == '':
            vir_regularized_time[i] = pad
    for i, vir_char in enumerate(vir_regularized_date):
        if vir_char == '':
            vir_regularized_date[i] = pad
    return parts_text_date, vir_regularized_date, parts_text_time, vir_regularized_time, 'time_present'

import re
def regularize_virs_time(attributes):
    vir_regularized = [''] * 10
    vir = attributes[len(attributes) - 1]
    vir = re.sub(r'T+', 'T', vir)
    rule = ''
    pad = '<pad>'
    millennium_parts = ['KA', 'MA', 'GA']
    year_parts = ['WE', 'SP', 'SU', 'WI', 'FA', 'Q', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'HALF1', 'HALF2']
    day_parts = ['TAF', 'TMO', 'TMI', 'TEV', 'TNI', 'TDT', 'AF', 'MO', 'MI', 'EV', 'NI', 'DT', 'W']
    fuzzy_expressions = ['PRESENT', 'PAST', 'FUTURE']

    if attributes[1] == 'TIME':
        vir_day_parts = [element for element in day_parts if str(element).lower() in str(vir).lower()]
        if '-' in vir and 'Tanchor' in vir and '-,' not in vir and 'Tanchor' in vir:
            parts = vir[0:vir.index('Tanchor')].split('-')
            parts.append(vir[vir.rindex(')') + 1:])
            vir_regularized[0] = parts[0]
            vir_regularized[1] = parts[1]
            vir_regularized[2] = parts[2]
            if parts[3] in vir_day_parts:
                if 'T' in parts[3]:
                    vir_regularized[9] = parts[3]
                else:
                    vir_regularized[9] = 'T' + parts[3]
                rule = 'tanchor_with_date_part_of_day'
            else:
                unit_value = vir[vir.rindex(')') + 1:]
                parts = unit_value.split(':')
                parts[0] = parts[0].replace('T', '')
                for i, part in enumerate(parts):
                    vir_regularized[i+6] = part
                rule = 'tanchor_with_date_time'
        elif 'anchor' in vir:
            unit_value = vir[vir.rindex(')') + 1:]
            anchor_value = vir[vir.index('(') + 1: vir.index(')')].split(',')
            if unit_value in vir_day_parts:
                if 'T' in unit_value:
                    vir_regularized[9] = unit_value
                else:
                    vir_regularized[9] = 'T' + unit_value
                rule = 'tanchor_part_of_day'
            else:
                parts = unit_value.split(':')
                parts[0] = parts[0].replace('T', '')
                for i, part in enumerate(parts):
                    vir_regularized[i+6] = part
                rule = 'tanchor_time'
            if anchor_value[1] == 'z' or anchor_value[1] == 'x':
                vir_regularized[3] = 'NEUTRAL'
            elif anchor_value[1] == '+':
                vir_regularized[3] = 'ADD'
            elif anchor_value[1] == '-':
                vir_regularized[3] = 'SUBTRACT'
            if 'DAYW' in anchor_value[2]:
                vir_regularized[4] = 'DAYW'
                vir_regularized[5] = anchor_value[2].split('DAYW')[0]
            elif len(anchor_value[2]) == 1:
                vir_regularized[4] = 0
                vir_regularized[5] = anchor_value[2]
            else:
                vir_regularized[4] = anchor_value[2][0:len(anchor_value[2]) - 1]
                vir_regularized[5] = anchor_value[2][len(anchor_value[2]) - 1]
        elif '-' in vir:
            date_parts = re.split(r'-', vir)
            time_part = re.split(r'T', date_parts[2])[1]
            date_parts[2] = re.split(r'T', date_parts[2])[0]
            vir_regularized[0] = date_parts[0]
            vir_regularized[1] = date_parts[1]
            vir_regularized[2] = date_parts[2]
            parts = re.split(r':', time_part)
            for i, part in enumerate(parts):
                vir_regularized[i + 6] = parts[i]
            rule = 'date_time'
        elif ':' in vir:
            parts = re.split(r':', vir)
            if re.split(r'T', parts[0])[0] != '':
                rule = 'time_as_year'
            elif len(parts) == 1:
                vir_regularized[0] = parts[0].replace('T', '')
                rule = 'hour'
            elif len(parts) == 2:
                vir_regularized[6] = parts[0].replace('T', '')
                vir_regularized[7] = parts[1]
                rule = 'hour_minute'
            elif len(parts) == 3:
                vir_regularized[6] = parts[0].replace('T', '')
                vir_regularized[7] = parts[1]
                vir_regularized[8] = parts[2]
                rule = 'hour_minute_second'
            else:
                rule = 'unrecognized_hour_minute_second_format'
        elif vir.count('T') == 1 and re.search(r'^T\d+', vir):
            vir_regularized[6] = vir.replace('T', '')
            rule = 'hour'
        elif vir == 'null':
            rule = 'vir_null'
        else:
            rule = 'vir_no_pattern'
    for i, vir_char in enumerate(vir_regularized):
        if vir_char == '':
            vir_regularized[i] = pad
    return vir_regularized, rule



#Regulariza los CIRs con expresiones regulares en vez de con ifs
def regularize_virs_duration(attributes):
    pad = '<pad>'
    vir_regularized = [""] * 8
    vir = attributes[len(attributes) - 1]
    year_parts = ['WE', 'SP', 'SU', 'WI', 'FA', 'Q', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9']
    hour_parts = ['TAF', 'TMO', 'TEV', 'NI', 'TDT']
    duration_set_parts = ['Y', 'M', 'D', 'H', 'MIN', 'S', 'W']
    rule = ''
    values = []
    units = []
    if attributes[1] == 'DURATION':
        vir_year_parts = [element for element in year_parts if str(element).lower() in str(vir).lower()]
        vir_hour_parts = [element for element in hour_parts if str(element).lower() in str(vir).lower()]
        vir_duration_set_parts = [element for element in duration_set_parts if str(element).lower() in str(vir).lower()]
        vir = vir.replace('P', '')
        if vir == '':
            rule = 'vir_empty'
        elif 'Ranchor' in vir:
            vir = vir.replace('Ranchor(', '').replace(')', '')
            parts = re.split(r',', vir)
            if parts[1].lower() == 'y' or parts[1].lower() == 'm':
                vir_regularized[1] = parts[1].upper()
                if parts[0] == '+':
                    vir_regularized[0] = 'ADD'
                    rule = 'ranchor_add'
                elif parts[0] == '-':
                    vir_regularized[0] = 'SUBTRACT'
                    rule = 'ranchor_subtract'
            else:
                rule = 'ranchor_bad_unit'
        elif len(vir_year_parts) > 0 or re.search(r'^((\d+(\.?\d+)?)|X)+T$', vir) or re.search(r'^((\d+(\.?\d+)?)|X)+HALF$', vir):
            vir_year_parts_aux = copy.deepcopy(vir_year_parts)
            vir_year_parts_aux.append('T')
            vir_year_parts_aux.append('HALF')
            if '-' not in vir:
                for part in vir_year_parts_aux:
                    parts = re.split(fr'({part})', vir)
                    if len(parts) > 1:
                        break
                values = [parts[0]]
                units = [parts[1]]
                rule = 'part_of_year_duration_format'
            else:
                parts = re.split(r'^(\d+|X+|X+\d+)-', vir)
                values = [parts[1]]
                units = [parts[2]]
                rule = 'part_of_year_date_format'
        elif len(vir_hour_parts) > 0 or re.search(r'^((\d+.?\d+)|X)+TMI$', vir):
            vir_hour_parts_aux = copy.deepcopy(vir_hour_parts)
            vir_hour_parts_aux.append('TMI')
            if '-' not in vir:
                for part in vir_hour_parts_aux:
                    parts = re.split(fr'({part})', vir)
                    if len(parts) > 1:
                        break
                values = [parts[0]]
                if parts[1] == 'NI':
                    units = ['T' + parts[1]]
                else:
                    units = [parts[1]]
                rule = 'part_of_hour_duration_format'
            else:
                parts = vir.split('-')
                for part in vir_hour_parts_aux:
                    parts_unit = re.split(fr'({part})', parts[len(parts)-1])
                    if len(parts) > 1:
                        break
                if re.search(r'^(\d+|X+|X+\d+)-(\d\d|XX)-(\d\d|XX)', vir):
                    values = [parts[0], parts[1], parts_unit[0]]
                    if parts_unit[1] == 'NI':
                        units = ['T' + parts_unit[1]]
                    else:
                        units = [parts_unit[1]]
                    rule = 'part_of_hour_full_date_format'
                if re.search(r'^(\d+|X+|X+\d+)-(W\d\d|WXX)-(\d|X)', vir):
                    values = [parts[0], parts[1].split('W')[1], parts_unit[0]]
                    if parts_unit[1] == 'NI':
                        units = ['T' + parts_unit[1]]
                    else:
                        units = [parts_unit[1]]
                    rule = 'part_of_hour_week_date_format'
        elif len(vir_duration_set_parts) > 0:
            flag_t = False
            characters = [char for char in vir]
            before_unit = False
            for character in characters:
                if str.isdigit(character) or character == 'X':
                    if len(units) == len(values):
                        values.append('')
                    values[len(units)] += character.lower()
                    before_unit = False
                else:
                    if character == 'T':
                        flag_t = True
                    if flag_t == True and character == 'M':
                        units.append('MIN')
                        if character != 'M':
                            flag_t = False
                    elif character == '.':
                        values[len(units)] += character
                    elif before_unit:
                        units[len(units) - 1] += character
                    else:
                        if character != 'P' and character != 'T':
                            units.append(character)
                            before_unit = True
            rule = 'normal_duration_format'
            #El resultado son dos listas de misma longitud, formando pares [unidad, valor]
        else:
            rule = 'vir_no_pattern'
        for value, unit in zip(values, units):
            if unit == 'Y':
                vir_regularized[0] = value
            elif unit == 'M':
                vir_regularized[1] = value
            elif unit == 'W':
                vir_regularized[2] = value
            elif unit == 'D':
                vir_regularized[3] = value
            elif unit == 'H':
                vir_regularized[4] = value
            elif unit == 'MIN':
                vir_regularized[5] = value
            elif unit == 'S':
                vir_regularized[6] = value
            elif unit in year_parts or unit == 'T' or unit == 'T1' or unit == 'T2' or unit == 'T3' or unit == 'HALF' or unit == 'HALF1' or unit == 'HALF2':
                if '-' in vir:
                    vir_regularized[0] = value
                    vir_regularized[7] = unit
                else:
                    vir_regularized[1] = value
                    vir_regularized[7] = unit
            elif unit in hour_parts or unit == 'TMI' or unit == 'TNI':
                if 'W' in vir:
                    vir_regularized[0] = values[0]
                    vir_regularized[2] = values[1]
                    vir_regularized[4] = values[2]
                    vir_regularized[7] = units[0]
                elif str.count(vir, '-') == 2:
                    vir_regularized[0] = values[0]
                    vir_regularized[1] = values[1]
                    vir_regularized[3] = values[2]
                    vir_regularized[7] = units[0]
                else:
                    vir_regularized[4] = value
                    vir_regularized[7] = unit
            else:
                rule = 'unit_no_pattern'
        for i, vir_char in enumerate(vir_regularized):
            if vir_char == '':
                vir_regularized[i] = pad
        return vir_regularized, rule



#Regulariza los CIRs con expresiones regulares en vez de con ifs
import re
import copy
def regularize_virs_set(attributes):
    pad = '<pad>'
    vir_regularized = [""] * 8
    vir = attributes[len(attributes) - 1]
    year_parts = ['WE', '-W', 'SP', 'SU', 'WI', 'FA', 'Q', 'Q1', 'Q2', 'Q3', 'Q4']
    hour_parts = ['AF', 'MO', 'EV', 'NI', 'DT', 'TAF', 'TMO', 'TEV', 'TNI', 'TDT']
    duration_set_parts = ['Y', 'M', 'D', 'H', 'MIN', 'S', 'W']
    rule = ''
    values = []
    units = []
    if attributes[1] == 'SET':
        vir_year_parts = [element for element in year_parts if str(element).lower() in str(vir).lower()]
        vir_hour_parts = [element for element in hour_parts if str(element).lower() in str(vir).lower()]
        vir_duration_set_parts = [element for element in duration_set_parts if str(element).lower() in str(vir).lower()]
        if len(vir_year_parts) > 0 or re.search(r'^((\d+(\.?\d+)?)|X)+T$', vir) or re.search(r'^((\d+(\.?\d+)?)|X)+HALF$', vir):
            vir_year_parts_aux = copy.deepcopy(vir_year_parts)
            vir_year_parts_aux.append('T')
            vir_year_parts_aux.append('HALF')
            if '-' not in vir:
                for part in vir_year_parts_aux:
                    parts = re.split(fr'({part})', vir)
                    if len(parts) > 1:
                        break
                digits = re.findall(r'\d+', parts[0])
                digits_combined = ''.join(digits)
                values = digits_combined
                units = [parts[1]]
                rule = 'part_of_year_duration_format'
            else:
                parts = re.split(r'^(\d+|X+|X+\d+)-', vir)
                if 'WE' in parts[2]:
                    parts = re.split(r'-', vir)
                    year_we = parts[0]
                    week_we = parts[1].lower().replace('w', '').upper()
                    values = [parts[1]]
                    units = [parts[2]]
                elif 'W' in parts[2]:
                    parts = re.split(r'-', vir)
                    year_we = parts[0]
                    week_we = parts[1].lower().replace('w', '').upper()
                    if len(parts) == 3:
                        day = parts[2]
                    else:
                        day = ''
                    values = [parts[1]]
                    units = ['-W']
                else:
                    values = [parts[1]]
                    units = [parts[2]]
        elif len(vir_hour_parts) > 0 or re.search(r'^((\d+.?\d+)|X)+TMI$', vir):
            vir_hour_parts_aux = copy.deepcopy(vir_hour_parts)
            vir_hour_parts_aux.append('TMI')
            if '-' not in vir:
                for part in vir_hour_parts_aux:
                    parts = re.split(fr'({part})', vir)
                    if len(parts) > 1:
                        break
                if parts[0] == 'PT' or parts[0] == 'P':
                    values = [0]
                else:
                    digits = re.findall(r'\d+', parts[0])
                    digits_combined = ''.join(digits)
                    values = digits_combined
                if 'T' in parts[1]:
                    units = [parts[1]]
                else:
                    units = ['T' + parts[1]]
                rule = 'part_of_hour_duration_format'
            else:
                parts = vir.split('-')
                for part in vir_hour_parts_aux:
                    parts_unit = re.split(fr'({part})', parts[len(parts)-1])
                    if len(parts) > 1:
                        break
                if re.search(r'^(\d+|X+|X+\d+)-(\d\d|XX)-(\d\d|XX)', vir):
                    values = [parts[0], parts[1], parts_unit[0].replace('T', '')]
                    if parts_unit[1] == 'NI':
                        units = ['T' + parts_unit[1]]
                    else:
                        units = [parts_unit[1]]
                    rule = 'part_of_hour_full_date_format'
                if re.search(r'^(\d+|X+|X+\d+)-(W\d\d|WXX)-(\d|X)', vir):
                    values = [parts[0], parts[1].split('W')[1], parts_unit[0].replace('T', '')]
                    if parts_unit[1] == 'NI':
                        units = ['T' + parts_unit[1]]
                    else:
                        units = ['T' + parts_unit[1]]
                    rule = 'part_of_hour_week_date_format'
        elif len(vir_duration_set_parts) > 0:
            vir = vir.replace('PT', '')
            if vir[0] == 'X':
                values.append(vir[0])
                units.append(vir[1:])
            else:
                characters = [char for char in vir]
                before_unit = False
                for character in characters:
                    if str.isdigit(character):
                        if len(units) == len(values):
                            values.append('')
                        values[len(units)] += character
                        before_unit = False
                    else:
                        if character == '.':
                            values[len(units)] += character
                        elif before_unit:
                            units[len(units) - 1] += character
                        else:
                            if character != 'P' and character != 'T':
                                units.append(character)
                                before_unit = True
            rule = 'normal_duration_format'
        else:
            rule = 'vir_no_pattern'
        for value, unit in zip(values, units):
            if unit == 'Y':
                vir_regularized[0] = value
            elif unit == 'M':
                vir_regularized[1] = value
            elif unit == 'W':
                vir_regularized[2] = value
            elif unit == 'D':
                vir_regularized[3] = value
            elif unit == 'H':
                vir_regularized[4] = value
            elif unit == 'MIN':
                vir_regularized[5] = value
            elif unit == 'S':
                vir_regularized[6] = value
            elif unit in year_parts or unit == 'T' or unit == 'T1' or unit == 'T2' or unit == 'T3' or unit == 'HALF' or unit == 'HALF1' or unit == 'HALF2':
                if 'we' in unit.lower():
                    vir_regularized[0] = year_we
                    vir_regularized[2] = week_we
                    vir_regularized[7] = 'WE'
                elif 'w' in unit.lower():
                    vir_regularized[0] = year_we
                    vir_regularized[2] = week_we
                    if day != '':
                        vir_regularized[7] = day
                elif '-' in vir:
                    vir_regularized[0] = value
                    vir_regularized[7] = unit
                else:
                    vir_regularized[1] = value
                    vir_regularized[7] = unit
            elif unit in hour_parts or unit == 'TMI' or unit == 'TNI':
                if 'W' in vir:
                    vir_regularized[0] = values[0]
                    vir_regularized[2] = values[1]
                    vir_regularized[2] = values[2]
                    vir_regularized[7] = units[0]
                elif str.count(vir, '-') == 2:
                    vir_regularized[0] = values[0]
                    vir_regularized[1] = values[1]
                    vir_regularized[3] = values[2]
                    vir_regularized[7] = units[0]
                else:
                    vir_regularized[2] = value
                    vir_regularized[7] = unit
            else:
                rule = 'unit_no_pattern'
        for i, vir_char in enumerate(vir_regularized):
            if vir_char == '':
                vir_regularized[i] = pad
        return vir_regularized, rule
    
        
def regularize_timex_files(path_org):
    filename_csv_text = 'corpus_plain_text.csv'
    fields = ['File', 'String']
    create_csv(filename_csv_text, fields)
    
    filename_csv_expression_list = 'expressions_list.csv'
    fields = ['File', 'id', 'Type', 'Value', 'VIR', 'String', 'Explicit', 'Rule', 'VIR_regularized']
    create_csv(filename_csv_expression_list, fields)
    
    filename_csv_no_rule = 'expressions_list_no_rule.csv'
    fields = ['File', 'id', 'Type', 'Value', 'CIR', 'String', 'Explicit', 'Rule', 'CIR_regularizado']
    create_csv(filename_csv_no_rule, fields)
    

    filename_csv_problems = 'malformed_files.csv'
    fields = ['file', 'expression', 'exception']
    pad = '<pad>'
    all_files = os.listdir(path_org)
    count_flag_date_time = 0
    with tqdm(total=len(all_files)) as pbar: 
        for filename in all_files:
            try:
                if filename != '.DS_Store':
                    file_text = open(path_org + '/' + filename, 'r',).read()
                    file_text_vir_regularized = copy.deepcopy(file_text)
                    expressions = re.findall(r'\<TIMEX3.*?\</TIMEX3\>', file_text)
                    attributes_expressions = []
                    attributes_expressions_no_rule = []
                    for expression in expressions:
                        flag_date_time = False
                        splitted_expression = expression.replace('>', '> ').replace('<', ' <').split()
                        attributes = re.findall(r'".*?"', expression)
                        attributes = list(map(lambda x: x.replace('"', ''), attributes))
                        type_ = attributes[1]
                        if len(attributes) > 4:
                            attributes.pop(3)
                            expression_text_list = splitted_expression[6:len(splitted_expression)-1]
                        else:
                            expression_text_list = splitted_expression[5:len(splitted_expression)-1]
                        expression_text = ' '.join(expression_text_list)
                        if type_ == 'DATE':
                            vir_regularized, rule = regularize_virs_date(attributes)
                        elif type_ == 'TIME':
                            if 'PRESENT' in attributes[2] or 'PAST' in attributes[2] or 'FUTURE' in attributes[2]:
                                parts_text_date, vir_regularized_date, parts_text_time, vir_regularized_time, rule = regularize_virs_time_present(attributes, expression_text)
                                flag_date_time = True
                                count_flag_date_time += 1
                            else:
                                vir_regularized, rule = regularize_virs_time(attributes)
                        elif type_ == 'DURATION':
                            vir_regularized, rule = regularize_virs_duration(attributes)
                        elif type_ == 'SET':
                            vir_regularized, rule = regularize_virs_set(attributes)
                        else:
                            print('SET IMPOSTOR')
                        if flag_date_time:
                            tag_vir_regularized_time = "<" + type_ + ' ' + parts_text_time
                            vir_regularized_time_concat = ''
                            flag = False
                            for x in vir_regularized_time:
                                if x == pad:
                                    flag = False
                                    vir_regularized_time_concat += str(x)
                                else:
                                    if flag:
                                        vir_regularized_time_concat += ' ' + str(x)    
                                    else:
                                        flag = True
                                        vir_regularized_time_concat += str(x)
                            tag_vir_regularized_time += ' ' + vir_regularized_time_concat + '>'
                            tag_vir_regularized_date = "<" + type_ + ' ' + parts_text_date
                            vir_regularized_date_concat = ''
                            flag = False
                            for x in vir_regularized_date:
                                if x == pad:
                                    flag = False
                                    vir_regularized_date_concat += str(x)
                                else:
                                    if flag:
                                        vir_regularized_date_concat += ' ' + str(x)    
                                    else:
                                        flag = True
                                        vir_regularized_date_concat += str(x)
                            tag_vir_regularized_date += ' ' + vir_regularized_date_concat + '>'
                            tag_vir_regularized = tag_vir_regularized_time + ' ' + tag_vir_regularized_date
                            file_text_vir_regularized = file_text_vir_regularized.replace(expression, tag_vir_regularized)
                            attributes_time = [filename, count_flag_date_time+9999, 'TIME', 'T'+attributes[2].split('_REF')[1].replace('TT', 'T'), 'T'+attributes[2].split('_REF')[1].replace('TT', 'T'), parts_text_time, 'implicit', rule, vir_regularized_time_concat]
                            attributes_date = [filename, count_flag_date_time+9999, 'DATE', attributes[2].split('_REF')[0] + '_REF', attributes[2].split('_REF')[0] + '_REF', parts_text_date, 'implicit', rule, vir_regularized_date_concat]
                            attributes_expressions.append(attributes_time)
                            attributes_expressions.append(attributes_date)
                        else:
                            if 'NI' in attributes[3]:
                                attributes[3].replace('NI', 'TNI')
                            attributes.append(expression_text)
                            attributes.insert(0, filename)
                            if 'anchor' in attributes[4]:
                                attributes.append('implicit')
                            else:
                                attributes.append('explicit')
                            attributes.append(rule)
                            tag_vir_regularized = "<" + attributes[2] + ' ' + attributes[5]
                            vir_regularized_concat = ''
                            flag = False
                            for x in vir_regularized:
                                if x == pad:
                                    flag = False
                                    vir_regularized_concat += str(x)
                                else:
                                    if flag:
                                        vir_regularized_concat += ' ' + str(x)    
                                    else:
                                        flag = True
                                        vir_regularized_concat += str(x)
                            tag_vir_regularized += ' ' + vir_regularized_concat + '>'
                            if all(map(lambda x: x == pad, vir_regularized)):
                                file_text_vir_regularized = file_text_vir_regularized.replace(expression, expression_text)
                                attributes.append(vir_regularized_concat)
                                attributes_expressions_no_rule.append(attributes)
                            else:
                                file_text_vir_regularized = file_text_vir_regularized.replace(expression, tag_vir_regularized)
                                attributes.append(vir_regularized_concat)
                                attributes_expressions.append(attributes)
                    fields = ['File', 'String']
                    df_file = pd.DataFrame([[filename, file_text_vir_regularized]], columns=fields)
                    df_file.to_csv(filename_csv_text, mode = 'a', index = False, header=False)
                    fields = ['File', 'id', 'Type', 'Value', 'VIR', 'String', 'Explicit', 'Rule', 'VIR_regularized']
                    df_file = pd.DataFrame(attributes_expressions, columns=fields)
                    df_file.to_csv(filename_csv_expression_list, mode = 'a', index = False, header=False)
                    if len(attributes_expressions_no_rule) > 0:
                        df_file = pd.DataFrame(attributes_expressions_no_rule, columns=fields)
                        df_file.to_csv(filename_csv_no_rule, mode = 'a', index = False, header=False)
                pbar.update()
            except Exception as e:
                print(e)
                df_file = pd.DataFrame([[filename, expression, e]], columns=['file', 'expression', 'exception'])
                df_file.to_csv(filename_csv_problems, mode = 'a', index = False, header=False)
                pbar.update()
            
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regularize TIMEX files in a directory.")
    parser.add_argument('--path_org', type=str, required=True, help='Path to the directory containing the original TIMEX files.')
    args = parser.parse_args()
    regularize_timex_files(args.path_org)
            
            
