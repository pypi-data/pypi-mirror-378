from typing import Tuple

from collections import OrderedDict
from django import forms
from django.utils.translation import gettext_lazy as _
from pretix.base.models import OrderPosition
from pretix.base.ticketoutput import BaseTicketOutput


class NextcloudShareTicketOutput(BaseTicketOutput):
    identifier = "nextcloud"
    verbose_name = _("Nextcloud share")
    download_button_text = _("Download")
    long_download_button_text = _("Download product")
    preview_allowed = False
    multi_download_enabled = False

    @property
    def settings_form_fields(self) -> dict:
        return OrderedDict(
            list(super().settings_form_fields.items())
            + [
                (
                    "nextcloud_url",
                    forms.CharField(
                        label=_("Nextcloud URL"),
                        help_text=_("Root URL of the Nextcloud instance"),
                        required=True,
                    ),
                ),
                (
                    "nextcloud_username",
                    forms.CharField(
                        label=_("Nextcloud username"),
                        help_text=_(
                            "Username of the Nextcloud user used for creating shares"
                        ),
                        required=True,
                    ),
                ),
                (
                    "nextcloud_password",
                    forms.CharField(
                        label=_("Nextcloud password"),
                        help_text=_(
                            "Password of the Nextcloud user used for creating shares"
                        ),
                        required=True,
                    ),
                ),
            ]
        )

    def generate(self, position: OrderPosition) -> Tuple[str, str, str]:
        share = position.item.nextcloud_product.create_share(position)
        return ("download", "text/uri-list", share.share_url)
