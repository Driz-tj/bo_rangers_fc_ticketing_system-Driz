from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Match, News


class MatchConsistencyTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test matches
        future_date = timezone.now() + timedelta(days=7)
        past_date = timezone.now() - timedelta(days=7)
        
        # Create upcoming matches
        self.upcoming_match1 = Match.objects.create(
            title="Bo Rangers FC vs Team A",
            date=future_date,
            home_team="Bo Rangers FC",
            opponent="Team A",
            venue="Bo Stadium",
            status="upcoming",
            matchday=1
        )
        
        self.upcoming_match2 = Match.objects.create(
            title="Bo Rangers FC vs Team B",
            date=future_date + timedelta(days=3),
            home_team="Bo Rangers FC",
            opponent="Team B",
            venue="Bo Stadium",
            status="upcoming",
            matchday=2
        )
        
        # Create a completed match
        self.completed_match = Match.objects.create(
            title="Bo Rangers FC vs Team C",
            date=past_date,
            home_team="Bo Rangers FC",
            opponent="Team C",
            venue="Bo Stadium",
            status="completed",
            matchday=3
        )

    def test_upcoming_matches_consistency(self):
        """Test that upcoming matches on home page match fixtures page"""
        # Get home page response
        home_response = self.client.get('/')
        self.assertEqual(home_response.status_code, 200)
        
        # Get fixtures page response with upcoming filter
        fixtures_response = self.client.get('/fixtures/?status=upcoming')
        self.assertEqual(fixtures_response.status_code, 200)
        
        # Extract upcoming matches from home page context
        home_upcoming = home_response.context['upcoming_matches']
        
        # Extract matches from fixtures page context
        fixtures_matches = fixtures_response.context['matches']
        
        # Both should contain the same upcoming matches (home page limits to 3)
        self.assertEqual(len(home_upcoming), 2)  # We have 2 upcoming matches
        self.assertEqual(len(fixtures_matches), 2)  # Fixtures should show all upcoming
        
        # Check that the matches are the same
        home_match_ids = set(match.id for match in home_upcoming)
        fixtures_match_ids = set(match.id for match in fixtures_matches)
        
        self.assertEqual(home_match_ids, fixtures_match_ids)
        
        # Verify that only upcoming matches are shown
        for match in home_upcoming:
            self.assertEqual(match.status, 'upcoming')
        
        for match in fixtures_matches:
            self.assertEqual(match.status, 'upcoming')


class NewsPaginationTest(TestCase):
    def setUp(self):
        """Set up test data for news pagination"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create test news articles
        for i in range(15):  # Create 15 articles to test pagination
            News.objects.create(
                title=f"Test News Article {i+1}",
                body=f"This is the body of test news article {i+1}",
                author=self.user,
                category='general'
            )

    def test_news_pagination(self):
        """Test that news pagination works correctly"""
        # Test first page
        response = self.client.get('/news/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['news_articles']), 10)  # First 10 articles
        self.assertTrue(response.context['has_next'])
        
        # Test second page
        response = self.client.get('/news/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['news_articles']), 5)  # Remaining 5 articles
        self.assertFalse(response.context['has_next'])

    def test_load_more_news_ajax(self):
        """Test the AJAX endpoint for loading more news"""
        response = self.client.get('/load-more-news/?page=2&category=all')
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        import json
        data = json.loads(response.content)
        
        self.assertIn('articles_html', data)
        self.assertIn('has_next', data)
        self.assertFalse(data['has_next'])  # Should be false for page 2 with 15 articles
