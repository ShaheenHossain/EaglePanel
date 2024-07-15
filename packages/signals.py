# The world is a prison for the believer.
## https://www.youtube.com/watch?v=DWfNYztUM1U

from django.dispatch import Signal

## This event is fired before EaglePanel core load the create package template, this special event is used
## to create a beautiful names official plugin. Actual package creation happes with event named preSubmitPackage and postSubmitPackage.
preCreatePacakge = Signal(providing_args=["request"])

## See info for preCreatePacakge
postCreatePacakge = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start creation a package.
preSubmitPackage = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished creation of a package.
postSubmitPackage = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start deletion of a package.
preSubmitDelete = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished deletion of a package.
postSubmitDelete = Signal(providing_args=["request", "response"])

## This event is fired before EaglePanel core start to modify a package.
preSaveChanges = Signal(providing_args=["request"])

## This event is fired after EaglePanel core finished modifying a package.
postSaveChanges = Signal(providing_args=["request", "response"])