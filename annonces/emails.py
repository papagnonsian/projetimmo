from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def notifier_nouveau_message(request, message):
    """Prévient l'autre partie qu'un nouveau message a été posté dans la discussion."""
    demande = message.demande
    auteur = message.auteur

    # Déterminer le destinataire : si l'auteur est le client → notifier l'agent, et vice-versa
    if hasattr(auteur, 'client'):
        destinataire_email = demande.bien.agent.email
        destinataire_nom = f"{demande.bien.agent.prenom} {demande.bien.agent.nom}"
    else:
        destinataire_email = demande.client.email
        destinataire_nom = f"{demande.client.prenom} {demande.client.nom}"

    if not destinataire_email:
        return

    lien = request.build_absolute_uri(reverse('discussion', args=[demande.id]))
    send_mail(
        subject=f"Nouveau message — {demande.bien.titre}",
        message=(
            f"Bonjour {destinataire_nom},\n\n"
            f"{auteur.get_full_name() or auteur.username} vous a envoyé un message "
            f"concernant la demande de visite pour « {demande.bien.titre} ».\n\n"
            f"Voir la discussion : {lien}\n\n"
            f"— Agence Immo CI"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destinataire_email],
        fail_silently=True,
    )


def notifier_nouvelle_demande(request, demande):
    """Prévient l'agent qu'une nouvelle demande de visite vient d'arriver."""
    agent_email = demande.bien.agent.email
    if not agent_email:
        return

    lien = request.build_absolute_uri(reverse('demandes_recues'))
    message = render_to_string('annonces/emails/nouvelle_demande.txt', {
        'demande': demande,
        'lien': lien,
    })
    send_mail(
        subject=f"Nouvelle demande de visite - {demande.bien.titre}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[agent_email],
        fail_silently=True,
    )


def notifier_demande_traitee(request, demande):
    """Prévient le client que sa demande a été acceptée ou refusée."""
    client_email = demande.client.email
    if not client_email:
        return

    lien = request.build_absolute_uri(reverse('mes_demandes'))
    message = render_to_string('annonces/emails/demande_traitee.txt', {
        'demande': demande,
        'lien': lien,
    })
    send_mail(
        subject=f"Votre demande de visite a été {demande.get_statut_display().lower()}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[client_email],
        fail_silently=True,
    )
