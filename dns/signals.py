# The world is a prison for the believer.

from django.dispatch import Signal

## This event is fired before EaglePanel core start creation of NS Records.
preNSCreation = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished creation NS Records.
postNSCreation = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start creation DNS Zone.
preZoneCreation = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished creation of DNS Zone.
postZoneCreation = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start to add an DNS record.
preAddDNSRecord = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished adding DNS record.
postAddDNSRecord = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start deletion of DNS Record.
preDeleteDNSRecord = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished deletion DNS Record.
postDeleteDNSRecord = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start deletion of a DNS Zone.
preSubmitZoneDeletion = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished deletion of DNS Zone.
postSubmitZoneDeletion = Signal(providing_args=["request", "response"])