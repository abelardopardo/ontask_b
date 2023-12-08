.. _canvas_email_config:

Canvas Configuration
********************

OnTask allows to connect to a `Canvas Learning Management System <https://www.canvaslms.com/>`_ using its API to perform certain operations such as send personalized emails to users's inbox. Configuring this functionality requires permission from Canvas to access its API using OAuth2 authentication. Once this authorization is obtained, the following variables need to be defined in the file configuration file:

``CANVAS_INFO_DICT``
  A dictionary with elements pairs containing the identifier for a Canvas instance that will be shown to the user and a dictionary with the following configuration parameters:

  - ``domain_port``: A string containing the domain and port (if needed) of the Canvas host.

  - ``client_id``: This value is provided by the administrator of the Canvas instance once permission to use the API has been granted.

  - ``client_secret``: This value is provided together with the ``client_id`` once the permission to use the API is granted. It is typically a large random sequence of characters.

   - ``authorize_url``: URL template to access the first step of the authorization. This is usually ``https://{0}/login/oauth2/auth``. The string ``{0}`` is replaced internally with the value of ``domain_port``.

   - ``access_token_url``: URL template to access the token. This is usually ``https://{0}/login/oauth2/token``. The string ``{0}`` is replaced internally with the value of ``domain_port``.

      CANVAS_INFO_DICT = {
          "Server one":
              {"domain_port": "yourcanvasdomain.edu",
               "client_id": "10000000000001",
               "client_secret": "YZnGjbkopt9MpSq2fujUO",
               "authorize_url": "http://{0}/login/oauth2/auth",
               "access_token_url": "http://{0}/login/oauth2/token",
       }

  Make sure you include this information **all in a single line in the configuration file**.

  Default: ``{}`` (Empty dictionary)

``CANVAS_TOKEN_EXPIRY_SLACK``
  The number of seconds to renew a token before it expires. For example, if the variable is 300, any API call performed with a token five minutes before it expires will prompt a token refresh. Here is an example of such definition in ``local.env``::

      CANVAS_TOKEN_EXPIRY_SLACK=300

  Default: 600

After defining these variables, restart the application for the values to be considered. To test the configuration open a workflow, create an action of type ``Personalized canvas email`` and email those messages.

