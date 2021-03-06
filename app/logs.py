import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from .conf import conf


# Provide a class to allow SSL (Not TLS) connection for mail handlers by overloading the emit() method
class SSLSMTPHandler(SMTPHandler):
    def emit(self, record):
        try:
            import smtplib
            from email.message import EmailMessage
            import email.utils
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP_SSL(self.mailhost, port, timeout=self.timeout)
            msg = EmailMessage()
            msg['From'] = self.fromaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.getSubject(record)
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))
            if self.username:
                smtp.login(self.username, self.password)
            # smtp.sendmail(self.fromaddr, self.toaddrs, msg.as_string())
            smtp.send_message(msg)
            smtp.quit()
        except Exception:
            self.handleError(record)


def log_init_app(app):
    # Create file handler for error/warning/info/debug logs
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=1 * 1024 * 1024, backupCount=100)

    # Apply format to the log messages
    formatter = logging.Formatter("[%(asctime)s] |  %(levelname)s | {%(pathname)s:%(lineno)d} | %(message)s")
    file_handler.setFormatter(formatter)

    file_handler.setLevel(getattr(logging, app.config['LOGFILE_LEVEL']))

    # Create equivalent mail handler using hacking class for SSL email
    mail_handler = SSLSMTPHandler((app.config['MAIL_SERVER'], int(app.config['MAIL_PORT'])),
                                  app.config['MAIL_SENDER'], [app.config['MAIL_SENDER']],
                                  'Myarxiv app failure log',
                                  credentials=(app.config['MAIL_SENDER'], app.config['MAIL_PASSWORD']))

    # Set the email format
    mail_handler.setFormatter(logging.Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))

    mail_handler.setLevel(logging.ERROR)

    loggers = [app.logger, logging.getLogger('sqlalchemy'), logging.getLogger('werkzeug'), logging.getLogger('celery')]
    if app.config["LOG_FILE"]:
        for logger in loggers:
            logger.addHandler(file_handler)
    print(app.logger.handlers)
    if app.config["MAIL_ON_ERROR"]:
        for logger in loggers:
            logger.addHandler(mail_handler)
