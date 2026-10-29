"""Offline safety tests for the new V55 Met Open Access acquisition step."""
import hashlib
import json
import pytest
from PIL import Image
from src import artvision_met_prepared_assets_v55 as mod

META = {'objectID': 436105, 'isPublicDomain': True, 'title': 'The Death of Socrates',
        'artistDisplayName': 'Jacques Louis David', 'objectDate': '1787',
        'dimensions': '129.5 x 196.2 cm',
        'primaryImage': 'https://images.metmuseum.org/CRDImages/ep/original/DT1502.jpg'}


def test_rejects_wrong_object_and_rights(tmp_path):
    for changed in ({'objectID': 11122}, {'isPublicDomain': False}, {'title': 'Different painting'},
                    {'artistDisplayName': 'Other artist'}, {'primaryImage': 'https://evil.example/image.jpg'}):
        meta = {**META, **changed}
        with pytest.raises(ValueError):
            mod.prepare(436105, tmp_path/'assets', expected_title='The Death of Socrates',
                        expected_artist='Jacques Louis David', metadata=meta)
        assert not (tmp_path/'assets').exists()


def test_refuses_existing_destination(tmp_path):
    dest = tmp_path/'assets'
    dest.mkdir()
    with pytest.raises(FileExistsError):
        mod.prepare(436105, dest, expected_title='The Death of Socrates',
                    expected_artist='Jacques Louis David', metadata=META)


def test_rejects_redirect_to_untrusted_host(tmp_path):
    class Response:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def geturl(self): return 'https://evil.example/fake.jpg'
    with pytest.raises(ValueError):
        mod.download(META['primaryImage'], tmp_path/'image.jpg',
                     {'images.metmuseum.org'}, 1_000_000, opener=lambda *a, **k: Response())
    assert not (tmp_path/'image.jpg').exists()


def test_happy_path_pinned_hash_without_network(tmp_path, monkeypatch):
    def fake_fetch(url, path, hosts, max_bytes):
        if path.suffix == '.jpg':
            Image.new('RGB', (1300, 1000), (23, 43, 55)).save(path)
        else:
            path.write_bytes(b'original-audio-fixture')
        return path
    monkeypatch.setattr(mod, 'MUSIC_SHA256', hashlib.sha256(b'original-audio-fixture').hexdigest())
    result = mod.prepare(436105, tmp_path/'assets', expected_title='The Death of Socrates',
                         expected_artist='Jacques Louis David', metadata=META, fetcher=fake_fetch)
    assert result['status'] == 'assets_verified_only'
    assert result['rendered_mp4'] is False and result['v25_approved'] is False
    assert result['artwork']['width_px'] == 1300
    assert json.loads((tmp_path/'assets'/'PREPARED_ASSETS_V55.json').read_text()) == result
