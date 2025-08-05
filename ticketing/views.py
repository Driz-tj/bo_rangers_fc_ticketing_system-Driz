from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.conf import settings
from .models import Match, Ticket, News, TicketCategory, UserProfile, Report
from .forms import TicketBookingForm, NewsForm, GatemanCreationForm, AdminCreationForm, MatchForm
from django.contrib.auth.models import User
import json
import csv
import os
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, green, gold
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO


def get_upcoming_matches(limit=None):
    """Helper function to get upcoming matches consistently across views"""
    matches = Match.objects.filter(status='upcoming').order_by('date')
    if limit:
        matches = matches[:limit]
    return matches


def home(request):
    """Homepage with featured matches and news"""
    # Get upcoming matches using the same logic as fixtures page
    upcoming_matches = get_upcoming_matches(limit=3)
    featured_news = News.objects.filter(is_featured=True).order_by('-date_posted')[:3]
    recent_news = News.objects.order_by('-date_posted')[:6]
    
    context = {
        'upcoming_matches': upcoming_matches,
        'featured_news': featured_news,
        'recent_news': recent_news,
    }
    return render(request, 'ticketing/home.html', context)


def fixtures(request):
    """Display match fixtures with filtering"""
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('date', '')
    home_away_filter = request.GET.get('home_away', 'all')
    
    # If filtering for upcoming matches, use the same logic as home page
    if status_filter == 'upcoming' and not search_query and not date_filter and home_away_filter == 'all':
        matches = get_upcoming_matches()
    else:
        matches = Match.objects.all()
        
        # Apply status filter
        if status_filter != 'all':
            matches = matches.filter(status=status_filter)
        
        # Apply search filter
        if search_query:
            matches = matches.filter(
                Q(title__icontains=search_query) |
                Q(opponent__icontains=search_query) |
                Q(home_team__icontains=search_query) |
                Q(venue__icontains=search_query)
            )
        
        # Apply date filter
        if date_filter:
            matches = matches.filter(date__date=date_filter)
        
        # Apply home/away filter
        if home_away_filter == 'home':
            matches = matches.filter(home_team='Bo Rangers FC')
        elif home_away_filter == 'away':
            matches = matches.filter(~Q(home_team='Bo Rangers FC'))
        
        matches = matches.order_by('date')
    
    context = {
        'matches': matches,
        'current_filter': status_filter,
    }
    return render(request, 'ticketing/fixtures.html', context)


@login_required
def book_ticket(request, match_id):
    """Ticket booking page"""
    match = get_object_or_404(Match, id=match_id)
    ticket_categories = TicketCategory.objects.all()
    
    if request.method == 'POST':
        form = TicketBookingForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.match = match
            ticket.save()
            
            # Redirect to payment page
            return redirect('payment', ticket_id=ticket.id)
    else:
        form = TicketBookingForm()
    
    context = {
        'match': match,
        'form': form,
        'ticket_categories': ticket_categories,
    }
    return render(request, 'ticketing/book_ticket.html', context)


@login_required
def payment(request, ticket_id):
    """Mock payment page"""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        # Mock payment processing
        payment_method = request.POST.get('payment_method')
        phone_number = request.POST.get('phone_number')
        
        # Simulate payment success
        ticket.payment_status = 'completed'
        ticket.save()  # This will trigger QR code generation
        
        # Update report
        report, created = Report.objects.get_or_create(
            match=ticket.match,
            defaults={'tickets_sold': 0, 'revenue': 0}
        )
        report.tickets_sold += ticket.quantity
        report.revenue += ticket.total_price()
        report.save()
        
        messages.success(request, 'Payment successful! Your ticket has been generated.')
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'ticketing/payment.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """Display ticket details with QR code"""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'ticketing/ticket_detail.html', context)


def news_list(request):
    """Display news articles with pagination"""
    from django.core.paginator import Paginator
    
    category_filter = request.GET.get('category', 'all')
    page_number = request.GET.get('page', 1)
    articles_per_page = 10  # Number of articles to show per page
    
    if category_filter == 'all':
        news_articles = News.objects.all().order_by('-date_posted')
    else:
        news_articles = News.objects.filter(category=category_filter).order_by('-date_posted')
    
    # Create paginator
    paginator = Paginator(news_articles, articles_per_page)
    page_obj = paginator.get_page(page_number)
    
    categories = News.CATEGORY_CHOICES
    
    context = {
        'news_articles': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_filter,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    }
    return render(request, 'ticketing/news_list.html', context)


def news_detail(request, news_id):
    """Display individual news article"""
    article = get_object_or_404(News, id=news_id)
    related_news = News.objects.filter(category=article.category).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'related_news': related_news,
    }
    return render(request, 'ticketing/news_detail.html', context)


def load_more_news(request):
    """AJAX endpoint to load more news articles"""
    from django.core.paginator import Paginator
    from django.template.loader import render_to_string
    
    category_filter = request.GET.get('category', 'all')
    page_number = request.GET.get('page', 1)
    articles_per_page = 10
    
    if category_filter == 'all':
        news_articles = News.objects.all().order_by('-date_posted')
    else:
        news_articles = News.objects.filter(category=category_filter).order_by('-date_posted')
    
    paginator = Paginator(news_articles, articles_per_page)
    page_obj = paginator.get_page(page_number)
    
    # Render the articles HTML
    articles_html = render_to_string('ticketing/news_articles_partial.html', {
        'news_articles': page_obj,
        'current_category': category_filter,
    })
    
    return JsonResponse({
        'articles_html': articles_html,
        'has_next': page_obj.has_next(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            phone = request.POST.get('phone', '')
            UserProfile.objects.create(user=user, phone=phone, role='fan')
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """User profile page"""
    user_tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user_tickets': user_tickets,
    }
    return render(request, 'ticketing/profile.html', context)


def logout_view(request):
    """Log out the user and redirect to login page"""
    logout(request)
    return redirect('login')


def custom_login(request):
    """Custom login view that redirects based on user role"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Check user role and redirect accordingly
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.role == 'admin':
                        return redirect('admin_dashboard')  # Redirect admins to admin dashboard
                    elif user_profile.role == 'gateman':
                        return redirect('gateman_scanner')  # Redirect gateman to ticket scanner
                    else:
                        return redirect('home')  # Redirect fans to home page
                except UserProfile.DoesNotExist:
                    # If no profile exists, create one with default 'fan' role
                    UserProfile.objects.create(user=user, role='fan')
                    return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


# Admin views
@login_required
def admin_dashboard(request):
    """Admin dashboard with analytics"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Analytics data
    total_matches = Match.objects.count()
    total_tickets_sold = Ticket.objects.filter(payment_status='completed').aggregate(
        total=Sum('quantity'))['total'] or 0
    total_revenue = Ticket.objects.filter(payment_status='completed').aggregate(
        total=Sum('ticket_category__price'))['total'] or 0
    
    upcoming_matches = Match.objects.filter(status='upcoming').count()
    recent_tickets = Ticket.objects.filter(payment_status='completed').order_by('-created_at')[:5]
    
    # Chart data for revenue by match
    reports = Report.objects.all().order_by('-revenue')[:5]
    chart_data = {
        'labels': [report.match.title for report in reports],
        'revenue': [float(report.revenue) for report in reports],
        'tickets': [report.tickets_sold for report in reports]
    }
    
    context = {
        'total_matches': total_matches,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'upcoming_matches': upcoming_matches,
        'recent_tickets': recent_tickets,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'ticketing/admin_dashboard.html', context)


@login_required
def admin_users(request):
    """Admin user management page"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Make the user a staff member
            user.is_staff = True
            user.save()
            
            # Create UserProfile with admin role
            user_profile = UserProfile.objects.create(
                user=user,
                role='admin',
                phone=''
            )
            
            messages.success(request, f'Admin user "{user.username}" created successfully!')
            return redirect('admin_users')
    else:
        form = AdminCreationForm()
    
    # Get all admin users
    admin_profiles = UserProfile.objects.filter(role='admin').select_related('user')
    
    context = {
        'form': form,
        'admin_profiles': admin_profiles,
    }
    return render(request, 'ticketing/admin_users.html', context)


@login_required
def admin_matches(request):
    """Admin match management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Handle delete request
    if request.method == 'POST' and 'delete_match' in request.POST:
        match_id = request.POST.get('match_id')
        try:
            match = Match.objects.get(id=match_id)
            match_title = match.title
            match.delete()
            messages.success(request, f'Match "{match_title}" has been deleted successfully.')
        except Match.DoesNotExist:
            messages.error(request, 'Match not found.')
        return redirect('admin_matches')
    
    matches = Match.objects.all().order_by('-date')
    
    # Add sold tickets count for each match
    for match in matches:
        match.sold_tickets_count = match.ticket_set.filter(payment_status='completed').count()
    
    # Calculate counts for different match statuses
    upcoming_count = matches.filter(status='upcoming').count()
    completed_count = matches.filter(status='completed').count()
    live_count = matches.filter(status='live').count()
    
    context = {
        'matches': matches,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'live_count': live_count,
        'total_matches': matches.count(),
    }
    return render(request, 'ticketing/admin_matches.html', context)


@login_required
def add_match(request):
    """Add a new match"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = MatchForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match created successfully!')
            return redirect('admin_matches')
    else:
        form = MatchForm()
    
    context = {
        'form': form,
    }
    return render(request, 'ticketing/add_edit_match.html', context)


@login_required
def edit_match(request, match_id):
    """Edit an existing match"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        messages.error(request, 'Match not found.')
        return redirect('admin_matches')
    
    if request.method == 'POST':
        form = MatchForm(request.POST, request.FILES, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, f'Match "{match.title}" updated successfully!')
            return redirect('admin_matches')
    else:
        form = MatchForm(instance=match)
    
    context = {
        'form': form,
        'match': match,
    }
    return render(request, 'ticketing/add_edit_match.html', context)


@login_required
def admin_news(request):
    """Admin news management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            messages.success(request, 'News article created successfully!')
            return redirect('admin_news')
    else:
        form = NewsForm()
    
    news_articles = News.objects.all().order_by('-date_posted')
    
    # Calculate counts for each category
    total_articles = news_articles.count()
    featured_count = news_articles.filter(is_featured=True).count()
    match_recap_count = news_articles.filter(category='match_recap').count()
    press_release_count = news_articles.filter(category='press_release').count()
    club_news_count = news_articles.filter(category='club_news').count()
    transfer_count = news_articles.filter(category='transfer').count()
    general_count = news_articles.filter(category='general').count()
    
    context = {
        'form': form,
        'news_articles': news_articles,
        'total_articles': total_articles,
        'featured_count': featured_count,
        'match_recap_count': match_recap_count,
        'press_release_count': press_release_count,
        'club_news_count': club_news_count,
        'transfer_count': transfer_count,
        'general_count': general_count,
    }
    return render(request, 'ticketing/admin_news.html', context)


@login_required
def edit_news(request, news_id):
    """Edit an existing news article"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    try:
        news = News.objects.get(id=news_id)
    except News.DoesNotExist:
        messages.error(request, 'News article not found.')
        return redirect('admin_news')
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, f'News article "{news.title}" updated successfully!')
            return redirect('admin_news')
    else:
        form = NewsForm(instance=news)
    
    context = {
        'form': form,
        'news': news,
        'is_edit': True
    }
    return render(request, 'ticketing/add_edit_news.html', context)


@login_required
@require_http_methods(["POST"])
def delete_news(request, news_id):
    """Delete a news article"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied. Admin privileges required.'})
    
    try:
        news = News.objects.get(id=news_id)
        news_title = news.title
        news.delete()
        return JsonResponse({
            'success': True,
            'message': f'News article "{news_title}" has been deleted successfully.'
        })
    except News.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'News article not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def admin_reports(request):
    """Admin reports page"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    reports = Report.objects.all().order_by('-generated_at')
    
    # Calculate average price per ticket for each report
    for report in reports:
        if report.tickets_sold > 0:
            report.avg_price_per_ticket = report.revenue / report.tickets_sold
        else:
            report.avg_price_per_ticket = 0
    
    # Calculate totals
    total_tickets_sold = sum(report.tickets_sold for report in reports)
    total_revenue = sum(report.revenue for report in reports)
    highest_match_revenue = max((report.revenue for report in reports), default=0)
    
    context = {
        'reports': reports,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'highest_match_revenue': highest_match_revenue,
    }
    return render(request, 'ticketing/admin_reports.html', context)


@login_required
def export_reports_csv(request):
    """Export reports as CSV file"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bo_rangers_sales_reports.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow(['Match', 'Opponent', 'Date', 'Venue', 'Tickets Sold', 'Revenue (Nle)', 'Avg. Ticket Price', 'Report Generated'])
    
    # Get all reports
    reports = Report.objects.all().order_by('-generated_at')
    
    # Write data rows
    for report in reports:
        # Calculate average price per ticket
        avg_price = report.revenue / report.tickets_sold if report.tickets_sold > 0 else 0
        
        writer.writerow([
            report.match.title,
            report.match.opponent,
            report.match.date.strftime('%Y-%m-%d %H:%M'),
            report.match.venue,
            report.tickets_sold,
            float(report.revenue),
            float(avg_price),
            report.generated_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response


@login_required
def export_reports_pdf(request):
    """Export reports as PDF file"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set up the document with a header
    p.setFont('Helvetica-Bold', 16)
    p.drawString(30, height - 50, 'Bo Rangers FC - Sales Reports')
    p.setFont('Helvetica', 10)
    p.drawString(30, height - 70, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    p.drawString(30, height - 90, f'Generated by: {request.user.username}')
    
    # Add a horizontal line
    p.line(30, height - 100, width - 30, height - 100)
    
    # Get all reports
    reports = Report.objects.all().order_by('-generated_at')
    
    # Calculate totals
    total_tickets = sum(report.tickets_sold for report in reports)
    total_revenue = sum(report.revenue for report in reports)
    
    # Add summary section
    p.setFont('Helvetica-Bold', 12)
    p.drawString(30, height - 130, 'Summary')
    p.setFont('Helvetica', 10)
    p.drawString(30, height - 150, f'Total Reports: {reports.count()}')
    p.drawString(30, height - 170, f'Total Tickets Sold: {total_tickets}')
    p.drawString(30, height - 190, f'Total Revenue: Nle{float(total_revenue):.2f}')
    
    # Add table headers
    y_position = height - 230
    p.setFont('Helvetica-Bold', 10)
    p.drawString(30, y_position, 'Match')
    p.drawString(180, y_position, 'Date')
    p.drawString(260, y_position, 'Tickets')
    p.drawString(320, y_position, 'Revenue (Nle)')
    p.drawString(420, y_position, 'Generated')
    p.line(30, y_position - 10, width - 30, y_position - 10)
    
    # Add table data
    y_position -= 30
    p.setFont('Helvetica', 9)
    
    for report in reports:
        # Check if we need a new page
        if y_position < 50:
            p.showPage()
            p.setFont('Helvetica-Bold', 12)
            p.drawString(30, height - 50, 'Bo Rangers FC - Sales Reports (Continued)')
            p.setFont('Helvetica-Bold', 10)
            p.drawString(30, height - 80, 'Match')
            p.drawString(180, height - 80, 'Date')
            p.drawString(260, height - 80, 'Tickets')
            p.drawString(320, height - 80, 'Revenue (Nle)')
            p.drawString(420, height - 80, 'Generated')
            p.line(30, height - 90, width - 30, height - 90)
            y_position = height - 110
            p.setFont('Helvetica', 9)
        
        # Add report data
        match_title = f"{report.match.title} vs {report.match.opponent}"
        if len(match_title) > 25:
            match_title = match_title[:22] + '...'
        
        p.drawString(30, y_position, match_title)
        p.drawString(180, y_position, report.match.date.strftime('%Y-%m-%d'))
        p.drawString(260, y_position, str(report.tickets_sold))
        p.drawString(320, y_position, f"{float(report.revenue):.2f}")
        p.drawString(420, y_position, report.generated_at.strftime('%Y-%m-%d'))
        
        y_position -= 20
    
    # Add footer
    p.showPage()
    p.setFont('Helvetica', 8)
    p.drawString(30, 30, 'Bo Rangers FC Ticketing System - Confidential')
    
    # Save the PDF
    p.save()
    
    # Get the value of the BytesIO buffer and return the PDF as a response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bo_rangers_sales_reports.pdf"'
    response.write(pdf)
    
    return response


@login_required
def download_report(request, report_id):
    """Download a specific report as PDF"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        messages.error(request, 'Report not found.')
        return redirect('admin_reports')
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set up the document with a header
    p.setFont('Helvetica-Bold', 16)
    p.drawString(30, height - 50, f'Bo Rangers FC - Match Sales Report')
    p.setFont('Helvetica-Bold', 14)
    p.drawString(30, height - 80, f'{report.match.title} vs {report.match.opponent}')
    
    p.setFont('Helvetica', 10)
    p.drawString(30, height - 100, f'Match Date: {report.match.date.strftime("%Y-%m-%d %H:%M")}')
    p.drawString(30, height - 120, f'Venue: {report.match.venue}')
    p.drawString(30, height - 140, f'Report Generated: {report.generated_at.strftime("%Y-%m-%d %H:%M")}')
    
    # Add a horizontal line
    p.line(30, height - 160, width - 30, height - 160)
    
    # Add summary section
    p.setFont('Helvetica-Bold', 12)
    p.drawString(30, height - 190, 'Sales Summary')
    
    p.setFont('Helvetica', 10)
    p.drawString(30, height - 220, f'Tickets Sold: {report.tickets_sold}')
    p.drawString(30, height - 240, f'Total Revenue: Nle{float(report.revenue):.2f}')
    
    # Calculate average price
    avg_price = report.revenue / report.tickets_sold if report.tickets_sold > 0 else 0
    p.drawString(30, height - 260, f'Average Ticket Price: Nle{float(avg_price):.2f}')
    
    # Get ticket category breakdown for this match
    ticket_categories = Ticket.objects.filter(
        match=report.match, 
        payment_status='completed'
    ).values('ticket_category__name').annotate(
        count=Count('id'),
        total=Sum(F('ticket_category__price') * F('quantity'))
    )
    
    # Add category breakdown
    if ticket_categories:
        p.setFont('Helvetica-Bold', 12)
        p.drawString(30, height - 300, 'Category Breakdown')
        
        y_position = height - 330
        p.setFont('Helvetica-Bold', 10)
        p.drawString(30, y_position, 'Category')
        p.drawString(200, y_position, 'Tickets Sold')
        p.drawString(300, y_position, 'Revenue (Nle)')
        p.line(30, y_position - 10, width - 30, y_position - 10)
        
        y_position -= 30
        p.setFont('Helvetica', 10)
        
        for category in ticket_categories:
            p.drawString(30, y_position, category['ticket_category__name'])
            p.drawString(200, y_position, str(category['count']))
            p.drawString(300, y_position, f"{float(category['total']):.2f}")
            y_position -= 20
    
    # Add footer
    p.showPage()
    p.setFont('Helvetica', 8)
    p.drawString(30, 30, 'Bo Rangers FC Ticketing System - Confidential')
    
    # Save the PDF
    p.save()
    
    # Get the value of the BytesIO buffer and return the PDF as a response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    filename = f"bo_rangers_report_{report.match.title.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response


@login_required
@require_http_methods(["POST"])
def update_match_status(request):
    """Update match status via AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied. Admin privileges required.'})
    
    try:
        import json
        data = json.loads(request.body)
        match_id = data.get('match_id')
        new_status = data.get('new_status')
        
        if not match_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing match_id or new_status'})
        
        # Validate status
        valid_statuses = ['upcoming', 'live', 'completed']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        # Get the match
        match = Match.objects.get(id=match_id)
        
        # Update status
        match.status = new_status
        match.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Match status updated to {new_status}',
            'new_status': new_status,
            'match_title': match.title
        })
        
    except Match.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Match not found'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def admin_gatemen(request):
    """Admin gateman management page"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = GatemanCreationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Create UserProfile with gateman role
            user_profile = UserProfile.objects.create(
                user=user,
                role='gateman',
                phone_number='',  # Can be updated later
                date_of_birth=None  # Can be updated later
            )
            
            messages.success(request, f'Gateman "{user.username}" created successfully!')
            return redirect('admin_gatemen')
    else:
        form = GatemanCreationForm()
    
    # Get all gatemen
    gatemen_profiles = UserProfile.objects.filter(role='gateman').select_related('user')
    
    # Get scan statistics for each gateman
    for profile in gatemen_profiles:
        profile.total_scans = Ticket.objects.filter(
            is_scanned=True,
            scanned_by=profile.user
        ).count()
        
        # Today's scans
        today = timezone.now().date()
        profile.today_scans = Ticket.objects.filter(
            is_scanned=True,
            scanned_by=profile.user,
            scanned_at__date=today
        ).count()
    
    context = {
        'form': form,
        'gatemen_profiles': gatemen_profiles,
    }
    return render(request, 'ticketing/admin_gatemen.html', context)


@login_required
@require_http_methods(["POST"])
def delete_gateman(request, user_id):
    """Delete a gateman user"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied. Admin privileges required.'})
    
    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user, role='gateman')
        
        username = user.username
        user.delete()  # This will also delete the associated UserProfile due to CASCADE
        
        return JsonResponse({
            'success': True,
            'message': f'Gateman "{username}" deleted successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Gateman profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def delete_admin(request, user_id):
    """Delete an admin user"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied. Admin privileges required.'})
    
    # Prevent self-deletion
    if int(user_id) == request.user.id:
        return JsonResponse({'success': False, 'error': 'You cannot delete your own admin account.'})
    
    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user, role='admin')
        
        username = user.username
        user.delete()  # This will also delete the associated UserProfile due to CASCADE
        
        return JsonResponse({
            'success': True,
            'message': f'Admin user "{username}" deleted successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Admin profile not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Gateman views
@login_required
def gateman_scanner(request):
    """Gateman scanner interface with daily statistics"""
    # Check if user has gateman role
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'gateman':
            messages.error(request, 'Access denied. Gateman privileges required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Access denied. User profile not found.')
        return redirect('home')
    
    # Get today's statistics
    today = timezone.now().date()
    today_scans = Ticket.objects.filter(
        is_scanned=True,
        scanned_at__date=today,
        scanned_by=request.user
    ).count()
    
    # Get recent scans (last 10)
    recent_scans = Ticket.objects.filter(
        is_scanned=True,
        scanned_by=request.user
    ).order_by('-scanned_at')[:10]
    
    context = {
        'today_scans': today_scans,
        'recent_scans': recent_scans,
    }
    return render(request, 'ticketing/gateman_scanner.html', context)


@login_required
@require_http_methods(["POST"])
def scan_ticket(request):
    """Process ticket scanning via AJAX"""
    # Check if user has gateman role
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'gateman':
            return JsonResponse({'success': False, 'error': 'Access denied. Gateman privileges required.'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Access denied. User profile not found.'})
    
    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        
        if not ticket_id:
            return JsonResponse({'success': False, 'error': 'Missing ticket ID'})
        
        # Get the ticket
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found'})
        
        # Check if ticket is paid
        if ticket.payment_status != 'completed':
            return JsonResponse({'success': False, 'error': 'Ticket payment not completed'})
        
        # Check if already scanned
        if ticket.is_scanned:
            return JsonResponse({
                'success': False, 
                'error': f'Ticket already scanned on {ticket.scanned_at.strftime("%Y-%m-%d %H:%M")}'
            })
        
        # Scan the ticket
        ticket.is_scanned = True
        ticket.scanned_at = timezone.now()
        ticket.scanned_by = request.user
        ticket.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Ticket scanned successfully',
            'ticket_info': {
                'id': ticket.id,
                'match': ticket.match.title,
                'ticket_category': ticket.ticket_category.name,
                'quantity': ticket.quantity,
                'user': ticket.user.get_full_name() or ticket.user.username,
                'scanned_at': ticket.scanned_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def download_ticket(request, ticket_id):
    """Generate and download a professional PDF ticket"""
    try:
        # Get the ticket
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
        
        # Check if ticket is paid
        if ticket.payment_status != 'completed':
            messages.error(request, 'Ticket payment not completed')
            return redirect('profile')
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.alignment = TA_CENTER
        title_style.fontSize = 24
        title_style.textColor = green
        
        heading_style = styles['Heading2']
        heading_style.alignment = TA_CENTER
        heading_style.fontSize = 18
        heading_style.textColor = black
        
        normal_style = styles['Normal']
        normal_style.fontSize = 12
        normal_style.alignment = TA_LEFT
        
        # Add logo if exists
        logo_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', 'Logo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=2*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 12))
            except:
                pass  # Skip logo if there's an issue
        
        # Title
        elements.append(Paragraph("BO RANGERS FC", title_style))
        elements.append(Paragraph("OFFICIAL MATCH TICKET", heading_style))
        elements.append(Spacer(1, 24))
        
        # Ticket border (decorative line)
        elements.append(Paragraph("━" * 50, normal_style))
        elements.append(Spacer(1, 12))
        
        # Match Information
        elements.append(Paragraph(f"<b>MATCH:</b> {ticket.match.title}", normal_style))
        elements.append(Paragraph(f"<b>OPPONENT:</b> vs {ticket.match.opponent}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Date and Time
        elements.append(Paragraph(f"<b>DATE:</b> {ticket.match.date.strftime('%A, %B %d, %Y')}", normal_style))
        elements.append(Paragraph(f"<b>TIME:</b> {ticket.match.date.strftime('%H:%M')}", normal_style))
        elements.append(Paragraph(f"<b>VENUE:</b> {ticket.match.venue}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Ticket Details
        elements.append(Paragraph(f"<b>CATEGORY:</b> {ticket.ticket_category.name}", normal_style))
        elements.append(Paragraph(f"<b>QUANTITY:</b> {ticket.quantity} ticket{'s' if ticket.quantity > 1 else ''}", normal_style))
        elements.append(Paragraph(f"<b>TICKET HOLDER:</b> {ticket.user.get_full_name() or ticket.user.username}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Price
        elements.append(Paragraph(f"<b>TOTAL PAID:</b> Nle{ticket.total_price()}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Ticket ID
        elements.append(Paragraph("━" * 50, normal_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>TICKET ID:</b> {ticket.ticket_id}", normal_style))
        elements.append(Paragraph(f"<b>PURCHASED:</b> {ticket.created_at.strftime('%B %d, %Y at %H:%M')}", normal_style))
        elements.append(Spacer(1, 12))
        
        # QR Code
        if ticket.qr_code:
            qr_path = os.path.join(settings.MEDIA_ROOT, str(ticket.qr_code))
            if os.path.exists(qr_path):
                try:
                    qr_image = Image(qr_path, width=2*inch, height=2*inch)
                    qr_image.hAlign = 'CENTER'
                    elements.append(Paragraph("SCAN QR CODE AT ENTRANCE", heading_style))
                    elements.append(Spacer(1, 12))
                    elements.append(qr_image)
                    elements.append(Spacer(1, 12))
                except:
                    pass
        
        # Important Information
        elements.append(Paragraph("━" * 50, normal_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<b>IMPORTANT INFORMATION:</b>", normal_style))
        elements.append(Paragraph("• Arrive at stadium 30 minutes before kickoff", normal_style))
        elements.append(Paragraph("• Present QR code at entrance for scanning", normal_style))
        elements.append(Paragraph("• This ticket is non-transferable", normal_style))
        elements.append(Paragraph("• Keep this ticket safe until match day", normal_style))
        elements.append(Paragraph("• Contact: tickets@borangersfc.com for support", normal_style))
        elements.append(Spacer(1, 24))
        
        # Footer
        elements.append(Paragraph("━" * 50, normal_style))
        elements.append(Paragraph("Thank you for supporting Bo Rangers FC!", heading_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="BoRangersFC_Ticket_{ticket.ticket_id}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating ticket: {str(e)}')
        return redirect('profile')


@login_required
def match_preview(request, match_id):
    """Display detailed preview or summary for a single match."""
    match = get_object_or_404(Match, id=match_id)
    
    # Get match events for completed matches
    match_events = []
    if match.is_completed:
        match_events = match.events.all().order_by('minute')
    
    # Generate match summary if not provided
    if match.is_completed and not match.match_summary:
        match.match_summary = generate_match_summary(match)
    
    # Generate highlights if not provided
    if match.is_completed and not match.highlights:
        match.highlights = generate_match_highlights(match, match_events)
    
    context = {
        'match': match,
        'match_events': match_events,
    }
    return render(request, 'ticketing/match_preview.html', context)


def generate_match_summary(match):
    """Generate an auto-generated match summary based on match data."""
    if not match.is_completed:
        return ""
    
    summary_parts = []
    
    # Basic result - handle None case
    if match.result is None:
        summary_parts.append(f"Bo Rangers FC played against {match.opponent}")
    elif match.result == 'Win':
        summary_parts.append(f"Bo Rangers FC secured a {match.result.lower()} against {match.opponent}")
    elif match.result == 'Loss':
        summary_parts.append(f"Bo Rangers FC suffered a {match.result.lower()} to {match.opponent}")
    elif match.result == 'Draw':
        summary_parts.append(f"Bo Rangers FC played to a {match.result.lower()} with {match.opponent}")
    else:
        summary_parts.append(f"Bo Rangers FC played against {match.opponent}")
    
    summary_parts.append(f"in a thrilling encounter at {match.venue}.")
    
    # Score details
    if match.home_score is not None and match.away_score is not None:
        summary_parts.append(f"The final score was {match.score_display}.")
    else:
        summary_parts.append("The match has been completed.")
    
    # Attendance
    if match.attendance:
        summary_parts.append(f"The match was attended by {match.attendance:,} passionate fans.")
    
    # Weather
    if match.weather:
        summary_parts.append(f"Match conditions were {match.weather}.")
    
    # Key statistics
    if match.shots_home and match.shots_away:
        summary_parts.append(f"Bo Rangers had {match.shots_home} shots compared to {match.shots_away} from {match.opponent}.")
    
    if match.possession_home and match.possession_away:
        summary_parts.append(f"Possession was {match.possession_home}% - {match.possession_away}%.")
    
    return " ".join(summary_parts)


def generate_match_highlights(match, events):
    """Generate match highlights based on events and statistics."""
    if not match.is_completed:
        return ""
    
    highlights = []
    
    # Goals
    goal_events = [e for e in events if e.event_type == 'goal']
    if goal_events:
        highlights.append(f"⚽ {len(goal_events)} goals were scored during the match.")
    
    # Cards
    yellow_cards = [e for e in events if e.event_type == 'yellow_card']
    red_cards = [e for e in events if e.event_type == 'red_card']
    
    if yellow_cards:
        highlights.append(f"🟨 {len(yellow_cards)} yellow cards were shown.")
    if red_cards:
        highlights.append(f"🟥 {len(red_cards)} red cards were shown.")
    
    # Substitutions
    substitutions = [e for e in events if e.event_type == 'substitution']
    if substitutions:
        highlights.append(f"🔄 {len(substitutions)} substitutions were made.")
    
    # Key moments
    if match.shots_on_target_home and match.shots_on_target_away:
        total_shots_on_target = match.shots_on_target_home + match.shots_on_target_away
        highlights.append(f"🎯 {total_shots_on_target} shots were on target.")
    
    if match.corners_home and match.corners_away:
        total_corners = match.corners_home + match.corners_away
        highlights.append(f"🏁 {total_corners} corners were awarded.")
    
    return " ".join(highlights)
