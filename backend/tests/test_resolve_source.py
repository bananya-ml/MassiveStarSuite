from modules.resolve_source import resolve

if __name__ == "__main__":

    # test values
    source_id = '4111834567779557376'
    ra = '256.5229102004341'
    dec = '-26.580565130784702'

    results = resolve(id=source_id)#None,coords=list((ra,dec)))