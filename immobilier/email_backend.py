import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend


class LenientSSLEmailBackend(EmailBackend):
    """Backend SMTP qui tolère les certificats non-conformes RFC 5280.
    Uniquement pour le développement local — en prod, utiliser le backend Django standard."""

    def open(self):
        if self.connection:
            return False
        try:
            self.connection = smtplib.SMTP(host=self.host, port=self.port)
            self.connection.ehlo()
            if self.use_tls:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                self.connection.starttls(context=ctx)
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise
