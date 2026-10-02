from app.personalization.generator import word_count


def test_email_word_count_range():
    text = " ".join(["word"] * 60)
    assert word_count(text) == 60


def test_dm_word_count_range():
    text = " ".join(["word"] * 15)
    assert word_count(text) == 15
