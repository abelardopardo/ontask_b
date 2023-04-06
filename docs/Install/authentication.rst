.. _authentication:

Authentication
**************

OnTask comes with the following authentication mechanisms: IMS-LTI,
``REMOTE_USER`` variable, basic authentication, and LDAP. The first three
(IMS-LTI, ``REMOTE_USER`` and basic authentication) are enabled by default and used in that order whenever an unauthenticated request is received. It follows a brief description of how to configure them.

.. _ims_lti_config:

- `IMS Learning Tools Interoperability (IMS-LTI)
  <http://www.imsglobal.org/activity/learning-tools-interoperability>`__. LTI
  is a standard developed by the IMS Global Learning Consortium to integrate
  multiple tools within a learning environment. In LTI terms, OnTask is
  configured to behave as a *tool provider* and assumes a *tool consumer* such
  as a Learning Management System to invoke its functionality. Any URL in
  OnTask can be given to the LTI consumer as the point of access.

  Ontask only provides two points of access for LTI requests coming from the
  consumer. One is the URL with suffix ``/lti_entry`` and the second is the
  URL provided by the actions to serve the personalized content (accessible
  through the ``Actions`` menu.

  To allow LTI access you need:

  1) A tool consumer that can be configured to connect with OnTask. This type
     of configuration is beyond the scope of this manual.

  2) A set of pairs key,value in OnTask to be given to the tool consumers so that together with the URL, they are ready to send the requests. The key/value pairs need to be included as an additional variables in the file ``local.env`` in the folder ``settings`` together with other local configuration variables. For example, ::

       LTI_OAUTH_CREDENTIALS=key1=secret1,key2=secret2

  3) OnTask needs to identify those roles from the external tool mapped to the instructor role. This mapping is provided through a list of those roles in the following configuration variable::

       LTI_INSTRUCTOR_GROUP_ROLES=Instructor

  If you change the values of these variables, you need to restart the server so that the new values are in effect. This authentication has only basic functionality and it is assumed to be used only for learners (not for instructors).

- ``REMOTE_USER``. The second method uses `the variable REMOTE_USER
  <https://docs.djangoproject.com/en/2.1/howto/auth-remote-user/#authentication-using-remote-user>`__ that is assumed to be defined by an external application. This method is ideal for environments in which users are already authenticated and are redirected to the OnTask pages (for example, using SAML). If OnTask receives a request from a non-existent user through this channel, it automatically and transparently creates a new user in the platform with the user name stored in the ``REMOTE_USER`` variable. OnTask relies on emails to identify different user names, so if you plan to use this authentication method make sure the value of ``REMOTE_USER`` is the email.

  Additionally, this mode of authentication will be enforced in all requests reaching OnTask. However, this configuration prevents the recording of email reads. Read the section :ref:`email_config` to configure the server to allow such functionality to be properly configured.

- Basic authentication. If the variable ``REMOTE_USER`` is not set in the internal environment of Django where the web requests are served, OnTask resorts to conventional authentication requiring email and password. These credentials are stored in the internal database managed by OnTask.

The API can be accessed using through token authentication. The token can be generated manually through the user profile page. This type of authentication may need some special configuration in the web server (Apache or similar) so that the ``HTTP_AUTHORIZATION`` header is not removed.

.. _ldap_config:

LDAP Authentication
===================

OnTask may also be configured to use LDAP to authenticate users. This is done
through the external package `django-auth-ldap
<https://bitbucket.org/illocution/django-auth-ldap>`__. In its current version,
this authentication mode cannot be combined with the previous ones (this
requires some non-trivial code changes). The following instructions describe
the basic configuration to enable LDAP authentication. For more details check
the `documentation of the django-auth-ldap module
<https://django-auth-ldap.readthedocs.io/en/latest/>`__.

- Stop OnTask (if it is running)

- Make sure your server has installed the development files for OpenLDAP. In
  Debian/Ubuntu, the required packages are::

    libsasl2-dev python-dev libldap2-dev libssl-dev

  In RedHat/CentOS::

    python-devel openldap-devel

- Install the module ``django-auth-ldap``

- Edit the configuration file ``local.env`` and add the following two variable definitions::

    LDAP_AUTH_SERVER_URI=[uri pointing to your ldap server]
    LDAP_AUTH_PASSWORD=[Password to connect to the server]

- Edit the  file ``settings/base.py`` and uncomment the lines that import the ``ldap`` library (``import ldap``) and the lines that import three methods from the ``django_auth_ldap.config`` module (``LDAPSearch``, ``GroupOfNamesType`` and ``LDAPGroupQuery``)

- Locate the section in the file ``settings/base.py`` that contains the variables to configure *LDAP AUTHENTICATION*.

- Uncomment the ones needed for your configuration. Make sure all the information is included to connect to the server, perform the binding, search, and if needed, assign fields to user and group attributes.

- Locate the variable ``AUTHENTICATION_BACKENDS`` in the same file.

- Comment the lines referring to the back-ends ``LTIAuthBackend`` and
  ``RemoteUserBackend``.

- Uncomment the line referring to ``LDAPBackend``.

- Make sure the LDAP server contains the data about the users in the right
  format

- Start the OnTask server.

