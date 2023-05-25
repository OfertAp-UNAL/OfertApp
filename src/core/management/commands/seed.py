from faker import Faker
from auth.models import User, Admin
from publications.models import Publication, Category, Offer, PublicationSupport
from comments.models import Comment, Reaction
from transactions.models import Transaction, Payment
from notifications.models import Notification
from reports.models import Report, ReportSupport
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

# Useful constants
DEFAULT_SUPPORT_URL = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
DEFAULT_PROFILE_URL = "https://cdn.filestackcontent.com/pLDF5BZTP6ASwiobbC8W"

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

        # Useful for testing purposes
        def generate_user(i):
            username = str(i) + fake.user_name()
            email = str(i) + fake.email()
            password = fake.password()

            print(
                f"Credentials for user {username}, {email} : [{password}]"
            )

            user = User.objects.create(
                id = i,
                firstName = fake.first_name(),
                lastName = fake.last_name(),
                username = username,
                email = email,
                password = make_password(password),
                birthdate = fake.date(),
                address = fake.address(),
                idenIdType = fake.random_element(elements=('CC', 'CE', 'TI', 'PP', 'NIT')),
                phone = str(fake.phone_number()),
                accountType = fake.random_element(elements=('PP', 'EF', 'NQ', 'CD')),
                accountId = i,
                townId = fake.random_element(elements=(
                    1.2, 2.3, 3.4, 4.1, 5.4, 6.2, 7.7, 8.99, 9.10, 10.21
                )),
                verified = True,
                vipState = fake.random_element(elements=(True, False)),
                vipPubCount = fake.random_int(min=0, max=10),
                vipMemberSince = fake.date(),
            )

            # Update user's balance
            user.account.balance = fake.pydecimal(left_digits=13, right_digits=0, positive=True)
            user.account.save()

            return user
        
        users = [
            generate_user(i)
            for i in usersIds
        ]

        # 10% of Users will be admins        
        admins = [
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
        publications = [
            Publication.objects.create(
                title = fake.text(max_nb_chars=45),
                description = fake.text(),
                minOffer = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                endDate = fake.date_time(),
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
        
        self.stdout.write("Seeding Comments.... (10 per Publication)")
        comments = [
            Comment.objects.create(
                text = fake.text(),
                title = fake.text(max_nb_chars=45),
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
                publication = publications[
                    i % number
                ],
                parent = None
            )
            for i in range(number*10)
        ]

        # Relate comments with parents randomly
        _ = [
            Comment.objects.filter(id=comments[i].id).update(
                parent = comments[
                    fake.random_int(min=0, max=i)
                ] if fake.boolean() else None
            )
            for i in range(len(comments) - 1, -1, -1)
        ]

        self.stdout.write("Seeding Reactions.... (number * 100)")
        _ = [
            Reaction.objects.create(
                type = fake.random_element(elements=('LIKE', 'DISLIKE', 'WARNING')),
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
                comment = comments[
                    fake.random_int(min=0, max=len(comments) - 1)
                ]
            )
            for _ in range(number*100)
        ]

        self.stdout.write("Seeding Offers (10 per Publication)")
        offers = [
            Offer.objects.create(
                amount = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
                publication = publications[
                    i % number
                ],
                available = False
            )
            for i in range(number*10)
        ]

        # Update highest offers on each publication and set them as available
        for publication in publications:
            highestOffer = Offer.objects.filter(
                publication = publication
            ).order_by('-amount').first()

            if highestOffer:
                highestOffer.available = True
                highestOffer.save()

        self.stdout.write("Seeding PublicationSupports")
        _ = [
            PublicationSupport.objects.create(
                type = 'VIDEO',
                data = DEFAULT_SUPPORT_URL,
                description = fake.text(),
                publication = publications[
                    fake.random_int(min=0, max=len(publications) - 1)
                ]
            )
            for _ in range(number*10)
        ]

        # Seed payments
        self.stdout.write("Seeding Payments")
        payments = [
            Payment.objects.create(
                type = fake.random_element(elements=('NQ', 'PP')),
                amount = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                flow = fake.random_element(elements=('I', 'O'))
            )
            for _ in range(number*10)
        ]
        # Seed transactions also

        self.stdout.write("Seeding Transactions (Related to offers)")
        _ = [
            Transaction.objects.create(
                amount = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                account = users[i % len(users)].account,
                offer = offers[
                    fake.random_int(min=0, max=len(offers) - 1)
                ],
                type = fake.random_element(elements=('CS', 'BC')),
                description = fake.text( max_nb_chars=45 ),
                prevBalance = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                postBalance = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                prevFrozen = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                postFrozen = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                flow = fake.random_element(elements=('I', 'O'))
            )
            for i in range(number*5)
        ]

        self.stdout.write("Seeding Transactions (Related to payments)")
        _ = [
            Transaction.objects.create(
                amount = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                account = users[i % len(users)].account,
                payment = payments[i],
                type = fake.random_element(elements=('CS', 'BC')),
                description = fake.text( max_nb_chars=45 ),
                prevBalance = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                postBalance = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                prevFrozen = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                postFrozen = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                flow = fake.random_element(elements=('I', 'O'))
            )
            for i in range(number*10)
        ]

        self.stdout.write("Seeding Transactions (Related to admins)")
        _ = [
            Transaction.objects.create(
                amount = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                account = users[i % len(users)].account,
                type = fake.random_element(elements=('CS', 'BC')),
                description = fake.text( max_nb_chars=45 ),
                prevBalance = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                postBalance = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                prevFrozen = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                postFrozen = fake.pydecimal(left_digits=5, right_digits=0, positive=True),
                flow = fake.random_element(elements=('I', 'O')),
                admin = admins[
                    fake.random_int(min=0, max=len(admins) - 1)
                ]
            )
            for i in range(number*5)
        ]

        # Seeding notifications
        self.stdout.write("Seeding Notifications")
        _ = [
            Notification.objects.create(
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
                title = fake.text(max_nb_chars=45),
                description = fake.text(),
                isRead = fake.boolean()
            )
            for _ in range(number*10)
        ]

        # Seeding reports
        self.stdout.write("Seeding Reports")
        reports = [
            Report.objects.create(
                type = fake.random_element(elements=(
                    'DF', 'SF', 'DL', 'MA', 'QF'
                )),
                body = fake.text( max_nb_chars=45 ),
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
                publication = publications[
                    fake.random_int(min=0, max=len(publications) - 1)
                ]
            )
            for _ in range(number*10)
        ]

        # Seeding report supports
        self.stdout.write("Seeding ReportSupports")
        _ = [
            ReportSupport.objects.create(
                user = users[
                    fake.random_int(min=0, max=len(users) - 1)
                ],
                report = reports[
                    fake.random_int(min=0, max=len(reports) - 1)
                ],
                type = "VIDEO",
                data = DEFAULT_SUPPORT_URL,
                body = fake.text( max_nb_chars=45 )
            )
            for _ in range(number*10)
        ]
        
