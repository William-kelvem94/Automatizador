# -*- coding: utf-8 -*-

"""
ENCRYPTION MODULE - AES-256 Enterprise Encryption
Criptografia enterprise-grade para dados sensíveis
"""

import os
import base64
import hashlib
import secrets
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.exceptions import InvalidKey, InvalidTag
from ...shared.utils.logger import get_logger


class EncryptionError(Exception):
    """Erro de criptografia"""
    pass


class AESEncryption:
    """Criptografia AES-256 com PBKDF2"""

    # Configurações de segurança enterprise
    KEY_SIZE = 32  # 256 bits
    IV_SIZE = 16   # 128 bits (AES block size)
    SALT_SIZE = 32 # 256 bits
    ITERATIONS = 100000  # PBKDF2 iterations (NIST recommended)

    def __init__(self, master_key: Optional[str] = None):
        """
        Inicializar criptografia

        Args:
            master_key: Chave mestre (base64 encoded). Se None, gera uma nova.
        """
        self.logger = get_logger(__name__)

        if master_key:
            try:
                # Decodificar chave mestre fornecida
                self.master_key = base64.b64decode(master_key)
                if len(self.master_key) != self.KEY_SIZE:
                    raise EncryptionError(f"Master key deve ter {self.KEY_SIZE} bytes")
            except Exception as e:
                raise EncryptionError(f"Chave mestre inválida: {e}")
        else:
            # Gerar nova chave mestre
            self.master_key = secrets.token_bytes(self.KEY_SIZE)
            self.logger.info("Nova chave mestre gerada")

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derivar chave usando PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))

    def encrypt(self, plaintext: str, password: Optional[str] = None) -> Dict[str, str]:
        """
        Criptografar dados

        Args:
            plaintext: Texto a criptografar
            password: Senha para derivação de chave (opcional)

        Returns:
            Dict com dados criptografados
        """
        try:
            # Gerar salt e IV
            salt = secrets.token_bytes(self.SALT_SIZE)
            iv = secrets.token_bytes(self.IV_SIZE)

            # Derivar chave
            if password:
                key = self._derive_key(password, salt)
            else:
                key = self.master_key

            # Preparar dados para criptografia
            data = plaintext.encode('utf-8')

            # Adicionar padding
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()

            # Criptografar
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            # Codificar para base64
            encrypted_data = {
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                'salt': base64.b64encode(salt).decode('utf-8'),
                'iv': base64.b64encode(iv).decode('utf-8'),
                'version': '1.0'
            }

            # Adicionar hash para verificação de integridade
            data_to_hash = encrypted_data['ciphertext'] + encrypted_data['iv']
            integrity_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
            encrypted_data['integrity_hash'] = integrity_hash

            return encrypted_data

        except Exception as e:
            self.logger.error(f"Erro na criptografia: {e}")
            raise EncryptionError(f"Falha na criptografia: {e}")

    def decrypt(self, encrypted_data: Dict[str, str], password: Optional[str] = None) -> str:
        """
        Descriptografar dados

        Args:
            encrypted_data: Dados criptografados
            password: Senha para derivação de chave (opcional)

        Returns:
            Texto descriptografado
        """
        try:
            # Validar estrutura dos dados
            required_fields = ['ciphertext', 'salt', 'iv', 'integrity_hash']
            for field in required_fields:
                if field not in encrypted_data:
                    raise EncryptionError(f"Campo obrigatório faltando: {field}")

            # Decodificar dados
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            salt = base64.b64decode(encrypted_data['salt'])
            iv = base64.b64decode(encrypted_data['iv'])

            # Verificar integridade
            data_to_hash = encrypted_data['ciphertext'] + encrypted_data['iv']
            expected_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
            if expected_hash != encrypted_data['integrity_hash']:
                raise EncryptionError("Dados corrompidos ou alterados")

            # Derivar chave
            if password:
                key = self._derive_key(password, salt)
            else:
                key = self.master_key

            # Descriptografar
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remover padding
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

            return plaintext.decode('utf-8')

        except Exception as e:
            self.logger.error(f"Erro na descriptografia: {e}")
            raise EncryptionError(f"Falha na descriptografia: {e}")

    def get_master_key_b64(self) -> str:
        """Obter chave mestre em base64 (para backup)"""
        return base64.b64encode(self.master_key).decode('utf-8')

    def rotate_key(self, new_master_key: Optional[str] = None) -> str:
        """
        Rotacionar chave mestre

        Args:
            new_master_key: Nova chave (opcional)

        Returns:
            Nova chave em base64
        """
        if new_master_key:
            # Usar chave fornecida
            self.master_key = base64.b64decode(new_master_key)
        else:
            # Gerar nova chave
            self.master_key = secrets.token_bytes(self.KEY_SIZE)

        self.logger.info("Chave mestre rotacionada")
        return self.get_master_key_b64()

    @staticmethod
    def generate_secure_password(length: int = 32) -> str:
        """Gerar senha segura aleatória"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde da criptografia"""
        try:
            # Teste básico de criptografia
            test_data = "test_encryption_data"
            encrypted = self.encrypt(test_data)
            decrypted = self.decrypt(encrypted)

            if decrypted != test_data:
                raise EncryptionError("Teste de criptografia falhou")

            return {
                'status': 'healthy',
                'algorithm': 'AES-256-CBC',
                'key_derivation': 'PBKDF2-SHA256',
                'iterations': self.ITERATIONS,
                'master_key_configured': True
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class DataEncryptionManager:
    """Gerenciador de criptografia para diferentes tipos de dados"""

    def __init__(self, encryption: AESEncryption):
        self.encryption = encryption
        self.logger = get_logger(__name__)

    def encrypt_credentials(self, username: str, password: str) -> Dict[str, str]:
        """Criptografar credenciais de usuário"""
        data = f"{username}:{password}"
        encrypted = self.encryption.encrypt(data)
        encrypted['type'] = 'credentials'
        return encrypted

    def decrypt_credentials(self, encrypted_data: Dict[str, str]) -> tuple[str, str]:
        """Descriptografar credenciais"""
        if encrypted_data.get('type') != 'credentials':
            raise EncryptionError("Tipo de dados incorreto")

        data = self.encryption.decrypt(encrypted_data)
        username, password = data.split(':', 1)
        return username, password

    def encrypt_task_data(self, task_data: Dict[str, Any]) -> Dict[str, str]:
        """Criptografar dados de tarefa (senhas, tokens, etc.)"""
        import json

        # Identificar campos sensíveis
        sensitive_fields = ['password', 'token', 'secret', 'key', 'credentials']

        # Criptografar apenas campos sensíveis
        data_to_encrypt = {}
        for field in sensitive_fields:
            if field in task_data and task_data[field]:
                data_to_encrypt[field] = task_data[field]

        if not data_to_encrypt:
            # Nada para criptografar
            return {'encrypted': False, 'data': json.dumps(task_data)}

        # Criptografar dados sensíveis
        json_data = json.dumps(data_to_encrypt, ensure_ascii=False)
        encrypted = self.encryption.encrypt(json_data)
        encrypted['type'] = 'task_data'
        encrypted['encrypted_fields'] = list(data_to_encrypt.keys())

        return encrypted

    def decrypt_task_data(self, encrypted_data: Dict[str, str], base_task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Descriptografar dados de tarefa"""
        if encrypted_data.get('encrypted') == False:
            # Dados não criptografados
            import json
            return json.loads(encrypted_data['data'])

        if encrypted_data.get('type') != 'task_data':
            raise EncryptionError("Tipo de dados incorreto")

        # Descriptografar
        json_data = self.encryption.decrypt(encrypted_data)
        decrypted_data = json.loads(json_data)

        # Mesclar com dados base
        result = base_task_data.copy()
        result.update(decrypted_data)

        return result

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Criptografar arquivo"""
        if not os.path.exists(file_path):
            raise EncryptionError(f"Arquivo não encontrado: {file_path}")

        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Criptografar conteúdo
        b64_data = base64.b64encode(file_data).decode('utf-8')
        encrypted = self.encryption.encrypt(b64_data)
        encrypted['type'] = 'file'
        encrypted['original_filename'] = os.path.basename(file_path)

        # Salvar arquivo criptografado
        if not output_path:
            output_path = file_path + '.encrypted'

        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(encrypted, f, indent=2, ensure_ascii=False)

        return output_path

    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """Descriptografar arquivo"""
        if not os.path.exists(encrypted_file_path):
            raise EncryptionError(f"Arquivo criptografado não encontrado: {encrypted_file_path}")

        import json
        with open(encrypted_file_path, 'r', encoding='utf-8') as f:
            encrypted_data = json.load(f)

        if encrypted_data.get('type') != 'file':
            raise EncryptionError("Tipo de arquivo incorreto")

        # Descriptografar
        b64_data = self.encryption.decrypt(encrypted_data)
        file_data = base64.b64decode(b64_data)

        # Salvar arquivo descriptografado
        if not output_path:
            original_name = encrypted_data.get('original_filename', 'decrypted_file')
            output_path = os.path.join(os.path.dirname(encrypted_file_path), original_name)

        with open(output_path, 'wb') as f:
            f.write(file_data)

        return output_path
