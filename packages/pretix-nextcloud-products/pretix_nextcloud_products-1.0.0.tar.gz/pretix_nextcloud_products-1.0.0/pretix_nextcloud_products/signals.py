# Register your receivers here
from django.dispatch import receiver
from pretix.base.signals import item_copy_data, register_ticket_outputs
from pretix.control.signals import item_forms

from .forms import NextcloudProductItemForm
from .models import NextcloudProductItem


@receiver(register_ticket_outputs, dispatch_uid="nextcloud_share_output")
def register_ticket_output(sender, **kwargs):
    from .ticketoutput import NextcloudShareTicketOutput

    return NextcloudShareTicketOutput


@receiver(item_forms, dispatch_uid="nextcloud_item_forms")
def control_item_forms(sender, request, item, **kwargs):
    try:
        inst = NextcloudProductItem.objects.get(item=item)
    except NextcloudProductItem.DoesNotExist:
        inst = NextcloudProductItem(item=item)
    return NextcloudProductItemForm(
        instance=inst,
        data=(request.POST if request.method == "POST" else None),
        prefix="nextcloudproductitem",
    )


@receiver(item_copy_data, dispatch_uid="badges_item_copy")
def copy_item(sender, source, target, **kwargs):
    try:
        inst = NextcloudProductItem.objects.get(item=source)
        NextcloudProductItem.objects.create(
            item=target, nextcloud_path=inst.nextcloud_path
        )
    except NextcloudProductItem.DoesNotExist:
        pass
