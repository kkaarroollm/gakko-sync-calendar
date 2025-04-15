from datetime import datetime

import factory

from src.tasks.models import ScrapedTask


class ScrapedTaskFactory(factory.Factory):
    class Meta:
        model = ScrapedTask

    href = factory.Sequence(lambda n: f"/task/{n}")
    title = factory.Faker("sentence", nb_words=3)
    subject = factory.Faker("word")
    due_date = datetime.min
