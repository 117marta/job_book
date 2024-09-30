from django.core.management.base import BaseCommand

from trades.models import (
    ABBREVIATION_BRIDGE,
    ABBREVIATION_CONSTRUCTION,
    ABBREVIATION_CONTACT_SYSTEM,
    ABBREVIATION_DRAINAGE,
    ABBREVIATION_OTHER,
    ABBREVIATION_POWER_ENGINEERING,
    ABBREVIATION_RAILWAY,
    ABBREVIATION_RAILWAY_TRAFFIC,
    ABBREVIATION_ROAD,
    ABBREVIATION_TELECOMMUNICATION,
    Trade,
)


class Command(BaseCommand):
    help = "Populates the database with trades."

    def handle(self, *args, **options):
        Trade.objects.create(
            name="Railway",
            abbreviation=ABBREVIATION_RAILWAY,
            description="Tracks structure, roadbed, tracks, turnouts, platforms and escarpments",
        )
        Trade.objects.create(
            name="Road",
            abbreviation=ABBREVIATION_ROAD,
            description="Roads and railway crossings",
        )
        Trade.objects.create(
            name="Bridge",
            abbreviation=ABBREVIATION_BRIDGE,
            description="Bridges, viaducts and culverts",
        )
        Trade.objects.create(
            name="Construction",
            abbreviation=ABBREVIATION_CONSTRUCTION,
            description="Railway stations, cabins",
        )
        Trade.objects.create(
            name="Drainage",
            abbreviation=ABBREVIATION_DRAINAGE,
            description="Surface (ditches, storage reservoir), "
                        "deep (seeps, drains, absorbent wells) "
                        "and underground (covered ditches, storm sewerage) drainage",
        )
        Trade.objects.create(
            name="Contact System",
            abbreviation=ABBREVIATION_CONTACT_SYSTEM,
            description="3kv DC: traction wires and poles, electrical power substations",
        )
        Trade.objects.create(
            name="Power Engineering",
            abbreviation=ABBREVIATION_POWER_ENGINEERING,
            description="Non-traction electrical engineering: LPN, transformer stations, MV switching stations. "
                        "Low-voltage electrical engineering: railway lighting equipments, "
                        "electric heating of turnouts (EOR), electrical installations in infrastructure facilities",
        )
        Trade.objects.create(
            name=ABBREVIATION_TELECOMMUNICATION,
            abbreviation="TL",
            description="Telecommunications lines, radio communication, dynamic traveller information system",
        )
        Trade.objects.create(
            name="SRK",
            abbreviation=ABBREVIATION_RAILWAY_TRAFFIC,
            description="Railway traffic control system",
        )
        Trade.objects.create(name="Other", abbreviation=ABBREVIATION_OTHER)

        print("Trades have been completed successfully!")
