"""
Django Management Command: Initialize DynamoDB Tables
Run this during Render deployment (release phase in Procfile)

Usage:
    python manage.py init_dynamodb
    python manage.py init_dynamodb --delete  (WARNING: Deletes all data!)
"""

from django.core.management.base import BaseCommand
from core.dynamodb_models import create_all_tables, delete_all_tables


class Command(BaseCommand):
    help = 'Create DynamoDB tables for RecruitHub'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all DynamoDB tables (WARNING: Data loss!)',
        )

    def handle(self, *args, **options):
        if options['delete']:
            confirm = input(
                "⚠️  WARNING: This will DELETE ALL DATA in DynamoDB tables!\n"
                "Type 'yes' to confirm: "
            )
            if confirm.lower() == 'yes':
                delete_all_tables()
                self.stdout.write(
                    self.style.WARNING('🗑️  DynamoDB tables deleted!')
                )
            else:
                self.stdout.write(
                    self.style.NOTICE('Operation cancelled.')
                )
        else:
            create_all_tables()
            self.stdout.write(
                self.style.SUCCESS('✅ DynamoDB tables initialized successfully!')
            )
