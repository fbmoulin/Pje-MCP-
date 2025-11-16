"""
Certificate Manager Module
===========================

Módulo para gerenciamento de certificados digitais A1 e A3 para autenticação
em sistemas PJE (Processo Judicial Eletrônico).

Suporta:
- Certificados A1 (arquivos PFX/P12)
- Certificados A3 (Windows Certificate Store - via smart card/token)
- Validação de certificados
- Verificação de expiração
- Extração de informações do certificado

Autor: Claude Code
Licença: MIT
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import Certificate, load_pem_x509_certificate

# Logging
logger = logging.getLogger("cert-manager")


@dataclass
class CertificateInfo:
    """Informações do certificado digital"""

    subject: str
    issuer: str
    serial_number: str
    not_valid_before: datetime
    not_valid_after: datetime
    days_until_expiry: int
    is_valid: bool
    thumbprint: str
    cert_type: str  # "A1" or "A3"


class CertificateError(Exception):
    """Exceção base para erros de certificado"""
    pass


class CertificateExpiredError(CertificateError):
    """Certificado expirado"""
    pass


class CertificateNotFoundError(CertificateError):
    """Certificado não encontrado"""
    pass


class CertificatePasswordError(CertificateError):
    """Senha do certificado incorreta"""
    pass


class CertificateManager:
    """
    Gerenciador de certificados digitais A1 e A3

    Examples:
        >>> # Certificado A1
        >>> manager = CertificateManager(cert_type="A1")
        >>> manager.load_a1_certificate("/path/to/cert.pfx", "password")
        >>> info = manager.get_certificate_info()
        >>> print(f"Válido até: {info.not_valid_after}")
    """

    def __init__(self, cert_type: str = "A1"):
        """
        Inicializa o gerenciador de certificados

        Args:
            cert_type: Tipo do certificado ("A1" ou "A3")

        Raises:
            ValueError: Se cert_type não for "A1" ou "A3"
        """
        if cert_type not in ["A1", "A3"]:
            raise ValueError(f"Tipo de certificado inválido: {cert_type}. Use 'A1' ou 'A3'")

        self.cert_type = cert_type
        self.certificate: Optional[Certificate] = None
        self.private_key = None
        self.cert_path: Optional[str] = None
        self._additional_certs = []

        logger.info(f"CertificateManager inicializado para certificados {cert_type}")

    def load_a1_certificate(self, cert_path: str, password: str) -> None:
        """
        Carrega certificado A1 de arquivo PFX/P12

        Args:
            cert_path: Caminho para o arquivo PFX/P12
            password: Senha do certificado

        Raises:
            CertificateNotFoundError: Se o arquivo não existir
            CertificatePasswordError: Se a senha estiver incorreta
            CertificateExpiredError: Se o certificado estiver expirado
            CertificateError: Para outros erros
        """
        # Verificar se arquivo existe
        if not os.path.exists(cert_path):
            raise CertificateNotFoundError(f"Arquivo de certificado não encontrado: {cert_path}")

        logger.info(f"Carregando certificado A1 de: {cert_path}")

        try:
            # Ler arquivo PFX
            with open(cert_path, "rb") as f:
                pfx_data = f.read()

            # Converter senha para bytes se necessário
            if isinstance(password, str):
                password_bytes = password.encode()
            else:
                password_bytes = password

            # Carregar certificado e chave privada
            try:
                private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                    pfx_data,
                    password_bytes,
                    backend=default_backend()
                )
            except ValueError as e:
                if "password" in str(e).lower() or "mac" in str(e).lower():
                    raise CertificatePasswordError(
                        "Senha incorreta ou arquivo PFX corrompido"
                    ) from e
                raise CertificateError(f"Erro ao carregar certificado: {str(e)}") from e

            # Verificar se certificado foi carregado
            if certificate is None:
                raise CertificateError("Nenhum certificado encontrado no arquivo PFX")

            # Verificar validade
            now = datetime.utcnow()
            if certificate.not_valid_after < now:
                raise CertificateExpiredError(
                    f"Certificado expirado em {certificate.not_valid_after.isoformat()}"
                )

            if certificate.not_valid_before > now:
                raise CertificateError(
                    f"Certificado ainda não é válido. Válido a partir de {certificate.not_valid_before.isoformat()}"
                )

            # Armazenar certificado e chave
            self.certificate = certificate
            self.private_key = private_key
            self._additional_certs = additional_certs or []
            self.cert_path = cert_path

            logger.info("Certificado A1 carregado com sucesso")
            logger.info(f"Subject: {certificate.subject.rfc4514_string()}")
            logger.info(f"Válido até: {certificate.not_valid_after.isoformat()}")

        except (CertificateNotFoundError, CertificatePasswordError, CertificateExpiredError):
            raise
        except Exception as e:
            logger.exception("Erro ao carregar certificado A1")
            raise CertificateError(f"Erro ao carregar certificado: {str(e)}") from e

    def load_a3_certificate_windows(self, thumbprint: Optional[str] = None) -> None:
        """
        Carrega certificado A3 do Windows Certificate Store

        Args:
            thumbprint: Thumbprint do certificado (opcional, se None usa o primeiro encontrado)

        Raises:
            NotImplementedError: No Linux (não suporta Windows Certificate Store)
            CertificateNotFoundError: Se nenhum certificado for encontrado
        """
        if sys.platform != "win32":
            raise NotImplementedError(
                "Acesso ao Windows Certificate Store só é suportado no Windows. "
                "No Linux, use certificados A1 (arquivos PFX) exportados do smart card."
            )

        try:
            import win32crypt
            import win32cryptcon

            logger.info("Carregando certificado A3 do Windows Certificate Store")

            # Abrir certificate store
            store = win32crypt.CertOpenStore(
                win32cryptcon.CERT_STORE_PROV_SYSTEM,
                0,
                None,
                win32cryptcon.CERT_SYSTEM_STORE_CURRENT_USER,
                "MY"
            )

            # Procurar certificado
            cert_context = None

            if thumbprint:
                # Buscar por thumbprint específico
                logger.info(f"Buscando certificado com thumbprint: {thumbprint}")
                # TODO: Implementar busca por thumbprint
                raise NotImplementedError("Busca por thumbprint ainda não implementada")
            else:
                # Pegar primeiro certificado disponível
                cert_context = win32crypt.CertEnumCertificatesInStore(store, None)

            if not cert_context:
                raise CertificateNotFoundError("Nenhum certificado encontrado no Windows Certificate Store")

            # Converter para formato cryptography
            cert_bytes = win32crypt.CertSerializeCertificateStoreElement(cert_context, 0)
            certificate = x509.load_der_x509_certificate(cert_bytes, default_backend())

            # Fechar store
            win32crypt.CertCloseStore(store, 0)

            # Verificar validade
            now = datetime.utcnow()
            if certificate.not_valid_after < now:
                raise CertificateExpiredError(
                    f"Certificado expirado em {certificate.not_valid_after.isoformat()}"
                )

            # Armazenar certificado
            self.certificate = certificate
            self.private_key = None  # Chave privada fica no smart card
            self.cert_path = f"Windows Certificate Store (thumbprint: {thumbprint or 'auto'})"

            logger.info("Certificado A3 carregado com sucesso do Windows Certificate Store")
            logger.info(f"Subject: {certificate.subject.rfc4514_string()}")

        except ImportError:
            raise CertificateError(
                "Biblioteca win32crypt não encontrada. Instale pywin32: pip install pywin32"
            )
        except Exception as e:
            logger.exception("Erro ao carregar certificado A3")
            raise CertificateError(f"Erro ao carregar certificado A3: {str(e)}") from e

    def get_certificate_info(self) -> CertificateInfo:
        """
        Obtém informações do certificado carregado

        Returns:
            CertificateInfo: Dados completos do certificado incluindo validade,
                emissor, subject, thumbprint e dias até expiração

        Raises:
            CertificateError: Se nenhum certificado estiver carregado

        Example:
            >>> manager = CertificateManager("A1")
            >>> manager.load_a1_certificate("cert.pfx", "password")
            >>> info = manager.get_certificate_info()
            >>> print(f"Valid until: {info.not_valid_after}")
        """
        if self.certificate is None:
            raise CertificateError("Nenhum certificado carregado")

        # Calcular dias até expiração
        now = datetime.utcnow()
        days_until_expiry = (self.certificate.not_valid_after - now).days

        # Calcular thumbprint (SHA-1 fingerprint)
        thumbprint = self.certificate.fingerprint(hashes.SHA1()).hex().upper()

        # Verificar se está válido
        is_valid = (
                self.certificate.not_valid_before <= now <= self.certificate.not_valid_after
        )

        return CertificateInfo(
            subject=self.certificate.subject.rfc4514_string(),
            issuer=self.certificate.issuer.rfc4514_string(),
            serial_number=str(self.certificate.serial_number),
            not_valid_before=self.certificate.not_valid_before,
            not_valid_after=self.certificate.not_valid_after,
            days_until_expiry=days_until_expiry,
            is_valid=is_valid,
            thumbprint=thumbprint,
            cert_type=self.cert_type
        )

    def validate_certificate(self, warn_days: int = 30) -> Tuple[bool, str]:
        """
        Valida o certificado e retorna status

        Args:
            warn_days: Dias antes da expiração para gerar warning (padrão: 30)

        Returns:
            Tupla (is_valid, message) indicando se certificado é válido e mensagem descritiva

        Examples:
            >>> is_valid, msg = manager.validate_certificate()
            >>> if not is_valid:
            >>>     print(f"Erro: {msg}")
        """
        if self.certificate is None:
            return False, "Nenhum certificado carregado"

        info = self.get_certificate_info()

        # Verificar se expirado
        if not info.is_valid:
            if info.days_until_expiry < 0:
                return False, f"Certificado expirado há {abs(info.days_until_expiry)} dias"
            else:
                return False, f"Certificado ainda não é válido (válido a partir de {info.not_valid_before})"

        # Verificar se está próximo da expiração
        if info.days_until_expiry <= warn_days:
            return True, f"⚠️  Certificado expira em {info.days_until_expiry} dias ({info.not_valid_after.date()})"

        return True, f"✅ Certificado válido por mais {info.days_until_expiry} dias"

    def get_cert_and_key_pem(self) -> Tuple[bytes, bytes]:
        """
        Retorna certificado e chave privada em formato PEM

        Returns:
            Tupla (cert_pem, key_pem) com certificado e chave em formato PEM

        Raises:
            CertificateError: Se certificado ou chave não estiverem carregados
        """
        if self.certificate is None:
            raise CertificateError("Nenhum certificado carregado")

        if self.private_key is None:
            raise CertificateError("Chave privada não disponível (certificado A3 no smart card?)")

        # Serializar certificado para PEM
        cert_pem = self.certificate.public_bytes(serialization.Encoding.PEM)

        # Serializar chave privada para PEM
        key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        return cert_pem, key_pem

    def get_cert_and_key_for_requests(self) -> Tuple[str, str]:
        """
        Retorna paths temporários para certificado e chave para uso com requests library

        Returns:
            Tupla (cert_file_path, key_file_path) com paths dos arquivos temporários

        Raises:
            CertificateError: Se certificado ou chave não estiverem disponíveis

        Note:
            Arquivos temporários devem ser deletados após uso!
        """
        import tempfile

        cert_pem, key_pem = self.get_cert_and_key_pem()

        # Criar arquivos temporários
        cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
        key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')

        try:
            cert_file.write(cert_pem)
            cert_file.close()

            key_file.write(key_pem)
            key_file.close()

            return cert_file.name, key_file.name
        except Exception as e:
            # Limpar em caso de erro
            try:
                os.unlink(cert_file.name)
            except OSError as cleanup_error:
                logger.warning(f"Failed to delete temp cert file: {cleanup_error}")
            try:
                os.unlink(key_file.name)
            except OSError as cleanup_error:
                logger.warning(f"Failed to delete temp key file: {cleanup_error}")
            raise CertificateError(f"Erro ao criar arquivos temporários: {str(e)}") from e

    def __repr__(self) -> str:
        if self.certificate:
            info = self.get_certificate_info()
            return (
                f"CertificateManager(type={self.cert_type}, "
                f"subject={info.subject}, "
                f"valid_until={info.not_valid_after.date()})"
            )
        return f"CertificateManager(type={self.cert_type}, loaded=False)"


# ========================================
# Funções auxiliares
# ========================================

def load_certificate_from_env() -> CertificateManager:
    """
    Carrega certificado usando variáveis de ambiente

    Environment Variables:
        PJE_CERT_TYPE: Tipo de certificado ("A1" ou "A3")
        PJE_CERT_PATH: Caminho para arquivo PFX (para A1)
        PJE_CERT_PASSWORD: Senha do certificado (para A1)
        PJE_CERT_THUMBPRINT: Thumbprint do certificado (para A3, opcional)

    Returns:
        CertificateManager com certificado carregado

    Raises:
        CertificateError: Se variáveis de ambiente não estiverem configuradas ou certificado inválido

    Examples:
        >>> manager = load_certificate_from_env()
        >>> is_valid, msg = manager.validate_certificate()
    """
    cert_type = os.getenv("PJE_CERT_TYPE", "A1")
    manager = CertificateManager(cert_type=cert_type)

    if cert_type == "A1":
        cert_path = os.getenv("PJE_CERT_PATH")
        cert_password = os.getenv("PJE_CERT_PASSWORD")

        if not cert_path:
            raise CertificateError("PJE_CERT_PATH não configurado nas variáveis de ambiente")

        if not cert_password:
            raise CertificateError("PJE_CERT_PASSWORD não configurado nas variáveis de ambiente")

        # Expandir ~ para home directory
        cert_path = os.path.expanduser(cert_path)

        manager.load_a1_certificate(cert_path, cert_password)

    elif cert_type == "A3":
        thumbprint = os.getenv("PJE_CERT_THUMBPRINT")
        manager.load_a3_certificate_windows(thumbprint)

    return manager


def validate_certificate_file(cert_path: str, password: str) -> Tuple[bool, str, Optional[CertificateInfo]]:
    """
    Valida um arquivo de certificado sem carregar permanentemente

    Args:
        cert_path: Caminho para arquivo PFX
        password: Senha do certificado

    Returns:
        Tupla (is_valid, message, info) com status, mensagem e informações do certificado
    """
    try:
        manager = CertificateManager(cert_type="A1")
        manager.load_a1_certificate(cert_path, password)

        is_valid, message = manager.validate_certificate()
        info = manager.get_certificate_info()

        return is_valid, message, info

    except CertificateError as e:
        return False, str(e), None
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}", None
