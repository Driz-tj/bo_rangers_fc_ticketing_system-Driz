from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ticketing.models import Match, TicketCategory, News, UserProfile, Ticket, Report
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for Bo Rangers FC'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create superuser if it doesn't exist
        self.create_superuser()
        
        # Create ticket categories
        self.create_ticket_categories()
        
        # Create sample users
        self.create_sample_users()
        
        # Create matches
        self.create_matches()
        
        # Create news articles
        self.create_news_articles()
        
        # Create sample tickets and reports
        self.create_sample_tickets()
        
        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))

    def create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@borangersfc.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            UserProfile.objects.create(
                user=admin_user,
                phone='23276123456',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
        else:
            self.stdout.write('Superuser already exists')

    def create_ticket_categories(self):
        categories = [
            {'name': 'VIP', 'price': 50.00, 'description': 'Premium seating with exclusive amenities'},
            {'name': 'Regular', 'price': 20.00, 'description': 'Standard stadium seating'},
        ]
        
        for cat_data in categories:
            category, created = TicketCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'price': cat_data['price'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created ticket category: {category.name}')

    def create_sample_users(self):
        sample_users = [
            {'username': 'john_fan', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'phone': '23276111111'},
            {'username': 'mary_supporter', 'email': 'mary@example.com', 'first_name': 'Mary', 'last_name': 'Smith', 'phone': '23276222222'},
            {'username': 'david_rangers', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Johnson', 'phone': '23276333333'},
            {'username': 'sarah_fc', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Wilson', 'phone': '23276444444'},
        ]
        
        for user_data in sample_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='password123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                UserProfile.objects.create(
                    user=user,
                    phone=user_data['phone'],
                    role='fan'
                )
                self.stdout.write(f'Created user: {user.username}')

    def create_matches(self):
        now = timezone.now()
        
        matches = [
            # Past matches
            {
                'title': 'Bo Rangers FC vs Mighty Blackpool',
                'opponent': 'Mighty Blackpool',
                'date': now - timedelta(days=30),
                'venue': 'Bo Stadium',
                'status': 'completed',
                'matchday': 1
            },
            {
                'title': 'Bo Rangers FC vs East End Lions',
                'opponent': 'East End Lions',
                'date': now - timedelta(days=20),
                'venue': 'National Stadium',
                'status': 'completed',
                'matchday': 2
            },
            {
                'title': 'Bo Rangers FC vs FC Kallon',
                'opponent': 'FC Kallon',
                'date': now - timedelta(days=10),
                'venue': 'Bo Stadium',
                'status': 'completed',
                'matchday': 3
            },
            # Upcoming matches
            {
                'title': 'Bo Rangers FC vs Real Republicans',
                'opponent': 'Real Republicans',
                'date': now + timedelta(days=7),
                'venue': 'Bo Stadium',
                'status': 'upcoming',
                'matchday': 4
            },
            {
                'title': 'Bo Rangers FC vs Ports Authority',
                'opponent': 'Ports Authority',
                'date': now + timedelta(days=14),
                'venue': 'National Stadium',
                'status': 'upcoming',
                'matchday': 5
            },
            {
                'title': 'Bo Rangers FC vs Diamond Stars',
                'opponent': 'Diamond Stars',
                'date': now + timedelta(days=21),
                'venue': 'Bo Stadium',
                'status': 'upcoming',
                'matchday': 6
            },
            {
                'title': 'Bo Rangers FC vs Freetown City FC',
                'opponent': 'Freetown City FC',
                'date': now + timedelta(days=28),
                'venue': 'National Stadium',
                'status': 'upcoming',
                'matchday': 7
            },
        ]
        
        for match_data in matches:
            match, created = Match.objects.get_or_create(
                title=match_data['title'],
                defaults=match_data
            )
            if created:
                self.stdout.write(f'Created match: {match.title}')

    def create_news_articles(self):
        admin_user = User.objects.get(username='admin')
        
        articles = [
            {
                'title': 'Bo Rangers FC Wins Against Mighty Blackpool 2-1',
                'body': '''Bo Rangers FC secured a thrilling 2-1 victory against Mighty Blackpool in front of a packed Bo Stadium crowd. 
                
The match started with high intensity as both teams looked to take control early. Bo Rangers took the lead in the 25th minute through a brilliant strike from midfielder James Kamara, who found the top corner after a well-worked team move.

Mighty Blackpool equalized just before halftime with a header from their captain, making it 1-1 at the break. The second half was a tense affair with both teams creating chances.

The winning goal came in the 78th minute when striker Mohamed Bangura capitalized on a defensive error to slot home from close range, sending the home crowd into raptures.

Manager John Smith praised the team's resilience: "I'm proud of how the boys fought back. This shows the character we have in this squad."

The victory moves Bo Rangers FC to 2nd place in the league table with 25 points from 12 matches.''',
                'category': 'match_recap',
                'is_featured': True,
                'author': admin_user
            },
            {
                'title': 'New Signing: Bo Rangers FC Welcomes Striker Abdul Kamara',
                'body': '''Bo Rangers FC is delighted to announce the signing of striker Abdul Kamara from East End Lions on a two-year contract.

The 24-year-old forward brings pace, skill, and a proven goal-scoring record to the team. Last season, Kamara scored 15 goals in 20 appearances for East End Lions.

"I'm excited to join Bo Rangers FC and contribute to the team's success," said Kamara. "The club has a great history and passionate fans. I can't wait to get started."

Manager John Smith commented: "Abdul is exactly the type of player we've been looking for. His pace and finishing ability will add a new dimension to our attack."

Kamara will wear jersey number 9 and is expected to make his debut in the upcoming match against Real Republicans.''',
                'category': 'transfer',
                'is_featured': False,
                'author': admin_user
            },
            {
                'title': 'Bo Rangers FC Foundation Launches Youth Development Program',
                'body': '''The Bo Rangers FC Foundation has launched an ambitious youth development program aimed at nurturing young talent in the Bo District.

The program will provide free coaching, equipment, and educational support to children aged 8-16. Professional coaches from the first team will conduct weekly training sessions.

"We believe in giving back to our community," said Foundation Director Sarah Johnson. "This program will help develop the next generation of Sierra Leonean football stars."

The initiative is supported by local businesses and international partners. Registration is now open for interested young players.

Training sessions will take place every Saturday at the Bo Rangers FC training ground. For more information, contact the Foundation office.''',
                'category': 'club_news',
                'is_featured': True,
                'author': admin_user
            },
            {
                'title': 'Match Preview: Bo Rangers FC vs Real Republicans',
                'body': '''Bo Rangers FC will host Real Republicans this Saturday in what promises to be an exciting encounter at Bo Stadium.

The Rangers come into this match on the back of a convincing 2-1 victory over Mighty Blackpool, while Real Republicans secured a 1-0 win against FC Kallon in their last outing.

Key players to watch include Bo Rangers' top scorer Mohamed Bangura, who has netted 8 goals this season, and Real Republicans' creative midfielder Joseph Conteh.

Manager John Smith expects a tough match: "Real Republicans are a well-organized team with quality players. We need to be at our best to get the three points."

Tickets are still available for the match, which kicks off at 4:00 PM. The club expects a sell-out crowd for this crucial league encounter.''',
                'category': 'general',
                'is_featured': False,
                'author': admin_user
            },
            {
                'title': 'Stadium Renovation Project Update',
                'body': '''The Bo Stadium renovation project is progressing well, with the new VIP section expected to be completed by the end of the month.

The renovation includes upgraded seating, improved lighting, and enhanced security features. The project aims to increase the stadium's capacity to 8,000 spectators.

"We're committed to providing the best possible experience for our fans," said Club President Mohamed Sesay. "These improvements will make Bo Stadium one of the finest in Sierra Leone."

The renovation is being funded through a combination of club resources, government support, and private donations. Local contractors are being employed to ensure community involvement.

Phase two of the project, which includes new changing rooms and media facilities, is scheduled to begin next year.''',
                'category': 'club_news',
                'is_featured': False,
                'author': admin_user
            }
        ]
        
        for article_data in articles:
            article, created = News.objects.get_or_create(
                title=article_data['title'],
                defaults=article_data
            )
            if created:
                self.stdout.write(f'Created news article: {article.title}')

    def create_sample_tickets(self):
        # Get completed matches and sample users
        completed_matches = Match.objects.filter(status='completed')
        users = User.objects.filter(userprofile__role='fan')
        categories = TicketCategory.objects.all()
        
        if not users.exists() or not categories.exists():
            self.stdout.write(self.style.WARNING('No users or categories found for ticket creation'))
            return
        
        # Create tickets for completed matches
        for match in completed_matches:
            # Create 3-8 tickets per match
            num_tickets = random.randint(3, 8)
            
            for _ in range(num_tickets):
                user = random.choice(users)
                category = random.choice(categories)
                quantity = random.randint(1, 4)
                
                ticket = Ticket.objects.create(
                    user=user,
                    match=match,
                    ticket_category=category,
                    quantity=quantity,
                    payment_status='completed'
                )
                
                # Create or update report
                report, created = Report.objects.get_or_create(
                    match=match,
                    defaults={'tickets_sold': 0, 'revenue': 0}
                )
                report.tickets_sold += quantity
                report.revenue += ticket.total_price()
                report.save()
            
            self.stdout.write(f'Created {num_tickets} tickets for {match.title}')
        
        # Create some pending tickets for upcoming matches
        upcoming_matches = Match.objects.filter(status='upcoming')[:2]
        for match in upcoming_matches:
            num_tickets = random.randint(1, 3)
            
            for _ in range(num_tickets):
                user = random.choice(users)
                category = random.choice(categories)
                quantity = random.randint(1, 2)
                
                Ticket.objects.create(
                    user=user,
                    match=match,
                    ticket_category=category,
                    quantity=quantity,
                    payment_status='pending'
                )
            
            self.stdout.write(f'Created {num_tickets} pending tickets for {match.title}')
