def desregularizar(type, vir):
    import re
    import copy
    vir_desregularizado = ''
    if type.lower() == 'date':
        vir_desregularizado = desregularizar_cirs_date(vir)
    elif type.lower() == 'time':
        vir_desregularizado = desregularizar_cirs_time(vir)
    elif type.lower() == 'duration':
        vir_desregularizado = desregularizar_cirs_duration(vir)
    elif type.lower() == 'set':
        vir_desregularizado = desregularizar_cirs_set(vir)
    print(vir_desregularizado)
    return vir_desregularizado

def desregularizar_cirs_date(cir):
    import re
    import copy
    try:
        cir_desregularizado = ''
        regla = ''
        pad = 'pad'
        fuzzy = ['present', 'past',  'future']
        operaciones = ['suma', 'resta', 'neutro']
        estaciones = ['wi', 'su',  'sp', 'fa']
        anchor = ['y', 'm', 'w', 'we', 'd', 'q', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 't', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 'half', 'half1', 'half2', 'dayw']
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

        #Format -> year | month | week | day | operation | operating value | operating unit (Can be months, days, stations, etc.) / date unit WE/SP/SU/WI/FA/Q/T/H/FA / AF/MO/MI/EV/NI/DT / Fuzzy Future/Present/Past | century | decade)
        cir_slots = re.split(r'[<> ]', cir) 
        cir_slots = list(filter(lambda s: s != '', cir_slots))
        cir_slots = [i.lower() for i in cir_slots]
        
        #DWanchor
        if ('months' in cir_slots and cir_slots[1]==pad):
            cir_desregularizado = 'DWanchor('
            if 'resta' in cir_slots:
                cir_desregularizado += '-,'
                regla = 'dwanchor_resta'
            elif 'suma' in cir_slots:
                cir_desregularizado += '+,'
                regla = 'dwanchor_resta'
            if cir_slots[1]!=pad:
                cir_desregularizado += str(cir_slots[1]) + 'MONTHS)'
            else:
                cir_desregularizado += str(cir_slots[5]) + 'MONTHS)'
        
        #Sanchor
        elif cir_slots[6] in estaciones and cir_slots[4] in operaciones:
            if cir_slots[4] == 'resta':
                cir_desregularizado += 'Sanchor(-,'
                regla = 'sanchor_resta'
            elif cir_slots[4] == 'suma':
                cir_desregularizado += 'Sanchor(+,'
                regla = 'sanchor_suma'

            cir_desregularizado += 'XXXX' + '-' + cir_slots[6].upper() + ')'
            if cir_slots[0] != pad:
                cir_desregularizado = cir_slots[0] + '-' + cir_slots[6].upper()
        
        #Danchor
        elif ((cir_slots[0].isdigit() or cir_slots[1].isdigit() or cir_slots[2].isdigit() or cir_slots[3].isdigit() or cir_slots[4].isdigit()) and (cir_slots[4] in operaciones or re.split(r'\d',cir_slots[3])[-1] in operaciones)):# or (re.split(r'\d',cir_slots[3])[-1] in operaciones):
            cir_desregularizado = 'Danchor('
            if cir_slots[1].isdigit() and cir_slots[2].isdigit(): #Month and Week
                cir_desregularizado = ''
                rule = 'danchor_month_week'
            else:
                if re.split(r'\d',cir_slots[3])[-1] in operaciones:
                    if re.split(r'\d',cir_slots[3])[-1].lower() == 'resta':
                        cir_desregularizado += '-,'
                        regla = 'danchor_subtraction'
                    elif re.split(r'\d',cir_slots[3])[-1].lower() == 'suma':
                        cir_desregularizado += '+,'
                        regla = 'danchor_addition'
                    else:
                        cir_desregularizado += 'x,'
                        regla = 'danchor_neutral'
                    if cir_slots[0].isdigit() == False:
                        cir_desregularizado += 'XXXX'
                    else:#Year
                        cir_desregularizado += cir_slots[0]
                    if  cir_slots[1].isdigit():#Month
                        if cir_slots[1] in numbers: 
                            cir_slots[1] = '0' + cir_slots[1]
                        cir_desregularizado += '-' + cir_slots[1]
                    else:
                        cir_desregularizado += '-' + 'XX'
                    if  cir_slots[2].isdigit():#Week
                        cir_desregularizado += '-' + cir_slots[2] + 'W'
                    
                    operacion_aux = operaciones.index(re.split(r'\d', cir_slots[3])[-1])
                    dia = re.split(operaciones[operacion_aux], cir_slots[3])[0]
                    if dia in numbers:
                        dia = '0' + dia
                    cir_desregularizado += '-' + dia
                else:
                    if cir_slots[4] == 'resta':
                        cir_desregularizado += '-,'
                        regla = 'danchor_subtraction'
                    elif cir_slots[4] == 'suma':
                        cir_desregularizado += '+,'
                        regla = 'danchor_addition'
                    else:
                        cir_desregularizado += 'x,'
                        regla = 'danchor_neutral'
                    
                    if cir_slots[0].isdigit() == False:
                        cir_desregularizado += 'XXXX'
                    else:#Year
                        cir_desregularizado += cir_slots[0]
                    if  cir_slots[1].isdigit():#Month
                        if cir_slots[1] in numbers:
                            cir_slots[1] = '0' + cir_slots[1]
                        cir_desregularizado += '-' + cir_slots[1]
                    else:
                        cir_desregularizado += '-' + 'XX'
                    if  cir_slots[2].isdigit():#Week
                        cir_desregularizado += '-' + cir_slots[2] + 'W'
                    if  cir_slots[3].isdigit():#Day
                        if cir_slots[3] in numbers:
                            cir_slots[3] = '0' + cir_slots[3]
                        cir_desregularizado += '-' + cir_slots[3]
                

                cir_desregularizado += ')'

        #Anchor
        elif (cir_slots[6] in anchor and cir_slots[4] in operaciones) or 'dayw' in cir_slots[5]:
            if cir_slots[5].isdigit() or 'dayw' in cir_slots[5]:
                if cir_slots[4] == 'resta':
                    if 'dayw' in cir_slots[5]:
                        number = cir_slots[5].strip('dayw')[0]
                        cir_desregularizado += 'anchor(TODAY,-,' + number + 'DAYW' + ')'
                        regla = 'anchor_subtraction_dayw'
                    elif 'dayw' in cir_slots[6]:
                        cir_desregularizado += 'anchor(TODAY,-,' + cir_slots[5].upper() + cir_slots[6].upper() + ')'
                        regla = 'anchor_subtraction_dayw'
                    else:
                        cir_desregularizado += 'anchor(TODAY,-,' + cir_slots[5].upper() + cir_slots[6].upper() + ')'
                        regla = 'anchor_subtractino'
                elif cir_slots[4] == 'suma': 
                    if 'dayw' in cir_slots[5]:
                        number = cir_slots[5].strip('dayw')[0]
                        cir_desregularizado += 'anchor(TODAY,+,' + number + 'DAYW' + ')'
                        regla = 'anchor_addition_dayw'
                    elif 'dayw' in cir_slots[6]:
                        cir_desregularizado += 'anchor(TODAY,+,' + cir_slots[5].upper() + cir_slots[6].upper() + ')'
                        regla = 'anchor_addition_dayw'
                    else:
                        cir_desregularizado += 'anchor(TODAY,+,' + cir_slots[5].upper() + cir_slots[6].upper() + ')'
                        regla = 'anchor_addition'
                elif cir_slots[4] == 'neutro': 
                    if 'dayw' in cir_slots[5]:
                        number = cir_slots[5].strip('dayw')[0]
                        cir_desregularizado += 'anchor(TODAY,z,' + number + 'DAYW' + ')'
                        regla = 'anchor_neutral_dayw'
                    elif 'dayw' in cir_slots[6]:
                        cir_desregularizado += 'anchor(TODAY,z,' + cir_slots[5].upper() + cir_slots[6].upper() + ')'
                        regla = 'anchor_neutral_dayw'
                    else:
                        regla = 'anchor_neutral'
                        cir_desregularizado += 'anchor(TODAY,x,' + cir_slots[6].upper() + ')'
            else:
                regla = 'sin_patron'
                cir_desregularizado = ''
                    
        #Regular Date
        elif cir_slots[0] != pad or cir_slots[1] != pad or cir_slots[2] != pad or cir_slots[3] != pad or cir_slots[6] != pad:
            if cir_slots[0] != pad: #Year
                cir_desregularizado += str(cir_slots[0]).upper()
            else:
                if cir_slots[1] == pad and cir_slots[2] != pad and cir_slots[3] == pad:
                    False
                else:
                    cir_desregularizado += 'XXXX'
            if cir_slots[1] != pad: #Month
                cir_desregularizado += '-' + str(cir_slots[1]).upper()
            else:
                if cir_slots[1] == pad and cir_slots[2] != pad and cir_slots[3] == pad:
                    False
                elif cir_slots[2] == pad:
                    cir_desregularizado += '-XX'
            if cir_slots[2] != pad: #Week
                if cir_slots[1] != pad:
                    cir_desregularizado = ''
                elif cir_slots[3] == pad:
                    cir_desregularizado += cir_slots[2].upper()+'WE'
                elif cir_slots[3] != pad:
                    cir_desregularizado += '-W' + cir_slots[2].upper()
                else:
                    cir_desregularizado += str(cir_slots[2]).upper()
            if cir_slots[3] != pad: #Day
                cir_desregularizado += '-' + str(cir_slots[3]).upper()
            else:
                if cir_slots[1] == pad and cir_slots[2] != pad and cir_slots[3] == pad:
                    False
                if cir_slots[1] == pad and cir_slots[2] == pad:
                    if cir_slots[0] != pad:
                        cir_desregularizado = str(cir_slots[0]).upper()
                    else:
                        cir_desregularizado = 'XXXX'
                if cir_slots[0] != pad and cir_slots[1] != pad:
                    cir_desregularizado += '-XX'
            regla = 'date_normal'
            if cir_slots[6] != pad and cir_slots[6] not in fuzzy:
                if 'months' not in cir_slots[6] and 'dayw' not in cir_slots[6]:
                    cir_desregularizado += '-' + str(cir_slots[6]).upper()
                    regla = 'date_normal'
            #Fuzzy 
            elif cir_slots[6] in fuzzy:
                cir_desregularizado = str(cir_slots[6]).upper() + '_REF'
                regla = 'fuzzy'

        #Century Decade
        elif cir_slots[7] != pad or cir_slots[8] != pad:
            if cir_slots[7] != pad:
                cir_desregularizado += str(int(cir_slots[7])-1)
            else:
                cir_desregularizado += 'XX'
            if cir_slots[8] != pad:
                cir_desregularizado +=  str(cir_slots[8]).replace('0', '')
            regla = 'century_decade'
        
        else:
            regla = 'no_pattern'

        return cir_desregularizado
    except Exception as e:
        return e

def desregularizar_cirs_time(cir):
    import re
    import copy
    try:
        cir_desregularizado = ''
        regla = ''
        pad = 'pad'
        fuzzy = ['present', 'past',  'future']
        operaciones = ['suma', 'resta', 'neutro']
        estaciones = ['wi', 'su',  'sp', 'fa']
        anchor = ['y', 'm', 'w', 'd', 'q', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 'half1', 'half2', 'dayw']
        
        #Format -> year | month | day | operation | operating value | operating unit | hour | minute | second | hour unit AF/MO/MI/EV/NI/DT
        cir_slots = re.split(r'[<> ]', cir) 
        cir_slots = list(filter(lambda s: s != '', cir_slots))
        cir_slots = [i.lower() for i in cir_slots]
        
        #Anchor
        if cir_slots[5] in anchor:
            if cir_slots[3] == 'resta':
                cir_desregularizado  += 'anchor(TODAY,-,' + cir_slots[4].upper() + cir_slots[5].upper() + ')'
                regla = 'anchor_subtraction'
            elif cir_slots[3] == 'suma': 
                cir_desregularizado += 'anchor(TODAY,+,' + cir_slots[4].upper() + cir_slots[5].upper() + ')'
                regla = 'anchor_addition'
            elif cir_slots[3] == 'neutro':
                if cir_slots[5] == 'dayw':
                    cir_desregularizado += 'anchor(TODAY,z,' + cir_slots[4].upper() + cir_slots[5].upper() + ')'
                    regla = 'anchor_neutral_dayw'
                else:
                    regla = 'anchor_neutral'
                    cir_desregularizado += 'anchor(TODAY,x,' + cir_slots[5].upper() + ')'
        #Date
        if cir_slots[0] != pad or cir_slots[1] != pad or cir_slots[2] != pad:
            if cir_slots[0] != pad: #Year
                cir_desregularizado += cir_slots[0].upper() #Puede ser xx
                regla += '_year'
            if cir_slots[1] != pad: #Month
                if cir_slots[0] == pad:
                    cir_desregularizado = ''
                    regla = 'month_without_year'
                else:
                    cir_desregularizado += '-' + cir_slots[1].upper()
                    regla += '_month'
            if cir_slots[2] != pad: #Day
                if cir_slots[1] == pad or cir_slots[0] == pad:
                    cir_desregularizado = ''
                    regla = 'day_without_year_or_month'
                else:
                    cir_desregularizado += '-' + cir_slots[2].upper()
                    regla += '_day'

        #Hour anchor
        if cir_slots[6] != pad or cir_slots[7] != pad or cir_slots[8] != pad:
            cir_desregularizado += 'T' 
            if cir_slots[6] != pad: #Hour
                cir_desregularizado += cir_slots[6]
                regla += '_hour'
            if cir_slots[7] != pad: #Minute
                if cir_slots[6] == pad:
                    cir_desregularizado = ''
                    regla = 'minute_without_hour'
                else:
                    cir_desregularizado += ':' + cir_slots[7]
                    regla += '_Minute'
            if cir_slots[8] != pad: #Second
                if cir_slots[7] == pad or cir_slots[6] == pad:
                    cir_desregularizado = ''
                    regla = 'second_without_hour_or_minute'
                else:
                    cir_desregularizado += ':' + cir_slots[8]
                    regla += '_second'
        
        #Fuzzy
        if cir_slots[7] in fuzzy:
            cir_desregularizado = str(cir_slots[7]).upper() + '_REF'
            regla = 'fuzzy'
        
        #Part of Day
        if cir_slots[9] != pad: 
            if cir_slots[6] != pad or cir_slots[7] != pad or cir_slots[8] != pad:
                cir_desregularizado = ''
                regla = 'part_of_day_with_hour_min_sec'
            elif 't' in cir_slots[9]:
                cir_desregularizado += cir_slots[9].upper()
                regla += '_part_of_day'
            else:
                cir_desregularizado += cir_slots[9].upper()
        
        return cir_desregularizado
    except Exception as e:
        return ''

def desregularizar_cirs_duration(cir):
    import re
    import copy
    try:
        cir_desregularizado = ''
        regla = ''
        pad = 'pad'
        parte_de_anio = ['wi', 'su',  'sp', 'fa', 'q', 't', 'half', 'we']
        partes_de_dia = ['taf','tmo','tmi','tev','ni','tni','tdt','w']
        operaciones = ['suma', 'resta', 'neutro']

        #Longitud = 8 -> Year | Month/X(stations, etc.) | Week(W)value | Day | Hour/X(of evenings, etc.) | Minute | Second | WE/SP/SU/WI/FA/Q/T/H/FA / AF/MO/MI/EV/NI/DT
        cir_slots = re.split(r'[<> ]', cir) 
        cir_slots = list(filter(lambda s: s != '', cir_slots))
        cir_slots = [i.lower() for i in cir_slots]
        for i, slot in enumerate(cir_slots[1:]):
            for operacion in operaciones:
                if operacion in slot:
                    if slot == operacion:
                        cir_slots[i+1] = pad
                    else:
                        cir_slots[i+1] = cir_slots[i+1].replace(operacion, '')
                
        if cir_slots[0] != pad: #Year
            if cir_slots[0].lower() == 'suma':
                cir_desregularizado += 'Ranchor(+,' 
            elif cir_slots[0].lower() == 'resta': 
                cir_desregularizado += 'Ranchor(-,'
            else:    
                cir_desregularizado += cir_slots[0].upper() + 'Y'
            regla += 'year'
        if cir_slots[1] != pad: 
            if cir_slots[0].lower() == 'suma' or cir_slots[0].lower() == 'resta':
                cir_desregularizado += cir_slots[1].upper() + ')' 
            elif cir_slots[7].lower() in parte_de_anio:
                cir_desregularizado += cir_slots[1].upper() + cir_slots[7].upper()
                regla = 'part_of_year'
            else: #Month
                cir_desregularizado += cir_slots[1].upper() + 'M'
                if regla != '':
                    regla += '_month'
                else:
                    regla += 'month'
        if cir_slots[2] != pad: #Week
            cir_desregularizado += cir_slots[2].upper() + 'W'
            if regla != '':
                regla += '_week'
            else:
                regla += 'week'
        if cir_slots[3] != pad: #Day
            cir_desregularizado += cir_slots[3].upper() + 'D'
            if regla != '':
                regla += '_day'
            else:
                regla += 'day'
        if cir_slots[4] != pad: 
            if cir_slots[7].lower() in partes_de_dia: #Part of Day
                cir_desregularizado += cir_slots[4].upper() + cir_slots[7].upper()
                regla = 'part_of_day'
            else: #Hour
                cir_desregularizado += cir_slots[4].upper() + 'H'
                if regla != '':
                    regla += '_hour'
                else:
                    regla += 'hour'
        if cir_slots[5] != pad: #Minute
            cir_desregularizado += cir_slots[5].upper() + 'MIN'
            if regla != '':
                regla += '_minute'
            else:
                regla += 'minute'
        if cir_slots[6] != pad: #Second
            cir_desregularizado += cir_slots[6].upper() + 'S'
            if regla != '':
                regla += '_second'
            else:
                regla += 'segundo'
        return cir_desregularizado
    except Exception as e:
        return ''

def desregularizar_cirs_set(cir):
    import re
    import copy
    try:
        cir_desregularizado = ''
        regla = ''
        pad = 'pad'
        parte_de_anio = ['wi', 'su',  'sp', 'fa', 'q', 't', 'half', 'we']
        partes_de_dia = ['taf','tmo','tmi','tev','ni','tni','tdt','w']

        #Longitud = 8 -> Year | Month/X(of stations, etc.) | Week(W)value | Day | Hour/X(evening, etc.) | minute | second | WE/SP/SU/WI/FA/Q/T/H/FA / AF/MO/MI/EV/NI/DT
        cir_slots = re.split(r'[<> ]', cir) 
        cir_slots = list(filter(lambda s: s != '', cir_slots))
        cir_slots = [i.lower() for i in cir_slots]
        if cir_slots[0] != pad: #Year
            cir_desregularizado += cir_slots[0].upper() + 'Y'
            regla += 'year'
        if cir_slots[1] != pad: 
            if cir_slots[7].lower() in parte_de_anio:
                cir_desregularizado += cir_slots[1].upper() + cir_slots[7].upper()
                regla = 'part_of_year'
            else: #Month
                cir_desregularizado += cir_slots[1].upper() + 'M'
                if regla != '':
                    regla += '_month'
                else:
                    regla += 'month'
        if cir_slots[2] != pad: #week
            cir_desregularizado += cir_slots[2].upper() + 'W'
            if regla != '':
                regla += '_week'
            else:
                regla += 'week'
        if cir_slots[3] != pad: #Day
            cir_desregularizado += cir_slots[3].upper() + 'D'
            if regla != '':
                regla += '_day'
            else:
                regla += 'day'
        if cir_slots[4] != pad: 
            if cir_slots[7].lower() in partes_de_dia:
                cir_desregularizado += cir_slots[4].upper() + cir_slots[7].upper()
                regla = 'part_of_day'
            else: #Hour
                cir_desregularizado += cir_slots[4].upper() + 'H'
                if regla != '':
                    regla += '_hour'
                else:
                    regla += 'hour'
        if cir_slots[5] != pad: #Minute
            cir_desregularizado += cir_slots[5].upper() + 'MIN'
            if regla != '':
                regla += '_minute'
            else:
                regla += 'minute'
        if cir_slots[6] != pad: #Second
            cir_desregularizado += cir_slots[6].upper() + 'S'
            if regla != '':
                regla += '_second'
            else:
                regla += 'second'
        return cir_desregularizado
    except Exception as e:
        return ''

#Predice las n predicciones (num_predicts) del modelo para una entrada (double_mask_sentence)
def predict_tokens(double_mask_sentence, model_, tokenizer):
  num_predicts = 1

  double_mask_input = tokenizer.encode(double_mask_sentence, return_tensors="pt").to(device)
  double_mask_input

  double_mask_token_logits = model_(double_mask_input)[0].squeeze().detach()
  is_masked = torch.where(double_mask_input == tokenizer.mask_token_id, 1, 0)
  masked_idxs = torch.nonzero(is_masked)
  probs= torch.softmax(double_mask_token_logits[masked_idxs[:,1]], dim=1)

  top_vocab_idxes = torch.topk(probs, num_predicts)
  lista = []
  #for token_id in torch.transpose(top_vocab_idxes[1], 1, 0): #Devuelve el string ya decodificado
  #    lista.append(tokenizer.decode(token_id))
    
  for token_id in top_vocab_idxes[1]: #Devuelve un token por posición
      lista.append(tokenizer.decode(token_id))
  return lista

def predict(type, string):
    ##### ESTO SE PUEDE SACAR FUERA Y PASAR EL trainer COMO ARGUMENTO
    model_checkpoint = 'XLM_normalization_BEST_MODEL'
    model = AutoModelForMaskedLM.from_pretrained(model_checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    data_collator = MyDataCollatorForLanguageModeling(tokenizer=tokenizer)
    trainer = Trainer(
      model,
      args,
      tokenizer=tokenizer,
      data_collator=data_collator,
    )
    #####
    if type.lower() == 'date':
        sentence = f"<date {string.lower()} <mask><mask><mask><mask><mask><mask><mask><mask> >"
    if type.lower() == 'time':
        sentence = f"<time {string.lower()} <mask><mask><mask><mask><mask><mask><mask><mask> >"
    if type.lower() == 'duration':
        sentence = f"<duration {string.lower()} <mask><mask><mask><mask><mask><mask><mask><mask> >"
    if type.lower() == 'set':
        sentence = f"<set {string.lower()} <mask><mask><mask><mask><mask><mask><mask><mask> >"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_ = trainer.model.to(device)
    predicciones = predict_tokens(sentence, model_, trainer.tokenizer)
    #print(' '.join(predicciones))
    return ' '.join(predicciones)


def main():
    import re
    import copy
    import sys
    #print("Hello from the main program!")
    if len(sys.argv) != 3:
        #print("Enter both the type and vir")
        return
    else:
        type = sys.argv[1]
        string = sys.argv[2]
        vir = predict(type, string)
        cir = desregularizar(type, vir)
        #print(vir_desregularizado)
        return cir
        
        #Llamar a annotador -> anchoring
        #Return
        
if __name__ == "__main__":
    main()