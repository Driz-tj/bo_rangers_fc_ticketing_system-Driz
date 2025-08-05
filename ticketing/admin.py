from django.contrib import admin
from django.utils.html import format_html
from .models import Match, TicketCategory, Ticket, News, UserProfile, Report, MatchEvent


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['title', 'opponent', 'date', 'venue', 'status', 'matchday', 'score_display', 'result', 'tickets_sold']
    list_filter = ['status', 'date', 'venue']
    search_fields = ['title', 'opponent', 'venue']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Match Information', {
            'fields': ('title', 'opponent', 'date', 'venue', 'matchday')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Match Results', {
            'fields': ('home_score', 'away_score', 'match_summary', 'highlights', 'attendance', 'weather', 'referee'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'possession_home', 'possession_away',
                'shots_home', 'shots_away', 'shots_on_target_home', 'shots_on_target_away',
                'corners_home', 'corners_away',
                'fouls_home', 'fouls_away',
                'yellow_cards_home', 'yellow_cards_away',
                'red_cards_home', 'red_cards_away'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def score_display(self, obj):
        return obj.score_display
    score_display.short_description = "Score"
    
    def result(self, obj):
        if obj.result:
            color = 'green' if obj.result == 'Win' else 'red' if obj.result == 'Loss' else 'orange'
            return format_html('<span style="color: {};">{}</span>', color, obj.result)
        return '-'
    result.short_description = "Result"
    
    def tickets_sold(self, obj):
        count = obj.ticket_set.filter(payment_status='completed').count()
        return f"{count} tickets"
    tickets_sold.short_description = "Tickets Sold"


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ['match', 'event_type', 'minute', 'team', 'player_name', 'description']
    list_filter = ['event_type', 'team', 'match']
    search_fields = ['player_name', 'description', 'match__title']
    ordering = ['match', 'minute']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('match', 'event_type', 'minute', 'team', 'player_name')
        }),
        ('Details', {
            'fields': ('description', 'additional_info')
        }),
    )


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description']
    search_fields = ['name']
    ordering = ['price']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id_short', 'user', 'match', 'ticket_category', 'quantity', 'payment_status', 'created_at']
    list_filter = ['payment_status', 'ticket_category', 'created_at']
    search_fields = ['user__username', 'match__title', 'ticket_id']
    readonly_fields = ['ticket_id', 'qr_code', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('user', 'match', 'ticket_category', 'quantity')
        }),
        ('Payment', {
            'fields': ('payment_status',)
        }),
        ('System Information', {
            'fields': ('ticket_id', 'qr_code', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ticket_id_short(self, obj):
        return f"{str(obj.ticket_id)[:8]}..."
    ticket_id_short.short_description = "Ticket ID"
    
    def has_add_permission(self, request):
        # Prevent manual ticket creation through admin
        return False


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'date_posted', 'is_featured', 'has_image', 'has_video']
    list_filter = ['category', 'is_featured', 'date_posted', 'author']
    search_fields = ['title', 'body']
    ordering = ['-date_posted']
    date_hierarchy = 'date_posted'
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'body', 'category')
        }),
        ('Media', {
            'fields': ('image', 'video')
        }),
        ('Publishing', {
            'fields': ('author', 'is_featured')
        }),
    )
    
    def has_image(self, obj):
        if obj.image:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_image.short_description = "Has Image"
    
    def has_video(self, obj):
        if obj.video:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_video.short_description = "Has Video"
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new article
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'tickets_purchased']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email', 'phone']
    
    def tickets_purchased(self, obj):
        count = obj.user.ticket_set.filter(payment_status='completed').count()
        return f"{count} tickets"
    tickets_purchased.short_description = "Tickets Purchased"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['match', 'tickets_sold', 'revenue', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['match__title']
    ordering = ['-generated_at']
    readonly_fields = ['generated_at']
    
    def has_add_permission(self, request):
        # Reports are generated automatically
        return False


# Customize admin site
admin.site.site_header = "Bo Rangers FC Admin"
admin.site.site_title = "Bo Rangers FC"
admin.site.index_title = "Welcome to Bo Rangers FC Administration"

