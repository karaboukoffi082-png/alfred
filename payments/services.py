import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class MobileMoneyService:
    """
    Service d'intégration Mobile Money via PayGateGlobal (Flooz / T-Money).
    Documentation : https://paygateglobal.com
    """

    def __init__(self):
        self.auth_token = getattr(settings, 'PAYGATE_API_KEY', None)
        self.base_url = "https://paygateglobal.com/api/v1"
        # --- MODE SIMULATION FORCÉ (compte inactif) ---
        self.simulation_mode = True
        # self.simulation_mode = not self.auth_token   # À réactiver plus tard
        # ---------------------------------------------
        if self.simulation_mode:
            logger.warning("MobileMoneyService en mode simulation (compte inactif ou test).")
        else:
            logger.info("MobileMoneyService configuré avec PayGateGlobal.")

    def _clean_phone(self, phone):
        """Nettoie le numéro pour PayGateGlobal (format 228XXXXXXXX)."""
        if not phone:
            return phone
        phone = phone.strip().replace(' ', '').replace('-', '').replace('.', '')
        if phone.startswith('+'):
            phone = phone[1:]
        if not phone.startswith('228'):
            phone = '228' + phone
        return phone

    def initiate(self, amount, phone, operator, reference):
        """
        Initier une transaction (Méthode 1 - API directe).
        """
        if self.simulation_mode:
            return {
                'success': True,
                'transaction_id': f"SIMU_{reference}",
                'message': 'Transaction simulée - Mode test',
            }

        # Normalisation du réseau
        network = 'FLOOZ' if operator.upper() in ['FLOOZ', 'MOOV'] else 'TMONEY'

        # Nettoyage du numéro
        phone_clean = self._clean_phone(phone)

        payload = {
            'auth_token': self.auth_token,
            'phone_number': phone_clean,
            'amount': str(amount),
            'description': f'Commande {reference}',
            'identifier': reference,
            'network': network,
        }

        print("\n=== PAYGATE REQUEST ===")
        print(f"URL: {self.base_url}/pay")
        print(f"Payload: {payload}")
        print("========================\n")

        try:
            response = requests.post(
                f'{self.base_url}/pay',
                json=payload,
                timeout=30
            )

            print("\n=== PAYGATE RESPONSE ===")
            print(f"Status Code: {response.status_code}")
            print(f"Body (text): {response.text[:500]}")
            print("=========================\n")

            try:
                data = response.json()
            except ValueError:
                logger.error(f"Réponse non-JSON reçue: {response.text[:200]}")
                return {
                    'success': False,
                    'message': 'Le service de paiement a répondu de manière inattendue.'
                }

            status_code = data.get('status')
            if status_code == 0:
                return {
                    'success': True,
                    'transaction_id': data.get('tx_reference', ''),
                    'message': 'Transaction initiée avec succès',
                }
            elif status_code is None:
                # Gestion du format d'erreur avec error_code (ex: compte inactif)
                error_code = data.get('error_code')
                if error_code == 403:
                    msg = "Service de paiement momentanément indisponible (compte en cours d'activation)."
                else:
                    msg = data.get('error_message', 'Erreur inconnue')
                logger.error(f"PayGateGlobal error {error_code}: {msg}")
                return {'success': False, 'message': msg}
            else:
                error_messages = {
                    2: 'Clé API invalide',
                    4: 'Paramètres invalides',
                    6: 'Doublon de commande',
                }
                msg = error_messages.get(status_code, f"Erreur {status_code}")
                logger.error(f"PayGateGlobal error {status_code}: {msg}")
                return {'success': False, 'message': msg}

        except requests.RequestException as e:
            logger.error(f"Erreur réseau PayGateGlobal: {e}")
            return {'success': False, 'message': 'Impossible de contacter le service de paiement.'}

    def check_status(self, tx_reference):
        """Alias pour compatibilité."""
        return self.check_status_by_tx_reference(tx_reference)

    def check_status_by_tx_reference(self, tx_reference):
        """Vérifier le statut d'une transaction via tx_reference."""
        if self.simulation_mode:
            return {
                'status': 'success',
                'message': 'Paiement simulé réussi',
                'payment_reference': 'SIMU_REF',
            }

        payload = {
            'auth_token': self.auth_token,
            'tx_reference': tx_reference,
        }

        try:
            response = requests.post(
                f'{self.base_url}/status',
                json=payload,
                timeout=15
            )
            data = response.json()

            status_map = {0: 'success', 2: 'pending', 4: 'expired', 6: 'cancelled'}
            status_code = data.get('status')
            status = status_map.get(status_code, 'unknown')

            return {
                'status': status,
                'message': data.get('message', ''),
                'payment_reference': data.get('payment_reference', ''),
                'datetime': data.get('datetime'),
                'payment_method': data.get('payment_method'),
            }

        except requests.RequestException as e:
            logger.error(f"Erreur vérification statut: {e}")
            return {'status': 'unknown', 'message': str(e)}

    def check_status_by_identifier(self, identifier):
        """Vérifier le statut d'une transaction via identifiant commande (v2)."""
        if self.simulation_mode:
            return {
                'status': 'success',
                'message': 'Paiement simulé réussi',
                'payment_reference': 'SIMU_REF',
            }

        payload = {
            'auth_token': self.auth_token,
            'identifier': identifier,
        }

        try:
            response = requests.post(
                'https://paygateglobal.com/api/v2/status',
                json=payload,
                timeout=15
            )
            data = response.json()

            status_map = {0: 'success', 2: 'pending', 4: 'expired', 6: 'cancelled'}
            status_code = data.get('status')
            status = status_map.get(status_code, 'unknown')

            return {
                'status': status,
                'message': '',
                'payment_reference': data.get('payment_reference', ''),
                'datetime': data.get('datetime'),
                'payment_method': data.get('payment_method'),
            }

        except requests.RequestException as e:
            logger.error(f"Erreur vérification statut: {e}")
            return {'status': 'unknown', 'message': str(e)}

    def get_payment_page_url(self, amount, phone, reference, description='', network=None):
        """Générer l'URL de la page de paiement hébergée (Méthode 2)."""
        base_page_url = "https://paygateglobal.com/v1/page"
        params = {
            'token': self.auth_token,
            'amount': str(amount),
            'identifier': reference,
        }
        if description:
            params['description'] = description
        if phone:
            params['phone'] = self._clean_phone(phone)
        if network:
            params['network'] = network.upper()

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_page_url}?{query_string}"