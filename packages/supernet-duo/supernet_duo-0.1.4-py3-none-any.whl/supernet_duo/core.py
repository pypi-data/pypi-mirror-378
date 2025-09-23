def network(inpt,celldata,weights):
    def parse_key_value_pair(pair_string):
        colon_index = -1
        balance = 0
        for i, char in enumerate(pair_string):
            if char == '{':
                balance += 1
            elif char == '}':
                balance -= 1
            elif char == ':' and balance == 0:
                colon_index = i
                break
        if colon_index == -1:
            raise ValueError(f"Invalid key-value pair format: {pair_string}")
        key_string = pair_string[:colon_index].strip()
        value_string = pair_string[colon_index + 1:].strip()
        key = _convert_string_to_python_type(key_string)
        value = _convert_string_to_python_type(value_string)
        return key, value
    def string_to_dict(dict_string):
        if not dict_string.startswith('{') or not dict_string.endswith('}'):
            raise ValueError("Input string must be a dictionary representation enclosed in curly braces.")
        content = dict_string[1:-1]
        result_dict = {}
        balance = 0
        current_key_value_pair = []
        for char in content:
            if char == '{':
                balance += 1
            elif char == '}':
                balance -= 1
            if char == ',' and balance == 0:
                pair_string = "".join(current_key_value_pair).strip()
                if pair_string:
                    key, value = parse_key_value_pair(pair_string)
                    result_dict[key] = value
                current_key_value_pair = []
            else:
                current_key_value_pair.append(char)
        if current_key_value_pair:
            pair_string = "".join(current_key_value_pair).strip()
            if pair_string:
                key, value = parse_key_value_pair(pair_string)
                result_dict[key] = value
        return result_dict
    def percent_match1(str1, str2):
        m = len(str1)
        n = len(str2)
        if m == 0 or n == 0:
            return 100.0 if m == n else 0.0
        table = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                else:
                    table[i][j] = max(table[i - 1][j], table[i][j - 1])
        lcs_length = table[m][n]
        max_len = max(m, n)
        score = lcs_length / max_len
        def exp(x):
            n_terms = 50
            result = 0.0
            term = 1.0
            for i in range(n_terms):
                result += term
                term *= x / (i + 1)
            return result
        return 100 / (1 + exp(-12 * (score - 0.5)))
    def sigmoid(x):
        y = x ** 2
        return y
    def percent_match2(str1, str2):
        set1 = (str1.lower())
        set2 = (str2.lower())
        match = 0
        if len(set1)>=len(set2):
            cnt =0
            for it in set1:

                try:
                    if set1[cnt] == set2[cnt]:
                        match+=1
                except:
                    continue
                cnt=cnt+1
            full = match / len(set1)

        elif len(set2)>len(set1):

            cnt =0
            for it in set2:

                try:
                    if set1[cnt] == set2[cnt]:
                        match+=1
                except:
                    continue
                cnt=cnt+1
            full = match/len(set2)
        else:
            return None

        return float(str(sigmoid(full))[:4])
    def equalize(val,datadict):
        dict_values_object = datadict.values()
        listoval = list(dict_values_object)
        values_list = list(datadict.values())
        valdict = {}
        for va in listoval:
            count = values_list.count(va)
            valdict[va]=count
        percentdict = {}
        totals = list(valdict.values())
        total = 0
        for num in totals:
            total = total+num
        for key in valdict:
            percentdict[key] = ((valdict[key])/total)*100
        times = 100/len(percentdict)
        fixdict = {}
        for th in percentdict:
            prec = times/percentdict[th]
            fixdict[th] = prec
        items = list(set(listoval))

        retlist =[]
        for nums in items:
            req = val.count(nums)
            new = round(fixdict[nums] * req)
            while True:
                if new==0:
                    break
                retlist.append(nums)
                new = new-1
        return retlist
    def _convert_string_to_python_type(s):
        s = s.strip()
        if s.startswith("'") and s.endswith("'") or s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        elif s.isdigit() or (s.startswith('-') and s[1:].isdigit()):
            return int(s)
        elif s.replace('.', '', 1).isdigit() or (s.startswith('-') and s[1:].replace('.', '', 1).isdigit()):
            return float(s)
        elif s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
        elif s.lower() == 'none':
            return None
        elif s.startswith('{') and s.endswith('}'):
            return string_to_dict(s)
        else:
            return s
    def find_most_frequent_string(string_list):
        if not string_list:
            return None
        counts = {}
        for string in string_list:
            if string in counts:
                counts[string] += 1
            else:
                counts[string] = 1
        most_frequent_string = None
        max_count = 0
        for string, count in counts.items():
            if count > max_count:
                max_count = count
                most_frequent_string = string
        return most_frequent_string
    def calculate_average(float_list):
        if not float_list:
            return 0.0
        return sum(float_list) / len(float_list)
    def format(strin,cls,datadict):
        lst = strin.split(' ')
        data = {}
        for the in lst:
            if the in datadict:
                data[f' {the}']=cls
                continue
            data[the]=cls
        return data | datadict
    def lastLayer(list):
        dict_values_view = list.values()
        list_of_values = list(dict_values_view)
        return list_of_values
    def cell0(str):
        str.replace('\n','')
        str.replace('"', '')
        str.replace('=', ':')
        return str
    def cell1(str,celldata):
        vallist ={}
        keylist = []
        for key, value in celldata.items():
            match = percent_match1(key,str)*100
            vallist[key] = match
            keylist.append(float(match))
        keylist.sort(reverse=True)
        matching_keys=[]
        for val in keylist:
            for key, value in vallist.items():
                if value == val:
                    matching_keys.append(key)
        #print('//cell1//Matches:',vallist)

        addlist = []
        curval = -1
        for num in keylist:
            curval = curval+1
            if num == 100.0:
                if (celldata[matching_keys[0]]) == True:
                    return 1.00
                else:
                    return 0.00
            cnt = int(num/ 10)
            while True:
                cnt = cnt-1
                addlist.append(matching_keys[curval])
                if cnt < 1:
                    break
        finalist = []
        for ag in addlist:
            finalist.append(celldata[ag])
        totalsum = 0
        return finalist
    def cell2(str,celldata,cell1,bias):
        vallist ={}
        keylist = []
        for key, value in celldata.items():
            match = percent_match2(key,str)*100
            vallist[key] = match
            keylist.append(float(match))
        keylist.sort(reverse=True)
        matching_keys=[]
        for val in keylist:
            for key, value in vallist.items():
                if value == val:
                    matching_keys.append(key)
        #print('Matches:',vallist)

        addlist = []
        curval = -1
        for num in keylist:
            curval = curval+1
            if num == 100.0:
                if (celldata[matching_keys[0]]) == True:
                    return 1.00
                else:
                    return 0.00
            cnt = int(num/ 10)
            while True:
                cnt = cnt-1
                addlist.append(matching_keys[curval])
                if cnt < 1:
                    break
        finalist = []

        for op in cell1:
            cn = bias
            while True:
                if cn == 0:
                    break
                cn = cn-1
                finalist.append(op)
        #print(finalist)
        return finalist
    result = find_most_frequent_string(equalize(cell2(inpt, celldata, cell1(cell0(inpt), celldata), weights), celldata))
    return result

