.. _email_config:

Email Configuration
*******************

OnTask relies on the functionality included in Django to send emails from the application. The following variables can be used in the configuration file:

``EMAIL_HOST``
  Host providing the SMTP service.

  Default: ``''``

``EMAIL_PORT``
  Port to communicate with the host

  Default: ``''``

``EMAIL_HOST_USER``
  User account to log into the email host

  Default: ``''``

``EMAIL_HOST_PASSWORD``
  Password for the account to log into the email host

  Default: ``''``

``EMAIL_USE_TLS``
  Boolean stating if the communication should use TLS

  Default: ``False``

``EMAIL_USE_SSL``
  Boolean stating if the communication should use SSL

  Default: ``False``

``EMAIL_ACTION_NOTIFICATION_SENDER``
  Address to use when sending notifications

  Default: ``''``

``EMAIL_HTML_ONLY``
  Send HTML text only, or alternatively, send text and HTML as an attachment

  Default: ``True`` (send HTML only)

``EMAIL_BURST``
  Number of consecutive emails to send before pausing (to adapt to potential throttling of the SMTP server)

  Default: ``0``

``EMAIL_BURST_PAUSE``
  Number of seconds to wait between bursts.

  Default: ``0``


An example of the content in the configuration is::

  EMAIL_HOST=smtp.yourinstitution.org
  EMAIL_PORT=334
  EMAIL_HOST_USER=mailmaster
  EMAIL_HOST_PASSWORD=somepassword
  EMAIL_USE_TLS=False
  EMAIL_USE_SSL=False
  EMAIL_ACTION_NOTIFICATION_SENDER=ontaskmaster@yourinstitution.org
  EMAIL_BURST=500
  EMAIL_BURST_PAUSE=43200


Set theses variables in the configuration file to the appropriate values
before starting the application. Make sure the server is running **in production mode**. The development mode is configured to **not send** emails but show their content in the console instead.

Tracking Email Reads
====================

If OnTask is deployed using SAML, all URLs are likely to be configured to go through the authentication layer. This configuration prevents OnTask from receiving the email read confirmations. In this case, the web server needs to be configured so that the SAML authentication is removed for the URL ``trck`` (the one receiving the email read tracking). In Apache, this can be achieved by the following directive::

  <Location /trck>
    Require all granted
  </Location>

If OnTask is not served from the root of your web server, make sure you include the absolute URL to ``trck``. For example, if OnTask is available through the URL ``my.server.com/somesuffix/ontask``, then the URL to use in the previous configuration is ``my.server.com/somesuffix/ontask/trck``.

