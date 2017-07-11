import logging

_LOG = logging.getLogger(name="CocoNodz.events")


class Events(object):
    """ base class other specific event classes should inherit from, which includes the base methods for adding
    and removing events

    This class should help to keep custom eventhandling more organized
    """

    def __init__(self):
        self.__callbacks = {}

    @property
    def callbacks(self):
        """ dictionary that holds the registered eventNames and their values

        Returns: dictionary

        """
        return self.__callbacks

    @callbacks.setter
    def callbacks(self, callbacks):
        """ setter of the dictionary that holds the registered event names and their values

        Args:
            callbacks dictionary

        Returns:

        """
        assert isinstance(callbacks, dict)
        self.__callbacks = callbacks

    @property
    def callbacks_copy(self):
        """ an explicit copy of the dictionary that holds the registered eventNames and their values, this has to be
        used when removing events

        Returns:

        """
        return self.callbacks.copy()

    @property
    def registered_events(self):
        """ all registered event names

        Returns: list with event names

        """
        return self.callbacks_copy.keys()

    def add_event(self, event_name, callable, *callable_args, **callable_kwargs):
        """ base method to register an event

        Args:
            event_name: name identified for the event
            callable: callable function or callable for the event
            *callable_args: arguments that will be passed to the callable
            **callable_kwargs: keyword arguments that will be passed to the callable

        Returns: value, which should be a callback ID/hash

        """
        if self.callbacks.has_key(event_name):
            _LOG.error('Event name already exits. Skipped adding event. Use the override flag to override the event.')
        else:
            try:
                callbacks = self.callbacks
                _callback = callable(*callable_args, **callable_kwargs)
                callbacks[event_name] = _callback
                _LOG.info('Added event named %s' % event_name)
                self.callbacks = callbacks
                return _callback
            except RuntimeError:
                _LOG.error('Failed to register callback.', exc_info=True)

    def remove_event(self, event_name, callable, *callable_args, **callable_kwargs):
        """ base method to deregister an event

        Args:
            event_name: name the event was registered for
            callable: callable that will be called when removing the event (mostly this should be a specific remove callback/event function)
            *callable_args: arguments that will be passed to the callable
            **callable_kwargs: keyword arguments that will be passed to the callable

        Returns:

        """
        if self.callbacks.has_key(event_name):
            try:
                callbacks = self.callbacks
                callable(*callable_args, **callable_kwargs)
                del callbacks[event_name]
                self.callbacks = callbacks
                _LOG.info('Removed event %s' % event_name)
            except RuntimeError:
                _LOG.error('Not able to remove event {0}'.format(event_name), exc_info=True)

    def registerCallbacks(self):
        """!@brief main method to overwrite to register all related events

        """
        raise NotImplementedError

    def deregisterCallbacks(self):
        """!@brief main method to overwrite to deregister all related events

        """
        raise NotImplementedError