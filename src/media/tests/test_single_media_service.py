from unittest import TestCase
from unittest.mock import patch, MagicMock

from src.media.models import Media
from src.media.services.single_media.single_media_service import SingleMediaService


class TestSingleMediaService(TestCase):
    @patch('src.media.models.Media.objects')
    @patch('src.user.models.User')
    @patch('src.media.models.Unlock.objects')
    @patch('src.media.services.single_media.single_media_service.AESGCM')
    @patch('os.urandom')
    def test_get_single_media(
            self,
            mock_os_random,
            mock_aesgcm,
            mock_unlock,
            mock_user,
            mock_media
    ):
        media_id = 111
        media = Media()
        media.nonce = b'nonce'
        media.master_key = b'master_key'

        aesgcm_master_instance = MagicMock()
        aesgcm_session_instance = MagicMock()
        mock_aesgcm.side_effect = [aesgcm_master_instance, aesgcm_session_instance]

        # Media.objects.get(pk=media_id)
        mock_media.get.return_value = media
        mock_user.is_authenticated.return_value = True
        # Unlock.objects.filter(user=user, media=media).exists()
        mock_unlock.filter.return_value.exists.return_value = True
        # self.aesgcm.decrypt()
        decrypted_master_key = b'decryptedmasterkey'
        aesgcm_master_instance.decrypt.return_value = decrypted_master_key
        # os.urandom()
        session_key = b'x' * 32
        wrap_nonce = b'a' * 12
        mock_os_random.side_effect = [session_key, wrap_nonce]

        # AESGCM(session_key).encrypt()
        wrapped_master_key = b'encryptedmasterkey'
        aesgcm_session_instance.encrypt.return_value = wrapped_master_key

        service = SingleMediaService()
        result = service.get_single_media(media_id, mock_user)

        self.assertEqual(result.wrapped_master_key, wrapped_master_key)
        self.assertEqual(result.wrap_nonce, wrap_nonce)
        self.assertEqual(result.is_unlocked, True)
        self.assertEqual(result.session_key, session_key)
        aesgcm_master_instance.decrypt.assert_called_once_with(
            nonce=media.nonce,
            data=media.master_key,
            associated_data=None
        )

        aesgcm_session_instance.encrypt.assert_called_once_with(
            nonce=wrap_nonce,
            data=decrypted_master_key,
            associated_data=None
        )
