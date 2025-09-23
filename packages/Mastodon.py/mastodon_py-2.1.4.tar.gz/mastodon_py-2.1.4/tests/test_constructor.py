import pytest
from mastodon import Mastodon
from mastodon.Mastodon import MastodonIllegalArgumentError

def test_constructor_from_filenames(tmpdir):
    client = tmpdir.join('client')
    client.write_text(u'foo\nbar\n', 'UTF-8')
    access = tmpdir.join('access')
    access.write_text(u'baz\n', 'UTF-8')
    api = Mastodon(
        str(client),
        access_token=str(access),
        api_base_url="mastodon.social"
    )
    assert api.client_id == 'foo'
    assert api.client_secret == 'bar'
    assert api.access_token == 'baz'

def test_constructor_illegal_ratelimit():
    with pytest.raises(MastodonIllegalArgumentError):
        api = Mastodon('foo', client_secret='bar', ratelimit_method='baz', api_base_url="whatever")

def test_constructor_no_url():
    with pytest.raises(MastodonIllegalArgumentError):
        api = Mastodon('foo', client_secret='bar')
        
    with pytest.raises(MastodonIllegalArgumentError):
        api = Mastodon(access_token='baz')

def test_constructor_illegal_versioncheckmode():
    with pytest.raises(MastodonIllegalArgumentError):
        api = Mastodon(
                'foo', client_secret='bar',
                version_check_mode='baz')


def test_constructor_missing_client_secret():
    with pytest.raises(MastodonIllegalArgumentError):
        api = Mastodon('foo')

@pytest.mark.vcr()
def test_verify_version(api):
    assert api.verify_minimum_version("2.3.3") is True
    assert api.verify_minimum_version("9999.9999.9999") is False
    assert api.verify_minimum_version("1.0.0") is True
    
def test_supported_version(api):
    assert Mastodon.get_supported_version()