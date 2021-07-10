from api.helpers.spiders.custom.aixmarseillemetropole_spider import AixMarseilleParser
from api.helpers.spiders.custom.amiens_spider import AmiensParser
from api.helpers.spiders.custom.lille_spider import LilleSpider

custom_spiders = {
    "FRCOMM59350": LilleSpider,
    "FREPCI248000531": AmiensParser,
    "FRCOMM80021": AmiensParser,
    'FREPCI200054807': AixMarseilleParser
}
