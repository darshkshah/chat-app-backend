from django.core.management.base import BaseCommand
from users.models import User
from django.utils.timezone import localtime, now
from faker import Faker
import random
from django.utils import timezone
from zoneinfo import ZoneInfo

timezone.activate(ZoneInfo("Asia/Kolkata"))
print(timezone.localtime(timezone.now()))

class Command(BaseCommand):
    help = 'Populate demo data for users.models.User'

    def add_arguments(self, parser):
        parser.add_argument('param', type=int)

    def handle(self, *args, **kwargs):
        # Example demo data
        param = kwargs.get('param')
        fake = Faker('en_IN')
        en_faker = Faker()
        for _ in range(param):
            # print(type(localtime(now())))
            user = User(
                last_login=localtime(now()),
                is_superuser=False,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.user_name(),
                pn_country_code="+91",
                phone_number=fake.msisdn()[:10],
                email=fake.email(),
                bio=en_faker.text(max_nb_chars=random.randint(100, 200)),
                avatar=None,
                online_status=fake.boolean(),
                # created_at=localtime(now()),
                is_active=True,
                is_staff=False
            )
            user.set_password("12345678")
            user.save()
        
        self.stdout.write(self.style.SUCCESS(f'Demo data added successfully for {param} users'))
