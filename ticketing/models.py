from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
import uuid


class Match(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    home_team = models.CharField(max_length=100, default='Bo Rangers FC', help_text='Home team name')
    home_team_logo = models.ImageField(upload_to='team_logos/', blank=True, null=True, help_text='Home team logo')
    opponent = models.CharField(max_length=100)
    opponent_logo = models.ImageField(upload_to='team_logos/', blank=True, null=True, help_text='Opponent team logo')
    venue = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    matchday = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Match result fields for completed matches
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    match_summary = models.TextField(blank=True, help_text='Auto-generated match summary')
    highlights = models.TextField(blank=True, help_text='Key moments and highlights')
    attendance = models.PositiveIntegerField(null=True, blank=True)
    weather = models.CharField(max_length=50, blank=True)
    referee = models.CharField(max_length=100, blank=True)
    
    # Statistics fields
    possession_home = models.PositiveIntegerField(null=True, blank=True, help_text='Home team possession percentage')
    possession_away = models.PositiveIntegerField(null=True, blank=True, help_text='Away team possession percentage')
    shots_home = models.PositiveIntegerField(null=True, blank=True)
    shots_away = models.PositiveIntegerField(null=True, blank=True)
    shots_on_target_home = models.PositiveIntegerField(null=True, blank=True)
    shots_on_target_away = models.PositiveIntegerField(null=True, blank=True)
    corners_home = models.PositiveIntegerField(null=True, blank=True)
    corners_away = models.PositiveIntegerField(null=True, blank=True)
    fouls_home = models.PositiveIntegerField(null=True, blank=True)
    fouls_away = models.PositiveIntegerField(null=True, blank=True)
    yellow_cards_home = models.PositiveIntegerField(null=True, blank=True)
    yellow_cards_away = models.PositiveIntegerField(null=True, blank=True)
    red_cards_home = models.PositiveIntegerField(null=True, blank=True)
    red_cards_away = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"{self.title} vs {self.opponent}"
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def result(self):
        if not self.is_completed or self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return 'Win'
        elif self.home_score < self.away_score:
            return 'Loss'
        else:
            return 'Draw'
    
    @property
    def score_display(self):
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_score} - {self.away_score}"
        return "TBD"


class TicketCategory(models.Model):
    name = models.CharField(max_length=50)  # e.g., VIP, Regular
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Ticket Categories"
    
    def __str__(self):
        return f"{self.name} - Nle{self.price}"


class Ticket(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Scanning tracking fields for gateman functionality
    is_scanned = models.BooleanField(default=False)
    scanned_at = models.DateTimeField(null=True, blank=True)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scanned_tickets')

    def save(self, *args, **kwargs):
        # Generate QR code if payment is completed and QR code doesn't exist
        if self.payment_status == 'completed' and not self.qr_code:
            qr_data = f"Ticket ID: {self.ticket_id}\nMatch: {self.match.title}\nUser: {self.user.username}\nCategory: {self.ticket_category.name}\nQuantity: {self.quantity}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to file
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            filename = f'ticket_{self.ticket_id}.png'
            self.qr_code.save(filename, File(buffer), save=False)
        
        super().save(*args, **kwargs)
    
    def total_price(self):
        return self.ticket_category.price * self.quantity
    
    def __str__(self):
        return f"Ticket for {self.match.title} - {self.user.username}"


class News(models.Model):
    CATEGORY_CHOICES = [
        ('match_recap', 'Match Recap'),
        ('press_release', 'Press Release'),
        ('club_news', 'Club News'),
        ('transfer', 'Transfer News'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    video = models.FileField(upload_to='news_videos/', blank=True, null=True, help_text='Upload a video file to accompany the news article')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_posted']
        verbose_name_plural = "News"
    
    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=[('fan', 'Fan'), ('admin', 'Admin'), ('gateman', 'Gateman')], default='fan')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Report(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    tickets_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report for {self.match.title} - {self.tickets_sold} tickets sold"


class MatchEvent(models.Model):
    EVENT_TYPES = [
        ('goal', 'Goal'),
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
        ('substitution', 'Substitution'),
        ('foul', 'Foul'),
        ('corner', 'Corner'),
        ('free_kick', 'Free Kick'),
        ('penalty', 'Penalty'),
        ('injury', 'Injury'),
        ('other', 'Other'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    minute = models.PositiveIntegerField(help_text='Minute of the event')
    team = models.CharField(max_length=10, choices=[('home', 'Home'), ('away', 'Away')])
    player_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    additional_info = models.CharField(max_length=200, blank=True, help_text='Additional details like assist, card reason, etc.')
    
    class Meta:
        ordering = ['minute']
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.player_name} ({self.minute}')"
