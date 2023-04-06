import json

from django import template
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ontask import LOGGER
from ontask.django_auth_lti.thread_local import get_current_request

register = template.Library()


class ResourceLinkIdNode(template.Node):
    def render(self, context):
        request = get_current_request()
        if request:
            rli = request.LTI.get('resource_link_id')
            if rli:
                return format_html(
                    "<input type='hidden' name='resource_link_id' value='{}' />",
                    rli)
            else:
                LOGGER.warning(
                    _('Failed to find resource_link_id '
                      + 'in request context %s'),
                    json.dumps(request.LTI, indent=4))
        else:
            LOGGER.warning(
                _("Failed to get current request from thread_local"))
        return ''


@register.tag
def resource_link_id(parser, token):
    del parser, token
    return ResourceLinkIdNode()
