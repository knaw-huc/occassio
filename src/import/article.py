import json
from dateutil import parser
import email


class Article(object):
    """
    Represents a single article.
    """

    def __init__(self, id, folder, path, from_raw, newsgroups, subject, message_id, date, x_gateway, lines, xref,
                 body, references):
        self.from_name = None
        self.from_email = None
        self.date = None
        self.id = id
        self.location = folder
        self.path = path
        self.newsgroups = newsgroups.split(',')
        self.subject = subject
        self.message_id = message_id
        self.x_gateway = x_gateway
        self.lines = lines
        self.xref = xref
        self.body = body
        self.references = references

        self.set_from(from_raw)
        self.set_date(date)

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
            'id': self.id,
            'path': self.path,
            'folder': self.location,
            'from_name': self.from_name,
            'from_email': self.from_email,
            'newsgroups': self.newsgroups,
            'subject': self.subject,
            'message_id': self.message_id,
            'date': self.date.isoformat(),
            'year': self.date.year,
            'x_gateway': self.x_gateway,
            'lines': self.lines,
            'xref': self.xref,
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
        id = '-'.join(path_parts[-3:])
        return Article(
            id,
            '/'.join(path_parts[-3:-1]),
            msg['Path'],
            msg['From'],
            msg.get('Newsgroups', ''),
            msg['Subject'],
            msg['Message-ID'],
            msg['Date'],
            msg.get('X-Gateway', ''),
            msg['Lines'],
            msg.get('Xref', ''),
            body.strip(),
            msg.get('References', '')
        )
