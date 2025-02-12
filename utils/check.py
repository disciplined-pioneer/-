def get_nds(check_data: dict) -> int:
    data = check_data['data']['json']

    if nds := data.get('nds'):
        return nds
    elif nds := data.get('nds18'):
        return nds
    elif nds := data.get('nds0'):
        return nds
    elif data.get('ndsNo'):
        return 0
