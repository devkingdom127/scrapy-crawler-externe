import scrapy

from api.helpers.pipeline.serializers import location_serializer


class AdminDocItem(scrapy.Item):
    """
    Output type for the admin doc spider
    """

    #: the URL where the current file was found
    url = scrapy.Field()

    #: the MIME type for the current file
    responseMimeContentType = scrapy.Field()

    #: the territory_uid array that was given to the current spider
    locations = scrapy.Field(serializer=location_serializer)

    #: main website URL where the document was scraped
    dataProvider = scrapy.Field()

    #: reference to the specific crawler run when this was built
    operationId = scrapy.Field()
