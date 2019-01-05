"""
module for send html email of summary of highlight on arxiv
"""

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def makeauthorlink(authorname):
    authorname = authorname.split(" ")
    authorname = "+".join(authorname)
    url1 = 'https://arxiv.org/search/?query=%22'
    url2 = '%22&searchtype=author&abstracts=show&order=-announced_date_first&size=50'
    return url1 + authorname + url2


def makecss():
    return (
        '<style> .id {font-size: large; color: #b30000 !important; background: #F0EEE4; border:#999999 solid 1px !important;padding: 2px !important;}'
        '.title {font-size: large; font-weight: bold; line-height: 120%%; }'
        '.summary {line-height: 130%%; }'
        '.authors {font-style:italic; }'
        'p .tags {lin-height:130%%}'
        '.tag {display: inline-block; background-color: #aab5c3; border-radix: 10px; color: #fff; margin: 0 5px 5px 0; padding: 0px 10px;}'
        '</style>')


def makehtml(content, count):
    htmltext1 = (
                    '<p class="id">[%s] &nbsp  arXiv:<a href="%s">%s</a> &nbsp  &nbsp Keywords: %s</p>'
                    '<p class="title">%s</p>'
                ) % (
                    count, content['arxiv_url'], content['arxiv_id'], ", ".join([w[0] for w in content['keyword']]),
                    content['title'])
    htmltextauthors = ""
    if content.get('authors', None):
        htmltextauthors += '<p class="authors">'
        for a in content['authors']:
            link = makeauthorlink(a)
            htmltextauthors += '<a href="%s">%s</a>, ' % (link, a)
        htmltextauthors = htmltextauthors[:-1]
        htmltextauthors += '</p>'
    htmltexttags = ""
    if content.get('tags', None):
        htmltexttags += '<p class="tags">'
        for t in content['tags']:
            htmltexttags += '<span class="tag"> %s </span> &nbsp' % t[0]
        htmltexttags += '</p>'
    htmltext3 = ('<hr>'
                 '<p class="summary">%s</p>') % (content['summary'])
    return htmltext1 + htmltextauthors + htmltexttags + htmltext3


def makemailcontent(headline, contents):
    body = makecss() + " ".join([makehtml(it, i + 1) for i, it in enumerate(contents)])
    return ('<html><body>'
            '<p class="title">%s</p>'
            '%s'
            '</body></html>'
            ) % (headline, body)


def sendmail(sender, sender_alias, password, server, port, user, user_alias, title, content):
    '''
    Utility to send mail

    :param sender: string, the email address of the sender
    :param sender_alias: string, the alias of the sender name
    :param password: string, the password or token of the sender's email
    :param server: string, the smtp domain of sender's email
    :param port: int, the port no of smtp service
    :param user: string, the receiver email address
    :param user_alias: string, the name of the receiver
    :param title: string, the title of the email
    :param content: string, the content of the email
    :return: boolen, true for success sending
    '''
    ret = (True, None)
    try:
        msg = MIMEText(content, 'html', 'utf-8')
        msg['From'] = formataddr([sender_alias, sender])
        msg['To'] = formataddr([user_alias, user])
        msg['Subject'] = title

        server = smtplib.SMTP_SSL(server, port)
        server.login(sender, password)
        server.sendmail(sender, [user], msg.as_string())
        server.quit()
    except Exception as e:
        ret = (False, e)
    return ret
