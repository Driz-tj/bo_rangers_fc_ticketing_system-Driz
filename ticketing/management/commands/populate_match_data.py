from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ticketing.models import Match, MatchEvent
import random


class Command(BaseCommand):
    help = 'Populate sample match data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample match data...')
        
        # Create some completed matches with data
        completed_matches = [
            {
                'title': 'Bo Rangers FC',
                'opponent': 'East End Lions',
                'date': timezone.now() - timedelta(days=7),
                'venue': 'Bo Stadium',
                'status': 'completed',
                'matchday': 15,
                'home_score': 2,
                'away_score': 1,
                'possession_home': 58,
                'possession_away': 42,
                'shots_home': 12,
                'shots_away': 8,
                'shots_on_target_home': 5,
                'shots_on_target_away': 3,
                'corners_home': 6,
                'corners_away': 4,
                'fouls_home': 8,
                'fouls_away': 12,
                'yellow_cards_home': 2,
                'yellow_cards_away': 3,
                'red_cards_home': 0,
                'red_cards_away': 1,
                'attendance': 8500,
                'weather': 'Sunny',
                'referee': 'John Kamara',
                'match_summary': 'Bo Rangers FC secured a win against East End Lions in a thrilling encounter at Bo Stadium. The final score was 2 - 1. The match was attended by 8,500 passionate fans. Match conditions were Sunny. Bo Rangers had 12 shots compared to 8 from East End Lions. Possession was 58% - 42%.',
                'highlights': '⚽ 3 goals were scored during the match. 🟨 5 yellow cards were shown. 🟥 1 red cards were shown. 🔄 6 substitutions were made. 🎯 8 shots were on target. 🏁 10 corners were awarded.'
            },
            {
                'title': 'Bo Rangers FC',
                'opponent': 'Mighty Blackpool',
                'date': timezone.now() - timedelta(days=14),
                'venue': 'Bo Stadium',
                'status': 'completed',
                'matchday': 14,
                'home_score': 0,
                'away_score': 0,
                'possession_home': 45,
                'possession_away': 55,
                'shots_home': 7,
                'shots_away': 9,
                'shots_on_target_home': 2,
                'shots_on_target_away': 4,
                'corners_home': 3,
                'corners_away': 5,
                'fouls_home': 10,
                'fouls_away': 7,
                'yellow_cards_home': 1,
                'yellow_cards_away': 2,
                'red_cards_home': 0,
                'red_cards_away': 0,
                'attendance': 7200,
                'weather': 'Cloudy',
                'referee': 'Sarah Conteh',
                'match_summary': 'Bo Rangers FC played to a draw with Mighty Blackpool in a thrilling encounter at Bo Stadium. The final score was 0 - 0. The match was attended by 7,200 passionate fans. Match conditions were Cloudy. Bo Rangers had 7 shots compared to 9 from Mighty Blackpool. Possession was 45% - 55%.',
                'highlights': '⚽ 0 goals were scored during the match. 🟨 3 yellow cards were shown. 🔄 4 substitutions were made. 🎯 6 shots were on target. 🏁 8 corners were awarded.'
            },
            {
                'title': 'Bo Rangers FC',
                'opponent': 'Kallon FC',
                'date': timezone.now() - timedelta(days=21),
                'venue': 'Bo Stadium',
                'status': 'completed',
                'matchday': 13,
                'home_score': 3,
                'away_score': 2,
                'possession_home': 52,
                'possession_away': 48,
                'shots_home': 15,
                'shots_away': 11,
                'shots_on_target_home': 7,
                'shots_on_target_away': 5,
                'corners_home': 8,
                'corners_away': 6,
                'fouls_home': 6,
                'fouls_away': 9,
                'yellow_cards_home': 1,
                'yellow_cards_away': 2,
                'red_cards_home': 0,
                'red_cards_away': 0,
                'attendance': 9200,
                'weather': 'Partly Cloudy',
                'referee': 'Michael Sesay',
                'match_summary': 'Bo Rangers FC secured a win against Kallon FC in a thrilling encounter at Bo Stadium. The final score was 3 - 2. The match was attended by 9,200 passionate fans. Match conditions were Partly Cloudy. Bo Rangers had 15 shots compared to 11 from Kallon FC. Possession was 52% - 48%.',
                'highlights': '⚽ 5 goals were scored during the match. 🟨 3 yellow cards were shown. 🔄 5 substitutions were made. 🎯 12 shots were on target. 🏁 14 corners were awarded.'
            }
        ]
        
        # Create or update matches
        for match_data in completed_matches:
            match, created = Match.objects.get_or_create(
                title=match_data['title'],
                opponent=match_data['opponent'],
                date=match_data['date'],
                defaults=match_data
            )
            
            if created:
                self.stdout.write(f'Created match: {match.title} vs {match.opponent}')
            else:
                # Update existing match with new data
                for key, value in match_data.items():
                    setattr(match, key, value)
                match.save()
                self.stdout.write(f'Updated match: {match.title} vs {match.opponent}')
            
            # Create match events for the first match
            if match.opponent == 'East End Lions':
                events_data = [
                    {'event_type': 'goal', 'minute': 12, 'team': 'home', 'player_name': 'Mohamed Kamara', 'description': 'Brilliant header from a corner kick', 'additional_info': 'Assist: John Sesay'},
                    {'event_type': 'yellow_card', 'minute': 23, 'team': 'away', 'player_name': 'David Kargbo', 'description': 'Late tackle', 'additional_info': 'Foul on striker'},
                    {'event_type': 'goal', 'minute': 34, 'team': 'away', 'player_name': 'Ibrahim Conteh', 'description': 'Powerful shot from outside the box', 'additional_info': 'Long range effort'},
                    {'event_type': 'substitution', 'minute': 45, 'team': 'home', 'player_name': 'Ahmed Fofanah', 'description': 'Replaced injured midfielder', 'additional_info': 'Injury substitution'},
                    {'event_type': 'goal', 'minute': 67, 'team': 'home', 'player_name': 'Sulaiman Turay', 'description': 'Clinical finish from close range', 'additional_info': 'Assist: Mohamed Kamara'},
                    {'event_type': 'yellow_card', 'minute': 78, 'team': 'home', 'player_name': 'Patrick Koroma', 'description': 'Professional foul', 'additional_info': 'Stopping counter attack'},
                    {'event_type': 'red_card', 'minute': 89, 'team': 'away', 'player_name': 'Samuel Bangura', 'description': 'Second yellow card', 'additional_info': 'Reckless challenge'},
                ]
                
                for event_data in events_data:
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
                
                self.stdout.write(f'Created {len(events_data)} events for {match.title} vs {match.opponent}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated match data!')) 