from django.core.management.base import BaseCommand
from django.db import transaction
from ticketing.models import TicketCategory, Ticket


class Command(BaseCommand):
    help = 'Remove Family and Student ticket categories from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force removal even if there are existing tickets for these categories',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting removal of Family and Student ticket categories...'))
        
        categories_to_remove = ['Family', 'Student']
        force = options['force']
        
        with transaction.atomic():
            for category_name in categories_to_remove:
                try:
                    category = TicketCategory.objects.get(name=category_name)
                    
                    # Check if there are existing tickets for this category
                    existing_tickets = Ticket.objects.filter(ticket_category=category).count()
                    
                    if existing_tickets > 0:
                        if force:
                            # Delete all tickets for this category first
                            deleted_tickets = Ticket.objects.filter(ticket_category=category).delete()
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Deleted {deleted_tickets[0]} tickets for {category_name} category'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Cannot delete {category_name} category: {existing_tickets} tickets exist. '
                                    f'Use --force to delete tickets and category.'
                                )
                            )
                            continue
                    
                    # Delete the category
                    category.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully removed {category_name} ticket category')
                    )
                    
                except TicketCategory.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'{category_name} ticket category does not exist')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error removing {category_name} category: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS('Category removal process completed!'))
        
        # Show remaining categories
        remaining_categories = TicketCategory.objects.all()
        if remaining_categories:
            self.stdout.write('\nRemaining ticket categories:')
            for cat in remaining_categories:
                self.stdout.write(f'  - {cat.name}: Nle{cat.price}')
        else:
            self.stdout.write('\nNo ticket categories remain in the database.')
