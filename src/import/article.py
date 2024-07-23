"""
article.py
Contains Article class used for importing Usenet News articles.
"""

import email
import json
from dateutil import parser


class Article:
    """
    Represents a single article.
    """

    def __init__(self, article_id, headers, body):
        self.from_name = None
        self.from_email = None
        self.date = None
        self.headers = headers
        self.article_id = article_id
        self.body = body
        self.references = headers['references']

        self.set_from(headers['from_raw'])
        self.set_date(headers['date'])

    def set_date(self, date):
        """
        Parse date field and set it.
        :param date:
        :return:
        """
        loc = date.find(" (LOCAL)")
        if loc != -1:
            date = date[:loc]

        # Set tzinfos to map BST (British Summer Time) to UTC+1
        tzinfos = {
            'BST': 3600
        }
        self.date = parser.parse(date, tzinfos=tzinfos)

    def set_from(self, from_raw):
        """
        Set 'from': split in name and email when possible. This can follow three different formats.

        @see https://datatracker.ietf.org/doc/html/rfc1036#section-2.1.1
        :param from_raw: Raw string containing the 'from' name and email
        :return:
        """
        if '<' in from_raw:
            # Format "First Last <email@address.com>"
            from_parts = from_raw.split('<')
            self.from_email = from_parts[-1].strip('> ')
            self.from_name = '<'.join(from_parts[:-1]).strip(' ')
        elif '(' in from_raw:
            # Format: "email@address.com (First Last)"
            from_parts = from_raw.split('(')
            self.from_name = from_parts[-1].strip(') ')
            self.from_email = '('.join(from_parts[:-1]).strip(' ')
        else:
            # Format: "email@address.com"
            self.from_name = 'No name given'
            self.from_email = from_raw

    def to_dict(self):
        """
        Get a dictionary representation of the article.
        :return:
        """
        return {
            'id': self.article_id,
            'path': self.headers['path'],
            'folder': self.headers['location'],
            'from_name': self.from_name,
            'from_email': self.from_email,
            'newsgroups': self.headers['newsgroups'],
            'subject': self.headers['subject'],
            'message_id': self.headers['subject'],
            'date': self.date.isoformat(),
            'year': self.date.year,
            'x_gateway': self.headers['x_gateway'],
            'lines': self.headers['lines'],
            'xref': self.headers['xref'],
            'references': self.references,
            'body': self.body,
        }

    def to_json(self):
        """
        Get a JSON representation of the object.
        :return:
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_file(path):
        """
        Create a new Article object from a file.
        :param path: Path to file
        :return:
        """
        with open(path, "r", encoding='utf-8', errors='replace') as file:
            msg = email.message_from_file(file)
            if msg.is_multipart():
                body = ''
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdisp = str(part.get_content_disposition())

                    if ctype == 'text/plain' and 'attachment' not in cdisp:
                        body = part.get_payload(decode=True)
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='replace')

        pathstr = str(path)
        path_parts = pathstr.split('/')
        article_id = '-'.join(path_parts[-3:])

        headers = {
            'path': msg['Path'],
            'folder': '/'.join(path_parts[-3:-1]),
            'from_raw': msg['From'],
            'newsgroups': msg.get('Newsgroups', ''),
            'subject': msg['Subject'],
            'message_id': msg['Message-ID'],
            'date': msg['Date'],
            'x_gateway': msg.get('X-Gateway', ''),
            'lines': msg['Lines'],
            'xref': msg['X-Reference'],
            'references': msg.get('References', ''),
        }

        return Article(
            article_id,
            headers,
            body.strip()
        )
