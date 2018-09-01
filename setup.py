from host import Vulnerability, ConfigurationOption, Service, OperatingSystem


def populate_database():
    if OperatingSystem.objects(name='Ubuntu', version='14.04').first() is None:
        ubuntu = OperatingSystem(kernel='LINUX', name='Ubuntu', version='14.04', box='ubuntu/trusty64')
        ubuntu.save()

    if Service.objects(name='apache_ubuntu').first() is None:
        options = {
            'user': ConfigurationOption(name='Run As User', description='User to run the service as.', type='USER'),
            'port': ConfigurationOption(name='Port', description='Port to listen on.', type='INT'),
            'php': ConfigurationOption(name='Install PHP', description='Whether to install PHP or not.', type='BOOLEAN'),
            'files': ConfigurationOption(name='Server Files', description='Files to serve.', type='FILE'),
            'wwwroot': ConfigurationOption(name='Webserver Directory', description='Directory to serve the files from', type='STRING')
        }
        apache2 = Service(name='apache_ubuntu', full_name='Apache Web Server', version='2', options=options)
        apache2.save()

    if Service.objects(name='sudo_ubuntu').first() is None:
        sudo_options = {
            'users': ConfigurationOption(name='Sudoers', description='List of sudoers', type='USER', list=True, default=[])
        }
        sudo = Service(name='sudo_ubuntu', full_name='sudo', version='?', options=sudo_options)
        sudo.save()

        sudo = Service.objects(name="sudo_ubuntu").first()
        ubuntu = OperatingSystem.objects(name='Ubuntu').first()
        ubuntu.services = [sudo]
        ubuntu.save()

    if Service.objects(name='mysql_ubuntu').first() is None:
        options = {
            'user': ConfigurationOption(name='Run As User', description='User to run the service as.', type='USER'),
            'port': ConfigurationOption(name='Port', description='Port to listen on.', type='INT', default='3306'),
            'password': ConfigurationOption(name='Root Password')
        }
        mysql = Service(name='mysql_ubuntu', full_name='MySQL Server', version='5.0.15', options=options)

        local = Vulnerability(name='local_mysql', full_name='MySQL UDF Local Privilege Escalation',
                              category='Privilege Escalation', requirements=['mysql_ubuntu'], options={})
        local.save()
        mysql.vulnerabilities = [local]
        mysql.save()

    if Service.objects(name='mediawiki_ubuntu').first() is None:
        options = {
            'admin_username': ConfigurationOption(name='Wiki Admin Account Name', default='admin'),
            'admin_password': ConfigurationOption(name='Wiki Admin Account Password', default='password'),
            'db_username': ConfigurationOption(name='Wiki Database User', default='wikiuser'),
            'db_password': ConfigurationOption(name='Wiki Database Password', default=''),
            'host_directory': ConfigurationOption(name='Wiki install location'),
            'database': ConfigurationOption(name='Database', type='SERVICE'),
            'webserver': ConfigurationOption(name='Web Server', type='SERVICE')
        }
        mw = Service(name='mediawiki_ubuntu', full_name='MediaWiki', version='1.22.1', options=options)
        mw.save()

    if Service.objects(name='webcalendar_ubuntu').first() is None:
        options = {
            'webserver': ConfigurationOption(name='Web Server', type='SERVICE'),
            'host_directory': ConfigurationOption(name='Calendar install location')
        }
        s = Service(name='webcalendar_ubuntu', full_name='WebCalendar', version='1.2.4', options=options)

        vuln = Vulnerability.objects(name='rce_webcalendar').first()
        if vuln is None:
            vuln = Vulnerability(name='rce_webcalendar', full_name='WebCalendar index.php Remote Code Execution',
                                 category='Remote Code Execution', cve='CVE-2012-1495, CVE-2012-1496')
            vuln.save()

        s.vulnerabilities = [vuln]
        s.save()

    if Service.objects(name='vcms_php').first() is None:
        options = {
            'webserver': ConfigurationOption(name='Web Server', type='SERVICE'),
            'host_directory': ConfigurationOption(name='Relative Install location'),
            'database': ConfigurationOption(name='Database', type='SERVICE')
        }
        s = Service(name='vcms_php', full_name='V-CMS', version='1.0', options=options)
        v = Vulnerability.objects(name='rce_vcms').first()

        if v is None:
            v = Vulnerability(name='rce_vcms', full_name='V-CMS PHP File Upload and Execute',
                              category='Remote Code Execution', cve='CVE-2011-4828')
            v.save()

        s.vulnerabilities = [v]
        s.save()

    if Vulnerability.objects(name='rce_mediawiki').first() is None:
        options = {
            'mediawiki': ConfigurationOption(name='Affected MediaWiki Install', type='SERVICE'),
            'webserver': ConfigurationOption(name='Affected Web Server', type='SERVICE')
        }

        v = Vulnerability(name='rce_mediawiki', full_name='MediaWiki thumb.php Remote Command Execution',
                          cve="CVE-2014-1610", category='Remote Code Execution', options=options)
        v.save()

    if Vulnerability.objects(name='rfi_apache') is None:
        options = {
            'file': ConfigurationOption(name='Vulnerable File', description='File that is affected by the vulnerability',
                                        type='FILE'),
            'service': ConfigurationOption(name='Affected Service', type='SERVICE')
        }

        rfi = Vulnerability(name='rfi_apache', full_name='PHP Remote File Inclusion',
                            category='File Inclusion', requirements=['apache_ubuntu'], options=options)
        rfi.save()
