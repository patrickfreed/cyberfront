import os
import shutil

from mongoengine import Document, StringField, ReferenceField, ListField, EmbeddedDocument, EmbeddedDocumentListField, DictField, \
    EmbeddedDocumentField, MapField

from util import TMP, SERVICES


class OperatingSystem(Document):
    kernel = StringField(options=['WIN', 'LINUX', 'BSD'])  # TODO: ?
    name = StringField()
    accounts = EmbeddedDocumentListField('Account')
    version = StringField()
    box = StringField()


class ConfigurationOption(EmbeddedDocument):
    name = StringField()
    description = StringField()

    key = StringField()
    type = StringField(options=['STRING', 'FILE', 'INT', 'USER', 'BOOLEAN', 'LIST'], default='STRING')


class InstalledService(EmbeddedDocument):
    name = StringField()
    options = DictField()
    files = StringField()
    install = StringField()
    source = ReferenceField('Service')


class Service(Document):
    name = StringField()
    service_name = StringField()
    version = StringField()
    options = MapField(EmbeddedDocumentField(ConfigurationOption))

    def install(self, host, files=dict(), **kwargs):
        host_dir = TMP + host.hostname + '/'
        file_dir = host_dir + self.name + '/'
        outfile = file_dir[:-1].encode('utf-8')

        if not os.path.isdir(host_dir):
            os.mkdir(host_dir)

        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        opts = {}
        install = SERVICES + self.name + '.sh'

        for key, option in self.options.items():
            if option.type == 'FILE':
                f = files.get(key)

                if f is None:
                    print "File not found: " + path
                    return False
                else:
                    path = file_dir + f.filename
                    config = f.filename
                    f.save(path)
            else:
                config = kwargs.get(key)
                if config is None:
                    print "Missing configuration option " + key
                    return False
            opts[key] = config

        if len(files) > 0:
            shutil.make_archive(outfile, 'gztar', TMP + host.hostname, self.name)

        service = InstalledService(name=self.name, options=opts, files=outfile + '.tar.gz', install=install, source=self)
        host.services.append(service)
        host.save()
        return True


class Account(EmbeddedDocument):
    name = StringField()
    password = StringField()
    group = StringField()


class Host(Document):
    hostname = StringField(required=True)
    os = ReferenceField('OperatingSystem')

    services = EmbeddedDocumentListField(InstalledService)
    accounts = EmbeddedDocumentListField(Account)

    vulnerabilities = ListField()

    world = ReferenceField('World')

    # In-Game stuff
    ip = StringField()
    owner = StringField()

    def __init__(self, **kwargs):
        super(Host, self).__init__(**kwargs)

        if self.os is None:
            return

        found = False
        for account in self.os.accounts:
            for input_account in self.accounts:
                if input_account.name == account.name:
                    found = True
                    break
            if found:
                found = False
                continue

            self.accounts.append(account)
