"""Functions for LTI Configuration."""
from collections import defaultdict

from lxml import etree, objectify

from .utils import InvalidLTIConfigError

accessors = [
    'title',
    'description',
    'launch_url',
    'secure_launch_url',
    'icon',
    'secure_icon',
    'cartridge_bundle',
    'cartridge_icon',
    'vendor_code',
    'vendor_name',
    'vendor_description',
    'vendor_url',
    'vendor_contact_email',
    'vendor_contact_name'
]


class ToolConfig:
    """Object used to represent LTI configuration.

    Capable of creating and reading the Common Cartridge XML representation of
    LTI links as described here:
        http://www.imsglobal.org/LTI/v1p1pd/ltiIMGv1p1pd.html#_Toc309649689
    """

    def __init__(self, **kwargs):
        """Create a new ToolConfig with the given options."""

        # Initialize all class accessors to None
        for opt in accessors:
            setattr(self, opt, None)

        self.custom_params = kwargs.pop('custom_params') if \
            kwargs.get('custom_params') else defaultdict(lambda: None)
        self.extensions = kwargs.pop('extensions') \
            if kwargs.get('extensions') else defaultdict(lambda: None)

        # Iterate over all provided options and save to class instance members
        for (key, val) in kwargs.items():
            setattr(self, key, val)

    @classmethod
    def create_from_xml(cls, xml):
        """
        Create a ToolConfig from the given XML.
        """
        config = ToolConfig()
        config.process_xml(xml)
        return config

    def set_custom_param(self, key, val):
        """Set a custom parameter to provided value."""
        self.custom_params[key] = val

    def get_custom_param(self, key):
        """Gets a custom parameter. It not yet set, returns None object."""
        return self.custom_params[key]

    def set_ext_params(self, ext_key, ext_params):
        """Set the extension parameters for a specific vendor."""
        self.extensions[ext_key] = ext_params

    def get_ext_params(self, ext_key):
        """Get extension paramaters for provided extension.

        If not set, returns None object.
        """
        return self.extensions[ext_key]

    def set_ext_param(self, ext_key, param_key, val):
        """Set the provided parameter in a set of extension parameters."""
        if not self.extensions[ext_key]:
            self.extensions[ext_key] = defaultdict(lambda: None)
        self.extensions[ext_key][param_key] = val

    def get_ext_param(self, ext_key, param_key):
        """Get specific param in set of provided extension parameters."""
        return self.extensions[ext_key][param_key] \
            if self.extensions[ext_key] else None

    def process_xml(self, xml):
        """Parse tool configuration in the Common Cartridge LTI link XML."""
        root = objectify.fromstring(xml, parser=etree.XMLParser())
        # Parse all children of the root node
        for child in root.getchildren():
            if 'title' in child.tag:
                self.title = child.text
            if 'description' in child.tag:
                self.description = child.text
            if 'secure_launch_url' in child.tag:
                self.secure_launch_url = child.text
            elif 'launch_url' in child.tag:
                self.launch_url = child.text
            if 'icon' in child.tag:
                self.icon = child.text
            if 'secure_icon' in child.tag:
                self.secure_icon = child.text
            if 'cartridge_bundle' in child.tag:
                self.cartridge_bundle = child.attrib['identifierref']
            if 'catridge_icon' in child.tag:
                self.cartridge_icon = child.atrib['identifierref']

            if 'vendor' in child.tag:
                # Parse vendor tag
                for v_child in child.getchildren():
                    if 'code' in v_child.tag:
                        self.vendor_code = v_child.text
                    if 'description' in v_child.tag:
                        self.vendor_description = v_child.text
                    if 'name' in v_child.tag:
                        self.vendor_name = v_child.text
                    if 'url' in v_child.tag:
                        self.vendor_url = v_child.text
                    if 'contact' in v_child.tag:
                        # Parse contact tag for email and name
                        for c_child in v_child:
                            if 'name' in c_child.tag:
                                self.vendor_contact_name = c_child.text
                            if 'email' in c_child.tag:
                                self.vendor_contact_email = c_child.text

            if 'custom' in child.tag:
                # Parse custom tags
                for custom_child in child.getchildren():
                    self.custom_params[custom_child.attrib['name']] = \
                        custom_child.text

            if 'extensions' in child.tag:
                platform = child.attrib['platform']
                properties = {}

                # Parse extension tags
                for ext_child in child.getchildren():
                    if 'property' in ext_child.tag:
                        properties[ext_child.attrib['name']] = ext_child.text
                    elif 'options' in ext_child.tag:
                        opt_name = ext_child.attrib['name']
                        options = {}
                        for option_child in ext_child.getchildren():
                            options[option_child.attrib['name']] = \
                                option_child.text
                        properties[opt_name] = options

                self.set_ext_params(platform, properties)

    def to_xml(self, opts=defaultdict(lambda: None)):
        """Generate XML from the current settings."""
        del opts
        if not self.launch_url or not self.secure_launch_url:
            raise InvalidLTIConfigError('Invalid LTI configuration')

        NSMAP = {
            'blti': 'http://www.imsglobal.org/xsd/imsbasiclti_v1p0',
            'xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'lticp': 'http://www.imsglobal.org/xsd/imslticp_v1p0',
            'lticm': 'http://www.imsglobal.org/xsd/imslticm_v1p0',
        }

        root = etree.Element('cartridge_basiclti_link', attrib={
            '{%s}%s' % (NSMAP['xsi'], 'schemaLocation'):
                'http://www.imsglobal.org/xsd/imslticc_v1p0 '
                'http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd '
                'http://www.imsglobal.org/xsd/imsbasiclti_v1p0 '
                'http://www.imsglobal.org/xsd/lti/ltiv1p0/'
                'imsbasiclti_v1p0p1.xsd '
                'http://www.imsglobal.org/xsd/imslticm_v1p0 '
                'http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd '
                'http://www.imsglobal.org/xsd/imslticp_v1p0 '
                'http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd',
            'xmlns': 'http://www.imsglobal.org/xsd/imslticc_v1p0'
        }, nsmap=NSMAP)

        for key in ['title', 'description', 'launch_url', 'secure_launch_url']:
            option = etree.SubElement(root, '{%s}%s' % (NSMAP['blti'], key))
            option.text = getattr(self, key)

        vendor_keys = ['name', 'code', 'description', 'url']
        if any('vendor_' + key for key in vendor_keys) or \
                self.vendor_contact_email:
            vendor_node = etree.SubElement(
                root,
                '{%s}%s' % (NSMAP['blti'], 'vendor'))
            for key in vendor_keys:
                if getattr(self, 'vendor_' + key) is not None:
                    v_node = etree.SubElement(
                        vendor_node,
                        '{%s}%s' % (NSMAP['lticp'], key))
                    v_node.text = getattr(self, 'vendor_' + key)
            if getattr(self, 'vendor_contact_email'):
                v_node = etree.SubElement(
                    vendor_node,
                    '{%s}%s' % (NSMAP['lticp'], 'contact'))
                c_name = etree.SubElement(
                    v_node,
                    '{%s}%s' % (NSMAP['lticp'], 'name'))
                c_name.text = self.vendor_contact_name
                c_email = etree.SubElement(
                    v_node,
                    '{%s}%s' % (NSMAP['lticp'], 'email'))
                c_email.text = self.vendor_contact_email

        # Custom params
        if len(self.custom_params) != 0:
            custom_node = etree.SubElement(root, '{%s}%s' % (NSMAP['blti'],
                                                             'custom'))
            for (key, val) in sorted(self.custom_params.items()):
                c_node = etree.SubElement(custom_node, '{%s}%s'
                                          % (NSMAP['lticm'], 'property'))
                c_node.set('name', key)
                c_node.text = val

        # Extension params
        if len(self.extensions) != 0:
            for (key, params) in sorted(self.extensions.items()):
                extension_node = etree.SubElement(root,
                                                  '{%s}%s' % (NSMAP['blti'],
                                                              'extensions'),
                                                  platform=key)
                for key, val in params.items():
                    if isinstance(val, dict):
                        options_node = etree.SubElement(
                            extension_node,
                            '{%s}%s' % (NSMAP['lticm'], 'options'),
                            name=key)
                        for key, val in val.items():
                            property_node = etree.SubElement(
                                options_node,
                                '{%s}%s' % (NSMAP['lticm'], 'property'),
                                name=key)
                            property_node.text = val
                    else:
                        param_node = etree.SubElement(
                            extension_node,
                            '{%s}%s' % (NSMAP['lticm'], 'property'),
                            name=key)
                        param_node.text = val

        if getattr(self, 'cartridge_bundle'):
            etree.SubElement(
                root,
                'cartridge_bundle',
                identifierref=self.cartridge_bundle)

        if getattr(self, 'cartridge_icon'):
            etree.SubElement(
                root,
                'cartridge_icon',
                identifierref=self.cartridge_icon)

        return '<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(root)
