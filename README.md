# Administrative documents website crawler

This code crawls the whole given website and spits out the URL of the encountered PDFs in a txt file.
## Content

### Architecture
It is a worker [Scrapy crawler](https://docs.scrapy.org/en/latest/index.html)

## Prerequisites

### virtualenv

To setup the environment, run

```bash
pyenv install 3.6.7
pyenv virtualenv 3.6.7 crawler-worker-venv
pyenv local crawler-worker-venv
pip install -r requirements.txt
```

## Configuration
The list of the domain not allowed is stoked in S3 at `s3-admindoc-config/crawler_deny_domain.json`, where you can customize the domain will be denied for the crawler 
## Running the code locally

### Pensieve

- Start local pensieve; go to local repo and launch
```
python application.py
```
- Or launch with pensieve staging
```
export ADMINDOC_CRAWLER_PENSIEVE_URL=https://api.staging-pensieve.explain.fr
```
### Run crawler_worker

```
python application.py
```
 
#### In swagger interface

Open [http://127.0.0.1:9090/](http://127.0.0.1:9090/) in your brower 

Test run RP with this payload
```
{
   "crawler_expected_content_type":"administrative_document",
   "crawler_options":{
      "locations":[
         {
            "name":"Drôme",
            "uid":"FRDEPA26"
         }
      ],
      "start_url":"http://www.saintnazaireledesert.fr",
      "user":"my_user"
   },
   "crawler_type":"spider",
   "input":{}
}
```

To test the crawler, you should modify `start_url`.

In `locations`, uid is used to instantiate a specific spider. Other parameters can be left unchanged
and have no particular effect in this version of the crawler.

### Implement a specific crawler

In some cases for specific website with an uncommon architecture, it is necessary to develop specific
spiders. Here is the procedure to do so.

#### Create a specific spider file

The specific spider should be put into `api/helpers/spiders/custom` repository (where there are already
examples available). The name of the file should be clear enough to understand the territory to which 
the spider is used.

#### Content

The file should contain a single class, inheriting from the generic `AdminDocSpider`:

```python
from api.helpers.spiders.admin_doc_spider import AdminDocSpider

class SaintEtienneSpider(AdminDocSpider):
    """This class is specifically designed to scrapped pdf file from https://www.saint-etienne.fr/."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
```

As the class already has methods from `AdminDocSpider`, it is already able to scrape docs. You should then
add methods or supercharge some methods to treat specific cases. Such (non-exhaustive) examples are:

- Some documents are accessible only via calling to a search engine: in this case create some methods 
  that call the search engine endpoint and yield url (see `amiens_spider.py` for such example.
- Some website are single page application. In this case, endpoint should be called directly.
- In some cases, documents are inside an iframe. In this case, you can add the iframed website in 
the start url (see `aixmarseillemetropole_spider.py`).
- ...

This is often the parse_response method that need first to be supercharged
as this is the function that is recursively called when scraping a website.
This function should yield either:

- A scrapy.Reponse, which is a new page to go through.
- An `AdminDocItem`(which is a link to a pdf document).

When you supercharge the method, adding new functionality,
you should always also call `super().parse_response(response)` to 
use the generic spider crawling abilities.

#### Activate the specific spider

A custom spider is linked to a specific location uid. This link is created 
in `api/helpers/spiders/custom/__init__.py`. For instance:

```python
from api.helpers.spiders.custom.aixmarseillemetropole_spider import AixMarseilleParser
from api.helpers.spiders.custom.amiens_spider import AmiensParser
from api.helpers.spiders.custom.lille_spider import LilleSpider
from api.helpers.spiders.custom.saintetienne_spider import SaintEtienneSpider

custom_spiders = {
    "FRCOMM59350": LilleSpider,
    "FREPCI248000531": AmiensParser,
    "FRCOMM80021": AmiensParser,
    'FREPCI200054807': AixMarseilleParser,
    "FRCOMM42218": SaintEtienneSpider
}
```

When it's done, a call to the endpoint with a location code `FRCOMM422218` will trigger the `SaintEtienneSpider`.

#### How to verify the job is done ?

The triggering of a crawling task leads to the writing of 2 files in the `output` folder:

- `visited_urls.txt` which list the url the spider visited.
- `output_urls.txt` which list the docs it has found.

This way you can see whether the modifications you implemented
made a difference.
