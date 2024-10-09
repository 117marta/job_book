import factory
from factory.fuzzy import FuzzyChoice

from trades.models import ALL_TRADES, Trade


class TradeFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("sentence", nb_words=3)
    abbreviation = FuzzyChoice(ALL_TRADES)
    slug = factory.Faker("slug")
    description = factory.Faker("text", max_nb_chars=15)

    class Meta:
        model = Trade
        django_get_or_create = ["abbreviation"]
