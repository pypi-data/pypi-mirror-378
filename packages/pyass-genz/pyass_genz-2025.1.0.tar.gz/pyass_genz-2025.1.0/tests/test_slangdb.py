# pyass🍑/tests/test_slangdb.py

from pyass.core.models import SlangFilter

def test_slangdb_load(slang_db):
    """Test that DB loads correctly"""
    assert len(slang_db) > 0, "DB should have entries"
    assert "rizz" in slang_db, "Should contain 'rizz'"

def test_slangdb_get(slang_db):
    """Test get by term"""
    entry = slang_db.get("rizz")
    assert entry is not None, "Should find 'rizz'"
    assert "charisma" in entry.definition.lower(), "Definition should mention charisma"

def test_slangdb_search(slang_db):
    """Test search with filters"""
    # Search for high popularity US TikTok slang
    filter = SlangFilter(
        min_popularity=90,
        regions=["US"],
        platforms=["TikTok"]
    )
    results = slang_db.search(filter)
    assert len(results) > 0, "Should find some high-popularity US TikTok slang"

def test_slangdb_random(slang_db):
    """Test random generation"""
    entries = slang_db.random(5)
    assert len(entries) == 5, "Should return 5 random entries"

def test_slangdb_stats(slang_db):
    """Test stats generation"""
    stats = slang_db.stats()
    assert stats["total_entries"] > 0, "Should have total entries"
    assert "regions" in stats, "Should have regions stats"
