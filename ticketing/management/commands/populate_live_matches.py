from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ticketing.models import Match, MatchEvent
import random


class Command(BaseCommand):
    help = 'Populate sample live matches for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample live matches...')
        
        # Create some live matches with data
        live_matches = [
            {
                'title': 'Bo Rangers FC',
                'opponent': 'Ports Authority',
                'date': timezone.now() - timedelta(hours=1),  # Started 1 hour ago
                'venue': 'Bo Stadium',
                'status': 'live',
                'matchday': 16,
                'home_score': 1,
                'away_score': 0,
                'possession_home': 52,
                'possession_away': 48,
                'shots_home': 8,
                'shots_away': 5,
                'shots_on_target_home': 3,
                'shots_on_target_away': 2,
                'corners_home': 4,
                'corners_away': 3,
                'fouls_home': 6,
                'fouls_away': 8,
                'yellow_cards_home': 1,
                'yellow_cards_away': 2,
                'red_cards_home': 0,
                'red_cards_away': 0,
                'attendance': 7800,
                'weather': 'Partly Cloudy',
                'referee': 'Fatima Kamara',
            },
            {
                'title': 'Bo Rangers FC',
                'opponent': 'Central Parade',
                'date': timezone.now() - timedelta(minutes=30),  # Started 30 minutes ago
                'venue': 'Bo Stadium',
                'status': 'live',
                'matchday': 17,
                'home_score': 2,
                'away_score': 1,
                'possession_home': 58,
                'possession_away': 42,
                'shots_home': 12,
                'shots_away': 7,
                'shots_on_target_home': 5,
                'shots_on_target_away': 3,
                'corners_home': 6,
                'corners_away': 4,
                'fouls_home': 5,
                'fouls_away': 9,
                'yellow_cards_home': 0,
                'yellow_cards_away': 1,
                'red_cards_home': 0,
                'red_cards_away': 0,
                'attendance': 9200,
                'weather': 'Sunny',
                'referee': 'John Conteh',
            }
        ]
        
        # Create or update live matches
        for match_data in live_matches:
            match, created = Match.objects.get_or_create(
                title=match_data['title'],
                opponent=match_data['opponent'],
                date=match_data['date'],
                defaults=match_data
            )
            
            if created:
                self.stdout.write(f'Created live match: {match.title} vs {match.opponent}')
            else:
                # Update existing match with live data
                for key, value in match_data.items():
                    setattr(match, key, value)
                match.save()
                self.stdout.write(f'Updated live match: {match.title} vs {match.opponent}')
            
            # Create live match events
            if match.opponent == 'Ports Authority':
                live_events = [
                    {'event_type': 'goal', 'minute': 45, 'team': 'home', 'player_name': 'Mohamed Kamara', 'description': 'Brilliant header from a corner kick', 'additional_info': 'Assist: John Sesay'},
                    {'event_type': 'yellow_card', 'minute': 43, 'team': 'away', 'player_name': 'David Kargbo', 'description': 'Late tackle', 'additional_info': 'Foul on striker'},
                    {'event_type': 'substitution', 'minute': 40, 'team': 'home', 'player_name': 'Ahmed Fofanah', 'description': 'Replaced injured midfielder', 'additional_info': 'Injury substitution'},
                    {'event_type': 'yellow_card', 'minute': 35, 'team': 'away', 'player_name': 'Samuel Bangura', 'description': 'Professional foul', 'additional_info': 'Stopping counter attack'},
                    {'event_type': 'goal', 'minute': 30, 'team': 'away', 'player_name': 'Ibrahim Conteh', 'description': 'Disallowed goal - Offside', 'additional_info': 'VAR decision'},
                ]
            else:  # Central Parade match
                live_events = [
                    {'event_type': 'goal', 'minute': 25, 'team': 'home', 'player_name': 'Sulaiman Turay', 'description': 'Clinical finish from close range', 'additional_info': 'Assist: Mohamed Kamara'},
                    {'event_type': 'goal', 'minute': 40, 'team': 'away', 'player_name': 'Patrick Koroma', 'description': 'Equalizer from a free kick', 'additional_info': 'Direct free kick'},
                    {'event_type': 'goal', 'minute': 55, 'team': 'home', 'player_name': 'Ahmed Fofanah', 'description': 'Spectacular long-range shot', 'additional_info': '30-yard strike'},
                    {'event_type': 'yellow_card', 'minute': 50, 'team': 'home', 'player_name': 'John Sesay', 'description': 'Late challenge', 'additional_info': 'Tactical foul'},
                    {'event_type': 'substitution', 'minute': 60, 'team': 'away', 'player_name': 'Michael Kargbo', 'description': 'Fresh legs for attack', 'additional_info': 'Attacking substitution'},
                ]
            
            for event_data in live_events:
                MatchEvent.objects.get_or_create(
                    match=match,
                    minute=event_data['minute'],
                    event_type=event_data['event_type'],
                    team=event_data['team'],
                    player_name=event_data['player_name'],
                    defaults={
                        'description': event_data['description'],
                        'additional_info': event_data['additional_info']
                    }
                )
            
            self.stdout.write(f'Created {len(live_events)} live events for {match.title} vs {match.opponent}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated live matches!')) 