from unittest import TestCase
from unittest.mock import patch, Mock

from api.helpers.spiders.extended_link_extractor import ExtendedLinkExtractor
from scrapy.http import TextResponse


class MockConfigLoader:

    def __init__(self, *args, **kwargs):
        pass

    def get_allowed_cdn(self):
        """Return custom allowed CDN that can be visited because they can host data."""
        return ["an_allowed_cdn", "www.perdu.com", "www.ville-pierrelatte.fr"]

    def get_allowed_domain(self):
        """Return out of site domains that can be visited because they can host data."""
        return ["an_allowed_domain", "www.perdu.com", "www.ville-pierrelatte.fr"]

    def get_post_endpoints(self):
        return {
            "endpoint/url": {
                "url": "endpoint/url",
                "payload": {
                    "param1": "a",
                    "param2": "b"
                },
                "query_string": {
                    ""
                }
            }
        }

    def get_denied_pattern(self):
        """Return custom denied link patterns (calendar, search engine...)."""
        return ["a_denied_pattern",
                "www\\.bordeaux-metropole\\.fr/export/html/pdf",
                "www\\.lillemetropole\\.fr/communique-de-presse.*keywords",
                ".*tel:\\+?\\d+",
                ".*dcal=\\d+.*",
                ".*callto:\\d+.*",
                ".*[&\\?]xml=[NRF]\\d+.*",
                ".*recherche-avancee.*",
                ".*recherche[/]?\\?.*tx_solr.*",
                ".*layout/set/newsletter/layout/set/newsletter.*",
                ".*layout/set/print/layout/set/print.*",
                ".*/infos/infos/infos/.*",
                "(?i).*programme.*",
                "(?i).*planning.*",
                "(?i).*recherche\\?",
                "(?i).*reservations*.",
                "(?i).*www\\..*www\\..*",
                ".*mediatheque[s]?[\\.-].*",
                ".*bibliotheque[s]?[\\.-].*",
                ".*emploi[s]?[\\.-/].*",
                "(?i).*http.*http.*",
                "(?i).*offset.*offset.*",
                "(?i).*page.*page.*page.*page.*",
                "(?i).*id_photo.*id_photo.*",
                "(?i).*prt=.*prt=.*prt=.*",
                "(?i).*f=h.*f=h.*f=h.*",
                "(?i).*yyyy=.*yyyy=.*yyyy=.*",
                "(?i).*tmpl=component&print.*tmpl=component&print.*tmpl=component&print.*",
                "(?i).*p=\\d+.*p=\\d+.*p=\\d+.*",
                "(?i).*amp;amp;amp.*",
                "(?i).*printerfriendly=.*printerfriendly=.*",
                "(?i).*access=.*access=.*access=.*",
                "(?i).*/comptes-rendus-du-conseil/comptes-rendus-du-conseil.*",
                "(?i).*/actualites/actualites.*",
                "(?i).*catalog_repository.*catalog_repository.*",
                "(?i).*chateau-en-savoir-plus.*chateau-en-savoir-plus.*",
                "(?i).*imprimer=oui.*imprimer=oui.*",
                "(?i).*calendar.*",
                "(?i).*calendrier.*",
                "(?i).*agenda-des-elus.*",
                "(?i).*agenda-des-manifestations.*",
                "(?i).*agenda_.*",
                "(?i).*agenda\\..*",
                "(?i).*agenda-\\d+.*",
                "(?i).*[aA]genda-et-actualite[s]?.*",
                "(?i).*[aA]genda-de-.*",
                "(?i).*[aA]genda-date-.*",
                "(?i).*%20%20%20.*",
                "(?i).*////.*",
                "(?i).*\\?\\d+\\?\\d+\\?\\d+\\?\\d+.*",
                "(?i).*connexion\\?target.*",
                "(?i).*month=\\d+.*",
                "(?i).*mois=\\d+&an=\\d+.*",
                "(?i).*dtjour-\\d+.*",
                "(?i).*annuaire[s]?.*",
                "(?i).*paiement-en-ligne.*",
                "(?i).*[ée]v[éèe]nement[s]?.*",
                "(?i).*%C3%A9v%C3%A8nement[s]?.*",
                "(?i).*[Ff]ormulaire[s]?.*",
                ".*/contact/.*",
                ".*/lieux/.*",
                ".*/images/phocagallery/.*",
                ".*invitation.*",
                ".*mp4.*",
                ".*file/3D.*",
                ".*images/mp4.*",
                ".*/facebook_page.*",
                ".*xml",
                ".*video.*",
                "(?i).*horaire.*",
                ".*/reservation-de-salle[s]?/.*",
                ".*/jevents/.*",
                ".*/schedule/.*",
                ".*/commerces-et-services*",
                ".*geoloc.*",
                ".*vcard.*",
                ".*rhc-upcoming-events.*",
                ".*rhc-past-events.*",
                ".*mailto.*",
                ".*guide-des-demarches.*",
                ".*voillans.fr/search.*",
                ".*eANN9jMrtsPRta2/download.*",
                ".*/node/node/node/.*",
                ".*/index.php/index.php/.*",
                ".*/IMG/IMG/IMG/.*",
                ".*/IMG/pdf.*/IMG/pdf.*",
                ".*/IMG/jpg.*/IMG/jpg.*",
                ".*/vie-locale.*/vie-locale.*",
                ".*/vie-pratique.*/vie-pratique.*",
                ".*/activites--loisirs.*/activites--loisirs.*",
                ".*/la-commune.*/la-commune.*",
                ".*diaporamas.*la-commune.*",
                "(?i).*bouzel.fr/recherche.*",
                ".*droit[s]?-et-demarche[s]?.*",
                ".*droit[s]?-demarche[s]?.*",
                ".*autre[s]?-demarche[s]?.*",
                ".*les-demarches-administratives.*",
                ".*mention[s]?-legale[s]?.*",
                ".*disponibilite[s]?.*",
                ".*ModPath=td-galerie.*",
                ".*login.*",
                ".*window\\.open.*",
                ".*window\\.document\\.location\\.href.*",
                ".*/category/flashinfo/.*",
                ".*/day\\.php.*",
                ".*/month\\.php.*",
                ".*/week\\.php.*",
                ".*/day_all\\.php.*",
                ".*/month_all\\.php.*",
                ".*/week_all\\.php.*",
                ".*/fr/en/.*",
                ".*/sous-rubrique/\\d+/sous-rubrique/\\d+/sous-rubrique/\\d+.*",
                ".*/doc/images/\\d+/doc/images/\\d+.*",
                ".*/getNuevosFiltros.*",
                "(?i).*cerfa.*",
                "(?i).*pmb338/opac_css.*",
                "(?i).*ccvl.fr/plan.php.*",
                "(?i).*\\+\\+\\+.*",
                "(?i).*/export/print.*/export/print.*",
                ".*refine\\[Categories\\]\\[\\]=Photographies.*",
                "consultez-nos-offres.html",
                ".*/salles/.*",
                ".*/salle-municipale/.*",
                ".*/feed/.*",
                ".*/forums/.*",
                ".*/article[s]?-.*/article[s]?-.*/article[s]?-.*",
                ".*/les-photos.*",
                ".*joomladministration.*",
                "video-portes-les-valence.php",
                ".*date=\\d+.*",
                ".*mes-demarches.*",
                ".*/[Gg]alerie-de-photos.*",
                ".*/joomgallery.*",
                ".*/[Ss]ervice-[Pp]ublic*",
                ".*/\\(month\\)/.*/\\(day\\)/.*",
                ".*mois=\\d+&annee=\\d+.*",
                ".*annee=\\d+&annee=\\d+.*",
                ".*/la-ville-en-images/.*",
                ".*/events/.*",
                ".*year=.*",
                ".*/photos-\\d+.*",
                ".*/accessibilite/.*",
                ".*/demande_salle.*",
                ".*format=feed.*",
                ".*task=calendar.*",
                ".*media/media/media.*",
                ".*PLU/.*PLU/.*PLU/.*",
                ".*Documents/PLU/Documents/PLU/.*",
                ".*Documents/.*Documents/.*Documents/.*",
                ".*/switchFontSize.*",
                ".*/request_format.*",
                ".*/exact_date.*",
                ".*TPL_CODE.*",
                ".*this\\.removeAttribute.*"]

    def get_denied_domain(self):
        """Return domain not to visit (facebook, twitter, météofrance...)."""
        return ["education.fr",
                "fr-fr.facebook.com",
                "lempreinte.valenceromansagglo.fr",
                "moricobo.jimdo.com",
                "help.jimdo.com",
                "billiardwallaby.jimdo.com",
                "a.jimdo.com",
                "hsaa-studyabroad.jimdo.com",
                "www.weebly.com",
                "www.jimdo.com",
                "www.e-monsite.com",
                "team-japan.jimdo.com",
                "jp-help.jimdo.com",
                "davidlefebvre.e-monsite.com",
                "doc.conservatoire.agglo-montbeliard.fr:90",
                "emploi.vesoul.fr",
                "recrutement.bordeaux.fr",
                "reservations.port-sainte-foy.info",
                "plan.bordeaux.fr",
                "www.orange.fr",
                "fr.wordpress.com",
                "www.wordpress.com",
                "www.wix.com",
                "fr.wix.com",
                "www.wifeo.com",
                "salles.mairie-la-machine.fr",
                "ludomediatheques.terresdechalosse.fr",
                "www.canalblog.com",
                "biblio.vincennes.fr",
                "phototheque.hellemmes.fr"]


class TestExtendedLinkExtractor(TestCase):

    def setUp(self) -> None:
        self.sut = ExtendedLinkExtractor(list(), MockConfigLoader())

    def test__process_value_random_value_is_returned_as_is(self):
        random_input = 'a.random-link'

        actual = self.sut._process_value(random_input)

        self.assertEqual(random_input, actual)

    def test__process_value_mismatched_quote_is_returned_as_is(self):
        random_input = 'window.open("x\')'

        actual = self.sut._process_value(random_input)

        self.assertEqual(random_input, actual)

    def test__process_value_windowopen_returns_link(self):
        input = 'window.open("x")'

        actual = self.sut._process_value(input)

        self.assertEqual('x', actual)

    def test__process_value_windowlocation_returns_link(self):
        input = 'window.location("x")'

        actual = self.sut._process_value(input)

        self.assertEqual('x', actual)

    def test__process_value_windowopen_with_whitespace_returns_link(self):
        input = '  window  .  open  (  "x"  ,  '

        actual = self.sut._process_value(input)

        self.assertEqual('x', actual)

    def test__extract_links__returns_link(self):
        url = "https://www.ville-pierrelatte.fr/accueil/sortir/truck-de-food"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].url, "https://www.ville-pierrelatte.fr/accueil/sortir/truck-de-food")

    def test__extract_links__skips_service_public_1(self):
        url = "https://www.ville-pierrelatte.fr/accueil/quotidien/urbanisme/faire-des-travaux/permis-damenager?xml=F20568"  # noqa E501
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_service_public_2(self):
        url = "https://www.ville-pierrelatte.fr/accueil/quotidien/urbanisme/faire-des-travaux/permis-damenager?xml=N120"  # noqa E501
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_service_public_3(self):
        url = "https://www.ville-pierrelatte.fr/accueil/services-en-lignes/professionnels?xml=R8568"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_service_public_4(self):
        url = "https://saintrestitut-mairie.fr/demarches/?networkwide=1&xml=R2454"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_service_public_5(self):
        url = "https://saintrestitut-mairie.fr/demarches/?networkwide=1&xml=R2454&cookie=1"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_telephone_1(self):
        url = "https://saintrestitut-mairie.fr/demarches/tel:01235335"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_telephone_2(self):
        url = "https://saintrestitut-mairie.fr/demarches/tel:+331235335"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    def test__extract_links__skips_telephone_3(self):
        url = "tel:01235335"
        input = self._build_text_response(url)

        actual = self.sut.extract_links(input)

        self.assertListEqual(actual, [])

    @patch("api.helpers.spiders.extended_link_extractor.requests")
    def test__is_redirection(self, mk_request):
        mk_response = Mock(status_code=301)

        mk_request.get().history = [mk_response]
        mk_request.get().url = "new_url"

        actual = self.sut.is_redirected("random_url")
        self.assertEqual("new_url", actual[0])
        self.assertTrue(actual[1])

    @patch("api.helpers.spiders.extended_link_extractor.requests")
    def test__is_not_redirection(self, mk_request):
        mk_response = Mock(status_code=200)

        mk_request.get().history = [mk_response]
        mk_request.get().url = "new_url"

        actual = self.sut.is_redirected("random_url")
        self.assertEqual("random_url", actual[0])
        self.assertFalse(actual[1])

    def _build_text_response(self, url: str):
        return TextResponse(
            url='http://www.perdu.com/',
            encoding='utf-8',
            body=f'<a href="{url}">x</a>'
        )
