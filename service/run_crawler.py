from asyncio.log import logger
from time import sleep
import base64

from twocaptcha import TwoCaptcha
import requests

from app.config import settings
from utils.utils import clear_tax_id


class CrawlerCriminal:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.session = requests.Session()

        self.session.headers = {
            'Fingerprint': '',
            'Origin': f'https://{self.endpoint}',
            'Referer': f'https://{self.endpoint}/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def _get_warrant_details(self, warrant_id: int):
        url = f'https://{self.endpoint}/bnmpportal/api/certidaos/{warrant_id}/1'
        resp = self.session.get(url).json()

        parsed = dict()
        parsed['id'] = resp['id']
        parsed['expedition'] = resp['dataExpedicao']
        parsed['expiration'] = resp['dataValidade']
        parsed['warrant_number'] = resp['numeroPeca']
        parsed['warrant_type'] = resp['tipoPeca']['descricao']
        parsed['status'] = resp['status']['descricao']
        parsed['process_number'] = resp['numeroProcesso']
        parsed['prison_type'] = resp['especiePrisao']
        parsed['magistrate'] = resp['magistrado']
        parsed['consignor'] = resp['orgaoJudiciario']['nome']
        parsed['city'] = resp['orgaoJudiciario']['municipio']['nome']
        parsed['state'] = resp['orgaoJudiciario']['municipio']['uf']['sigla']
        parsed['penal_classification'] = (
            [item['rotulo'] for item in v] if (v := resp['tipificacaoPenal']) else None
        )
        parsed['person'] = {}
        parsed['person']['name'] = (
            v[0]['nome'] if (v := resp['pessoa']['outrosNomes']) else None
        )
        parsed['person']['nickname'] = (
            v[0]['nome'] if (v := resp['pessoa']['outrasAlcunhas']) else None
        )
        parsed['person']['mother_name'] = (
            v[0]['nome'] if (v := resp['pessoa']['nomeMae']) else None
        )
        parsed['person']['father_name'] = (
            v[0]['nome'] if (v := resp['pessoa']['nomePai']) else None
        )
        parsed['person']['nationality'] = (
            v['nome']
            if (v := resp['pessoa']['dadosGeraisPessoa']['paisNascimento'])
            else None
        )
        parsed['person']['birthdate'] = resp['pessoa']['dataNascimento']
        parsed['person']['sex'] = resp['pessoa']['dadosGeraisPessoa']['sexo'][
            'descricao'
        ]
        parsed['recapture'] = resp['recaptura']

        return parsed

    def _generate_no_warrants_file(self, doc_num) -> bytes:
        payload = {
            'numeroCpf': doc_num,
            'orgaoExpeditor': {},
            'buscaOrgaoRecursivo': True,
        }
        resp = self.session.post(
            f'https://{self.endpoint}/bnmpportal/api/pesquisa-pecas/emitir-documento',
            json=payload
        )

        return resp.content

    def _generate_warrant_file(self, warrant_id: int):
        url = f'https://{self.endpoint}/bnmpportal/api/certidaos/relatorio/{warrant_id}/1'
        resp = self.session.post(url, stream=True)
        return url, resp.content

    def search(self, dict_warrants):
        max_attempts = 3
        g_response = None
        for attempt in range(1, max_attempts + 1):
            try:
                resp = self.session.get(f'https://{self.endpoint}/api/recaptcha/sitekey')
                if resp.status_code != 200:
                    raise Exception('Erro ao obter siteKey')

                site_key = resp.json().get('siteKey')
                page_url = f'https://{self.endpoint}/#/pesquisa-peca'

                config = {
                    'apiKey': settings.RECAPTCHA_KEY,
                    'defaultTimeout': 120,
                    'recaptchaTimeout': 600,
                    'pollingInterval': 10
                }
                solver = TwoCaptcha(**config)

                try:
                    result = solver.recaptcha(
                        sitekey=site_key,
                        url=page_url
                    )
                    token = result['code']
                    g_response = token

                except Exception as e:
                    print('Erro ao resolver o captcha:', e)

                url = f"https://{self.endpoint}/api/recaptcha"
                payload = {'idToken': g_response}
                g_response = self.session.post(url, json=payload).json()['idToken']

                if g_response == 0:
                    raise print(f'Erro ao resolver captcha:')
                break

            except Exception as e:
                logger.error(f'Tentativa {attempt} falhou: {e}')
                sleep(3)
                if attempt == max_attempts:
                    raise print(f'Falhou após {max_attempts} tentativas') from e

        self.session.cookies.update({
            'portalbnmp': g_response
        })

        payload = {
            'numeroCpf': dict_warrants['tax_id'],
            'orgaoExpeditor': {},
            'buscaOrgaoRecursivo': False,
        }
        resp = self.session.post(
            f'https://{self.endpoint}/bnmpportal/api/pesquisa-pecas/filter',
            params={'page': 0, 'size': 10, 'sort': ''},
            json=payload
        )

        warrants = resp.json().get('content')

        try:
            if not warrants:
                no_warrants_file = base64.b64encode(
                    self._generate_no_warrants_file(doc_num=dict_warrants['tax_id'])
                ).decode()

                dict_return = {
                    'file': no_warrants_file,
                    'criminal_record': [],
                    'tax_id': clear_tax_id(dict_warrants['tax_id'])
                }

                return dict_return

            else:
                for warrant in warrants:
                    w = self._get_warrant_details(warrant['id'])
                    link, file_ = self._generate_warrant_file(warrant['id'])
                    w['file'] = base64.b64encode(file_).decode()
                    w['file_extension'] = 'pdf'
                    w['file_link'] = link

                    criminal_record_save = {
                        'certificate': w['id'],
                        'motherName': w['person']['mother_name'],
                        'name': w['person']['name'],
                        'cleanRecord': True,
                        'taskId': dict_warrants['tax_id'],
                        'expedition': w['expedition'],
                        'fileUrl': w['file']
                    }

                    dict_return = {
                        'file': w['file'],
                        'criminal_record': criminal_record_save,
                        'tax_id': clear_tax_id(dict_warrants['tax_id'])
                    }

                    return dict_return

        except Exception as e:
            logger.error(f'Erro falhou: {e}')
