import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from annonces.models import Agence, Agent, Bien, Categorie, Client, Demande

CATEGORIES = ['Appartement', 'Villa', 'Studio', 'Terrain', 'Bureau', 'Duplex', 'Immeuble', 'Magasin']

COMMUNES = [
    'Cocody', 'Yopougon', 'Marcory', 'Plateau', 'Treichville', 'Abobo',
    'Koumassi', 'Adjamé', 'Bingerville', 'Port-Bouët', 'Attécoubé', 'Songon',
]

NOMS_AGENCE = [
    "Ivoire Immo", "Abidjan Habitat", "Cocody Properties", "Sunu Logement",
    "Baoulé Immobilier", "Lagune Real Estate", "Confort Habitat", "Plateau Immo",
]

PRENOMS = [
    'Kouassi', 'Aya', 'Yao', 'Adjoua', 'Koffi', 'Akissi', 'Bakary', 'Fatou',
    'Issouf', 'Mariam', 'Sékou', 'Aminata', 'Drissa', 'Awa', 'Moussa', 'Nina',
    'Olivier', 'Stéphanie', 'Patrick', 'Grace', 'Eric', 'Carine',
]

NOMS = [
    'Traoré', 'Koné', 'Bamba', 'Ouattara', 'Diabaté', 'Yao', 'N\'Guessan',
    'Coulibaly', 'Touré', 'Diallo', 'Kouadio', 'Gnonsian',
]

DESCRIPTIONS = [
    "Bien situé dans un quartier calme et sécurisé, proche de toutes commodités.",
    "Belle opportunité avec finitions modernes et beaucoup de luminosité.",
    "Idéal pour une famille, proche des écoles et des commerces.",
    "Bien rénové récemment, prêt à être habité ou exploité immédiatement.",
    "Cadre de vie agréable avec accès facile aux grands axes de la ville.",
]


class Command(BaseCommand):
    help = "Génère des données de test : agences, agents, clients, catégories et biens."

    def add_arguments(self, parser):
        parser.add_argument('--agences', type=int, default=8)
        parser.add_argument('--agents', type=int, default=20)
        parser.add_argument('--clients', type=int, default=15)
        parser.add_argument('--biens', type=int, default=80)
        parser.add_argument('--demandes', type=int, default=30)

    def handle(self, *args, **options):
        categories = self._creer_categories()
        agences = self._creer_agences(options['agences'])
        agents = self._creer_agents(options['agents'], agences)
        clients = self._creer_clients(options['clients'])
        biens = self._creer_biens(options['biens'], agents, categories)
        self._creer_demandes(options['demandes'], clients, biens)

        self.stdout.write(self.style.SUCCESS(
            f"Terminé : {Categorie.objects.count()} catégories, "
            f"{Agence.objects.count()} agences, {Agent.objects.count()} agents, "
            f"{Client.objects.count()} clients, {Bien.objects.count()} biens, "
            f"{Demande.objects.count()} demandes."
        ))

    def _creer_categories(self):
        categories = []
        for nom in CATEGORIES:
            categorie, created = Categorie.objects.get_or_create(nom_categorie=nom)
            categories.append(categorie)
            if created:
                self.stdout.write(f"Catégorie créée : {nom}")
        return categories

    def _creer_agences(self, total):
        agences = []
        for i in range(total):
            nom = NOMS_AGENCE[i % len(NOMS_AGENCE)]
            if i >= len(NOMS_AGENCE):
                nom = f"{nom} {i // len(NOMS_AGENCE) + 1}"
            agence, created = Agence.objects.get_or_create(
                nom_agence=nom,
                defaults={
                    'adresse': f"{random.choice(COMMUNES)}, Abidjan",
                    'telephone': f"+225 27 {random.randint(20, 29)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
                    'email': f"contact@{nom.lower().replace(' ', '')}.ci",
                }
            )
            agences.append(agence)
            if created:
                self.stdout.write(f"Agence créée : {nom}")
        return agences

    def _creer_agents(self, total, agences):
        agents = []
        for i in range(1, total + 1):
            username = f"agent{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f"{username}@vianneyprojet.ci"},
            )
            if created:
                user.set_password('Agent2026!')
                user.save()

            agent, agent_created = Agent.objects.get_or_create(
                user=user,
                defaults={
                    'nom': random.choice(NOMS),
                    'prenom': random.choice(PRENOMS),
                    'telephone': f"+225 07 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
                    'email': user.email,
                    'agence': random.choice(agences),
                }
            )
            agents.append(agent)
            if agent_created:
                self.stdout.write(f"Agent créé : {username} / Agent2026!")
        return agents

    def _creer_clients(self, total):
        clients = []
        for i in range(1, total + 1):
            username = f"client{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f"{username}@vianneyprojet.ci"},
            )
            if created:
                user.set_password('Client2026!')
                user.save()

            client, client_created = Client.objects.get_or_create(
                user=user,
                defaults={
                    'nom': random.choice(NOMS),
                    'prenom': random.choice(PRENOMS),
                    'telephone': f"+225 05 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
                    'email': user.email,
                }
            )
            clients.append(client)
            if client_created:
                self.stdout.write(f"Client créé : {username} / Client2026!")
        return clients

    def _creer_biens(self, total, agents, categories):
        if not agents:
            self.stdout.write(self.style.WARNING("Aucun agent disponible, biens non créés."))
            return list(Bien.objects.all())

        a_creer = max(0, total - Bien.objects.count())
        for _ in range(a_creer):
            categorie = random.choice(categories)
            commune = random.choice(COMMUNES)
            agent = random.choice(agents)
            statut = random.choices(
                ['publie', 'brouillon', 'desactive'], weights=[80, 15, 5]
            )[0]

            Bien.objects.create(
                titre=f"{categorie.nom_categorie} à {commune}",
                description=random.choice(DESCRIPTIONS),
                prix=random.randint(5_000_000, 150_000_000),
                localisation=commune,
                type_transaction=random.choice(['vente', 'location']),
                statut=statut,
                surface=random.randint(20, 500),
                pieces=random.randint(1, 10),
                agence=agent.agence,
                agent=agent,
                categorie=categorie,
            )

        self.stdout.write(f"{a_creer} bien(s) créé(s).")
        return list(Bien.objects.all())

    def _creer_demandes(self, total, clients, biens):
        if not clients or not biens:
            self.stdout.write(self.style.WARNING("Aucun client/bien disponible, demandes non créées."))
            return

        a_creer = max(0, total - Demande.objects.count())
        for _ in range(a_creer):
            Demande.objects.create(
                client=random.choice(clients),
                bien=random.choice(biens),
                statut=random.choices(
                    ['en_attente', 'acceptee', 'refusee', 'annulee'],
                    weights=[40, 30, 20, 10],
                )[0],
                message="Je suis intéressé par ce bien, pourrions-nous organiser une visite ?",
            )

        self.stdout.write(f"{a_creer} demande(s) créée(s).")
