from http.client import NOT_FOUND
from drf_spectacular.utils import inline_serializer

from rest_framework import serializers
from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied,
    ValidationError, NotFound
)


PRIVACIES = [
    ('all', 'видно всем'),
    ('not_all', 'видно всем, кроме...'),
    ('no_one_except', 'не видно никому, кроме...'),
    ('nobody', 'не видно никому')
]

NOT_AUTHENTICATED = inline_serializer(
    name='NOT_AUTHENTICATED',
    fields={
        'detail': serializers.CharField(
            default=NotAuthenticated.default_detail
        )
    }
)

PERMISSION_DENIED = inline_serializer(
    name='PERMISSION_DENIED',
    fields={
        'detail': serializers.CharField(
            default=PermissionDenied.default_detail
        )
    }
)

BAD_REQUEST = inline_serializer(
    name='VALIDATION_ERROR',
    fields={
        'detail': serializers.CharField(
            default=ValidationError.default_detail
        )
    }
)

NOT_FOUND = inline_serializer(
    name='NOT_FOUND',
    fields={
        'detail': serializers.CharField(
            default=NotFound.default_detail
        )
    }
)

LANGUAGES = [
    ('arabic', 'Арабский'),
    ('amharic', 'Амхарский'),
    ('english', 'Английский'),
    ('afrikaans', 'Африкаанс'),
    ('albanian', 'Албанский'),
    ('armenian', 'Армянский'),
    ('azerbaijani', 'Азербайджанский'),
    ('bengali', 'Бенгальский'),
    ('belarusian', 'Белорусский'),
    ('burmese', 'Бирманский'),
    ('bulgarian', 'Болгарский'),
    ('bosnian', 'Боснийский'),
    ('catalan', 'Каталанский'),
    ('czech', 'Чешский'),
    ('chinese', 'Китайский'),
    ('danish', 'Датский'),
    ('dari', 'Дари'),
    ('dutch', 'Нидерландский'),
    ('dzongkha', 'Дзонг-кэ'),
    ('estonian', 'Эстонский'),
    ('filipino', 'Филиппинский'),
    ('finnish', 'Финский'),
    ('french', 'Французский'),
    ('georgian', 'Грузинский'),
    ('german', 'Немецкий'),
    ('greek', 'Греческий'),
    ('hebrew', 'Иврит'),
    ('hindi', 'Хинди'),
    ('croatian', 'Хорватский'),
    ('hungarian', 'Венгерский'),
    ('icelandic', 'Исландский'),
    ('indonesian', 'Индонезийский'),
    ('irish', 'Ирландский'),
    ('italian', 'Итальянский'),
    ('japanese', 'Японский'),
    ('kazakh', 'Казахский'),
    ('khmer', 'Кхмерский'),
    ('kinyarwanda', 'Киньяруанда'),
    ('kirundi', 'Кирунди'),
    ('korean', 'Корейский'),
    ('kyrgyz', 'Киргизский'),
    ('lao', 'Лаосский'),
    ('latvian', 'Латышский'),
    ('lithuanian', 'Литовский'),
    ('luxembourgish', 'Люксембургский'),
    ('macedonian', 'Македонский'),
    ('malagasy', 'Малагасийский'),
    ('malay', 'Малайский'),
    ('maltese', 'Мальтийский'),
    ('maori', 'Маори'),
    ('moldovan', 'Молдавский'),
    ('mongolian', 'Монгольский'),
    ('montenegrin', 'Черногорский'),
    ('nepali', 'Непальский'),
    ('norwegian', 'Норвежский'),
    ('pashto', 'Пушту'),
    ('persian', 'Персидский'),
    ('polish', 'Польский'),
    ('portuguese', 'Португальский'),
    ('romanian', 'Румынский'),
    ('russian', 'Русский'),
    ('samoan', 'Самоанский'),
    ('serbian', 'Сербский'),
    ('sinhala', 'Сингальский'),
    ('slovak', 'Словацкий'),
    ('slovene', 'Словенский'),
    ('somali', 'Сомалийский'),
    ('spanish', 'Испанский'),
    ('swahili', 'Суахили'),
    ('swedish', 'Шведский'),
    ('tajik', 'Таджикский'),
    ('tamil', 'Тамильский'),
    ('thai', 'Тайский'),
    ('turkish', 'Турецкий'),
    ('turkmen', 'Туркменский'),
    ('ukrainian', 'Украинский'),
    ('urdu', 'Урду'),
    ('uzbek', 'Узбекский'),
    ('vietnamese', 'Вьетнамский'),
    ('welsh', 'Валлийский'),
    ('berber', 'Берберский'),
    ('quechua', 'Кечуа'),
    ('aymara', 'Аймара'),
    ('guarani', 'Гуарани'),
    ('dhivehi', 'Мальдивский'),
    ('tigrinya', 'Тигринья'),
    ('sesotho', 'Сесото'),
    ('setswana', 'Сетсвана'),
    ('chichewa', 'Чева'),
    ('kurdish', 'Курдский'),
    ('sango', 'Санго'),
    ('tok pisin', 'Ток-писин'),
    ('hiri motu', 'Хири-моту'),
    ('nauruan', 'Науруанский'),
    ('palauan', 'Палауский'),
    ('marshallese', 'Маршалльский'),
    ('kiribati', 'Гилбертский'),
    ('tongan', 'Тонганский'),
    ('fijian', 'Фиджийский'),
    ('bislama', 'Бислама'),
    ('haitian creole', 'Гаитянский креольский'),
    ('tetum', 'Тетум'),
    ('tswana', 'Тсвана'),
    ('swati', 'Свати')
]
