

def pcs_parse_parameters(pcs_parameters: [str]) -> ([str], str):
    parameters = []
    parameters_with_args = {}
    solver = None

    for pcs_parameter_name, pcs_value in zip(pcs_parameters[::2], pcs_parameters[1::2]):
        name, priority_or_flag, key, *_ = pcs_parameter_name.split(':') + ([None] * 2)

        if name == '--solver':
            solver = pcs_value
            continue

        if priority_or_flag == 'S':  # skip flag
            continue
        elif priority_or_flag == 'F':  # flag parameter flag :)
            if pcs_value.lower() == 'yes':
                parameters.append(name)
        else:  # otherwise priority number or None
            if not parameters_with_args.get(name):
                parameters_with_args[name] = []
            parameters_with_args[name].append((int(priority_or_flag or 0), key, pcs_value))

    for name in parameters_with_args.keys():
        parameters_with_args[name].sort(key=lambda x: x[0])  # sort args by priority

        p = ','.join(map(lambda x: x[2] if not x[1] else f'{x[1]}={x[2]}', parameters_with_args[name]))
        parameters.append(f'{name}={p}')

    return parameters, solver
