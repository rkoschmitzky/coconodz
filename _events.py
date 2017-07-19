import logging

from lib import Singleton

LOG = logging.getLogger(name="CocoNodz.events")


class Events(Singleton):
    """ base class other specific event classes should inherit from, which includes the base methods for adding
    and removing events

    This class should help to keep custom eventhandling more organized
    """

    __data = {}

    @property
    def data(self):
        """ dictionary that holds the registered eventNames and their values

        Returns: dictionary

        """
        return self.__data

    @data.setter
    def data(self, callbacks):
        """ setter of the dictionary that holds the registered event names and their values

        Args:
            callbacks dictionary

        Returns:

        """
        assert isinstance(callbacks, dict)
        self.__data = callbacks

    @property
    def registered_events(self):
        """ all registered event names

        Returns: list with event names

        """
        return self.data.keys()

    def add_event(self, event_name, adder, owner=None, description="", remover=None, adder_args=(), adder_kwargs={}, remover_args=(), remover_kwargs={}):
        """ base method to register an event

        Args:
            event_name: name identified for the event
            adder: callable function or callable for the event
            *adder_callable_args: arguments that will be passed to the callable
            **adder_callable_kwargs: keyword arguments that will be passed to the callable

        Returns: value, which should be a callback ID/hash

        """
        if event_name in self.data:
            LOG.warning('Event name already exits. Skipped adding event. Use the override flag to override the event.')
            return
        else:
            try:
                event_data = {"adder": adder,
                              "adder_args": adder_args,
                              "adder_kwargs": adder_kwargs,
                              "remover": remover,
                              "remover_args": remover_args,
                              "remover_kwargs": remover_kwargs,
                              "id": None,
                              "owner": owner,
                              "description": description}

                event_data["id"] = adder(*adder_args, **adder_kwargs)
                self.data[event_name] = event_data
                LOG.info('Added event named %s' % event_name)

            except RuntimeError:
                LOG.error('Failed to register callback.', exc_info=True)

    def remove_event(self, event_name):
        """ base method to deregister an event

        Args:
            event_name: name the event was registered for
            callable: callable that will be called when removing the event (mostly this should be a specific remove callback/event function)
            *callable_args: arguments that will be passed to the callable
            **callable_kwargs: keyword arguments that will be passed to the callable

        Returns:

        """
        data_copy = self.data.copy()
        if event_name in self.data.keys():
            assert self.data[event_name]["remover"], "No event remover callable attached"
            remover = self.data[event_name]["remover"]
            event_data = self.data[event_name]
            try:
                remover(*event_data["remover_args"], **event_data["remover_kwargs"])
                del data_copy[event_name]
                self.data = data_copy
                LOG.info('Removed event %s' % event_name)
            except RuntimeError:
                LOG.error('Not able to remove event {0}'.format(event_name), exc_info=True)