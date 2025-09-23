from typing import Any

import requests
from datetime import date, datetime, timedelta
from defusedxml import ElementTree
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pretix.base.models import OrderPosition
from urllib.parse import urljoin


class NextcloudProductShare(models.Model):
    order_position = models.ForeignKey(
        "pretixbase.OrderPosition",
        on_delete=models.CASCADE,
        verbose_name=_("Order position"),
        related_name="nextcloud_shares",
    )
    share_id = models.CharField(max_length=255, verbose_name=_("Share ID"))
    share_url = models.URLField(verbose_name=_("Share URL"))
    share_expiration = models.DateTimeField(verbose_name=_("Share expiration"))

    def __str__(self):
        return self.share_id


class NextcloudProductItem(models.Model):
    item = models.OneToOneField(
        "pretixbase.Item",
        null=True,
        blank=True,
        related_name="nextcloud_product",
        on_delete=models.CASCADE,
    )
    nextcloud_path = models.TextField(verbose_name=_("Nextcloud path"))

    def build_url(self, path: str) -> str:
        """Build URL for given path."""
        print(self.item.event.settings.get("ticketoutput_nextcloud_nextcloud_url"))
        return urljoin(
            self.item.event.settings.get("ticketoutput_nextcloud_nextcloud_url"), path
        )

    def do_request(
        self, path: str, method: str = "GET", data: dict[str, Any] | None = None
    ):
        """Build request for given path."""
        username: str = self.item.event.settings.get(
            "ticketoutput_nextcloud_nextcloud_username"
        )
        password: str = self.item.event.settings.get(
            "ticketoutput_nextcloud_nextcloud_password"
        )
        url = self.build_url(path)
        headers = {"OCS-APIRequest": "true"}
        r = requests.request(
            method,
            url,
            data=data,
            auth=(username, password),
            headers=headers,
            timeout=10,
        )
        if not r.ok:
            raise Exception(r.text)
        xml = ElementTree.fromstring(r.content)
        return xml

    def test_connection(self):
        """Test connection to Nextcloud provider."""
        r = self.do_request("/ocs/v1.php/cloud/capabilities")
        return r.find("meta").find("status").text == "ok"

    def get_args_for_share(
        self, order_position: OrderPosition, expire_date: date | None = None
    ) -> dict[str, Any]:
        if not expire_date:
            expire_date = (timezone.now() + timedelta(days=1)).date()
        return {
            "path": self.nextcloud_path,
            "shareType": 3,
            "permissions": 1,
            "expireDate": expire_date.strftime("%Y-%m-%d"),
            "label": _("Personal download link for {name}").format(
                name=order_position.attendee_name
            ),
        }

    def create_share(self, order_position: OrderPosition):
        qs = NextcloudProductShare.objects.filter(
            order_position=order_position, share_expiration__gt=timezone.now()
        )
        if qs.exists():
            return qs.first()
        NextcloudProductShare.objects.filter(order_position=order_position).delete()
        args = self.get_args_for_share(order_position)
        xml = self.do_request(
            "/ocs/v1.php/apps/files_sharing/api/v1/shares", method="POST", data=args
        )
        share_id = xml.find("data").find("id").text
        share_url = xml.find("data").find("url").text
        share_expiration = datetime.strptime(
            xml.find("data").find("expiration").text, "%Y-%m-%d %H:%M:%S"
        )

        return NextcloudProductShare.objects.create(
            order_position=order_position,
            share_id=share_id,
            share_url=share_url,
            share_expiration=share_expiration,
        )

    class Meta:
        ordering = ("id",)
