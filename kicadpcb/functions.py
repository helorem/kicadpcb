def sexpr2dict(data, headers):
    key = data[0]
    res = {}
    for i in xrange(1, len(data)):
        item = data[i]
        if type(item) == type([]):
            sub_key, val = sexpr2dict(item, headers)
            if sub_key not in res:
                res[sub_key] = []
            res[sub_key].append(val)
        elif key in headers:
            res[headers[key][i - 1]] = [item]
        else:
            if key not in res:
                res[key] = []
            res[key].append(item)
    for res_key in res.keys():
        if len(res[res_key]) == 1:
            res[res_key] = res[res_key][0]
    if len(res) == 1 and key in res:
        res = res[key]
    return key, res


