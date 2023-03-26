from faker import Faker
from auth.models import User, Admin
from publications.models import Publication, Category
from django.core.management.base import BaseCommand
    
class Command(BaseCommand):
    
    help = "Seed elements to database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            help='Number of elements to seed'
        )

    def handle(self, *args, **options):
        self.stdout.write("Seeding data")

        number = options.get('number', 10)
            
        fake = Faker(
            ['es_ES']
        )

        usersIds = [ i for i in range(1, number + 1) ]

        # Users seeding
        self.stdout.write("Seeding Users....")
        users = [
            User.objects.create(
                id = i,
                firstName = fake.first_name(),
                lastName = fake.last_name(),
                username = str(i) + fake.user_name(),
                email = str(i) + fake.email(),
                password = fake.password(),
                birthdate = fake.date(),
                address = fake.address(),
                idenIdType = fake.random_element(elements=('CC', 'CE', 'TI', 'PP', 'NIT')),
                phone = str(fake.phone_number()),
                accountType = fake.random_element(elements=('PP', 'EF', 'NQ', 'CD')),
                accountId = i,
                townId = fake.random_element(elements=(
                    1.2, 2.3, 3.4, 4.1, 5.4, 6.2, 7.7, 8.99, 9.10, 10.21
                )),
                verified = True
            )
            for i in usersIds
        ]

        # 10% of Users will be admins        
        _ = [
            Admin.objects.create(
                user = users[i],
                hiredDate = fake.date()
            )
            for i in usersIds[:int(number * 0.1)]
        ]

        self.stdout.write("Seeding Categories (10% of Publications)....")
        
        categories = [
            Category.objects.create(
                name = fake.word()
            )
            for _ in range(int(number * 0.1))
        ]

        self.stdout.write("Seeding Publications....")
        _ = [
            Publication.objects.create(
                title = fake.text(max_nb_chars=45),
                description = fake.text(),
                minOffer = fake.pydecimal(left_digits=13, right_digits=0, positive=True),
                endDate = fake.date(),
                available = fake.boolean(),
                reportable = fake.boolean(),
                category = categories[ 
                    fake.random_int(min=0, max=len(categories) - 1)
                ],
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
            )
            for _ in range(number)
        ]
            