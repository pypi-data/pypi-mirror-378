import pytest

@pytest.mark.vcr()
def test_bookmarks(api, status):
    status_bookmarked = api.status_bookmark(status)
    assert status_bookmarked
    assert status_bookmarked.bookmarked
    
    bookmarked_statuses = api.bookmarks()
    assert bookmarked_statuses
    assert len(bookmarked_statuses) > 0
    assert status_bookmarked == bookmarked_statuses[0]
    
    bookmarked_statuses = api.bookmarks(limit=1)
    assert bookmarked_statuses
    assert len(bookmarked_statuses) > 0
    assert status_bookmarked == bookmarked_statuses[0]

    status_unbookmarked = api.status_unbookmark(status_bookmarked)
    assert status_unbookmarked
    assert not status_unbookmarked.bookmarked
    
    bookmarked_statuses_2 = api.bookmarks()
    assert bookmarked_statuses_2 is not None
    assert len(bookmarked_statuses_2) == len(bookmarked_statuses) - 1
    
