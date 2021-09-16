from typing import List, Tuple


def pcs_parse_parameters(pcs_parameters: List[str]) -> Tuple[List[str], str]:
    """ 
    Parse pcs parameters (delivered by SMAC) to clingo parameters.
    """
    parameters = []
    parameters_with_args = {}
    solver = None

    for pcs_parameter_name, pcs_value in zip(pcs_parameters[::2], pcs_parameters[1::2]):
        name, priority_or_flag, key, *_ = pcs_parameter_name.split(':') + ([None] * 2)

        if name == '--solver':
            solver = pcs_value
            continue

        if name in ['-c', '--const']:  # clingo constant
            constant_name = key if priority_or_flag.isnumeric() else priority_or_flag
            parameters += ['-c', f'{constant_name}={pcs_value}']
            continue

        if name == '--include':  # include
            include_file = pcs_value
            if include_file.lower() not in ['none', 'no']:
                parameters.append(include_file)
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
