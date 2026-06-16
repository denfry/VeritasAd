from corpus.erid_miner import mine_disclosure
from corpus.schema import MarkerType


def _types(text):
    return {m.marker_type for m in mine_disclosure(text)}


def test_erid_token_is_extracted_with_value():
    matches = mine_disclosure("Спасибо за просмотр. erid: 2Vfnxw9aBcd")
    erid = [m for m in matches if m.marker_type == MarkerType.ERID]
    assert len(erid) == 1
    assert erid[0].value == "2Vfnxw9aBcd"


def test_erid_with_equals_sign():
    assert MarkerType.ERID in _types("ссылка erid=LjN8KabcDE подробнее")


def test_phrase_na_pravah_reklamy():
    assert MarkerType.PHRASE_AD in _types("Это видео на правах рекламы.")


def test_hashtag_reklama():
    assert MarkerType.HASHTAG_AD in _types("Купите тут #реклама")


def test_advertiser_inn():
    text = "Реклама. Рекламодатель ООО Ромашка ИНН 7701234567"
    assert MarkerType.ADVERTISER_INN in _types(text)


def test_promo_code_value():
    matches = mine_disclosure("Промокод SALE20 даёт скидку")
    promo = [m for m in matches if m.marker_type == MarkerType.PROMO_CODE]
    assert promo and promo[0].value == "SALE20"


def test_sponsor_phrase_is_weak_only():
    types = _types("Выпуск при поддержке нашего друга")
    assert MarkerType.SPONSOR_PHRASE in types
    assert MarkerType.ERID not in types


def test_clean_text_has_no_markers():
    assert mine_disclosure("Сегодня я гулял в парке и пил кофе") == []


def test_empty_text():
    assert mine_disclosure("") == []
