from django.core.management.base import BaseCommand
from aircraft.accounts.models import Team


class Command(BaseCommand):
    help = 'Creates the initial teams for the aircraft system'

    def handle(self, *args, **kwargs):
        try:
            # Get the path to the JSON file
            team_types = ["WING", "FUSELAGE", "TAIL", "AVIONICS", "ASSEMBLY"]
            
            # Create teams
            for team_type in team_types:
                _, created = Team.objects.get_or_create(team_type=team_type)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new team: {team_type}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Team already exists: {team_type}'))

            self.stdout.write(self.style.SUCCESS('Successfully processed all teams'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing teams: {str(e)}')) 