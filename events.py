import logging

from lib import Singleton

LOG = logging.getLogger(name="CocoNodz.events")


class Events(Singleton):
    """ base class other specific event classes should inherit from, which includes the base methods for adding
    and removing events

    This class should help to keep custom eventhandling more organized
    """

    __data = {}
    __paused = {}

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

    @property
    def paused_events(self):
        """ all paused events

        Returns:

        """
        return [key for key, value in self.data.iteritems() if value["paused"]]


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
            # returning callback values have to be stored within a list
            # the idea is not to create new objects when readding/resuming an event and just modify the existing object
            # otherwise we wouldn't be able to update the returned value easily for a registered event
            try:
                event_data = {"adder": adder,
                              "adder_args": adder_args,
                              "adder_kwargs": adder_kwargs,
                              "remover": remover,
                              "remover_args": remover_args,
                              "remover_kwargs": remover_kwargs,
                              "paused": False,
                              "id_list": [],
                              "owner": owner,
                              "description": description
                              }

                event_data["id_list"] = [adder(*adder_args, **adder_kwargs)]
                self.data[event_name] = event_data
                LOG.info('Added event named %s' % event_name)

            except RuntimeError:
                LOG.error('Failed to register callback.', exc_info=True)

    def attach_remover(self, event_name, callable, callable_args=(), callable_kwargs={}):
        """ adds a remover callable to an existing event

        This can be useful if the remover will need access to the previous created event_data of the
        registered event, like for example the id_list

        Args:
            event_name: registered event name
            callable: callable that will be used to remove the event callback
            callable_args: callable arguments tuple
            callable_kwargs: callabe keyword arguments dictionary

        Returns:

        """
        assert event_name in self.registered_events, "No event named '{0}' registered".format(event_name)

        data = self.data.copy()
        data[event_name]["remover"] = callable
        data[event_name]["remover_args"] = callable_args
        data[event_name]["remover_kwargs"] = callable_kwargs

        self.data = data

    def remove_event(self, event_name, restore_on_fail=False):
        """ base method to deregister an event

        Args:
            event_name: registered event name
            restore_on_fail: will restore an event in case it can't be removed (currently not implement)

        Returns:

        """

        if restore_on_fail:
            raise NotImplementedError

        data_copy = self.data.copy()
        remover, args, kwargs = self._get_event_remover(event_name)

        try:
            remover(*args, **kwargs)
            self._remove_from(data_copy, event_name)
            self.data = data_copy
            LOG.info("Removed event '{0}'".format(event_name))
        except RuntimeError:
            LOG.error("Not able to remove event '{0}'".format(event_name), exc_info=True)

    def pause_event(self, event_name):
        """ temporary removes an event, but keep it stored within the events

        Args:
            event_name: registered event name

        Returns:

        """
        remover, args, kwargs = self._get_event_remover(event_name)

        try:
            remover(*args, **kwargs)
            self._toggle_paused_state(event_name)
            LOG.info("Paused event '{0}'".format(event_name))
        except RuntimeError:
            LOG.error("Not able to pause event '{0}'".format(event_name))

    def resume_event(self, event_name):
        """ resumes a previous paused event

        Args:
            event_name: registered event name

        Returns:

        """
        event_data = self._get_event_data(event_name)
        if event_data:
            # we don't have to assert an adder callable because this is required when adding events
            adder, args, kwargs = event_data["adder"], event_data["adder_args"], event_data["adder_kwargs"]
            assert event_data["paused"], "Event '{0}' is not paused. Nothing to resume.".format(event_name)

            # execute callable and store the id in case the corresponding callback returns something
            # like a hash or object that will be needed to remove it later
            id = adder(*args, **kwargs)
            self.data[event_name] = event_data
            self._replace_id_list(event_name, [id])
            self._toggle_paused_state(event_name)

    def _get_event_data(self, event_name):
        """ get the subdict for a specific event

        Args:
            event_name: registered event name

        Returns:

        """
        if event_name in self.data.keys():
            return self.data[event_name]
        else:
            LOG.info("Event '{0}' doesn't exist.".format(event_name))
            return {}

    def _get_event_remover(self, event_name):
        """ get the events remover callable, its args and kwargs

        Args:
            event_name: registered event name

        Returns: (callable, args tuple, kwargs dict)

        """
        event_data = self._get_event_data(event_name)
        if event_data:
            assert event_data["remover"], "No event remover callable attached"
            return event_data["remover"], event_data["remover_args"], event_data["remover_kwargs"]

    def _toggle_paused_state(self, event_name):
        """ toggles the stored paused state

        Args:
            event_name: registered event name

        Returns: bool of the new state

        """
        state_name = "paused"
        event_data = self._get_event_data(event_name)
        if event_data[state_name]:
            event_data[state_name] = False
            self.data[event_name] = event_data
            return False
        else:
            event_data[state_name] = True
            self.data[event_name] = event_data
            return True

    def _replace_id_list(self, event_name, new_id_list):
        """ removes all items from id_list for a given event and appends the new items

        This is a helper function that will not create a new list in the id_list event_data,
        but modifies the existing one like it would be a new list. This is necessary because we don't
        want to create a new object and just mutate the existing one.

        Args:
            event_name: registered event name
            new_id_list: list with updated ids

        Returns:

        """
        event_data = self.data[event_name]
        for id in event_data["id_list"]:
            event_data["id_list"].remove(id)
        for new_id in new_id_list:
            event_data["id_list"].append(new_id)

    @staticmethod
    def _remove_from(dictionary, key):
        """ simple helper function to remove a key from a dictionary

        Args:
            dictionary: dictionary
            key: key

        Returns:

        """
        try:
            del dictionary[key]
        except KeyError:
            LOG.error('Not able to remove key {0} from dictionary {0}'.format(dictionary, key), exc_info=True)

    def remove_all_events(self):
        """ removes all registered events

        Please be aware that it will only remove events if all of them have a remover callable attached

        Returns:

        """
        for event in self.registered_events:
            assert self.data[event]["remover"], "No remover attached for event '{0}'. Skipped process".format(event)

        for event in self.registered_events:
            self.remove_event(event)
