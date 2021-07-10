from config.definitions import Cst


def location_serializer(locations: list):
    """
    Serializer specific to the location field.

    Input : ["FRCOMM44503"]
    Output : [{"FRCOMM44503": ["publisher"]}]
    """
    output = ''
    for key in locations[0]:
        if key == 'uid':
            output = [{locations[0][key]: [Cst.PUBLISHER]}]

    return output
