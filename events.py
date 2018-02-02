import logging

logging.basicConfig(level=logging.info)
LOG = logging.getLogger(name="events")


class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


class Events(Singleton):
    """ A class that helps to keep custom eventhandling more organized and robust

    Notes:
        Avoids double registrations of events and provides a simple interface
        for event registration & deregistration
        Pause mechanism to prevent events from running temporarily
        Application agnostic through adder/remover callable.

    """

    __data = {}  # all event data
    __paused = {}  # temporary event data storage for paused events

    @property
    def data(self):
        """ dictionary that holds the registered eventNames and their values

        Returns:
            dict: current data

        """
        return self.__data

    @data.setter
    def data(self, callbacks):
        """ setter of the dictionary that holds the registered event names and their values

        Args:
            callbacks (dict):

        Returns:

        """
        assert isinstance(callbacks, dict)
        self.__data = callbacks

    @property
    def registered_events(self):
        """ all registered event names

        Returns:
            list: event names

        """
        return self.data.keys()

    @property
    def paused_events(self):
        """ all paused events

        Returns:
            list: event names of events that are in paused state

        """
        return [key for key, value in self.data.iteritems() if value["paused"]]

    def add_event(self, event_name, adder, owner=None, description="", remover=None, adder_args=(), adder_kwargs={}, remover_args=(), remover_kwargs={}):
        """ registers an event

        Args:
            event_name (str): event name identified
            adder (callable): caller responsible for callback addition
            owner (str): event owner
            description (str): event description
            remover (callable): caller responsible
            adder_args (tuple): arguments the adder needs
            adder_kwargs (dict): keyword arguments the adder needs
            remover_args (tuple): arguments the remover needs
            remover_kwargs (dict): keyword arguments the remover needs

        Returns:

        """
        if event_name in self.data:
            LOG.warning('Event name already exits. Skipped adding event. Use the override flag to override the event.')
            return
        else:
            # returning callback values have to be stored within a list
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
                ids = adder(*adder_args, **adder_kwargs)
                # keep the callers return value mutable
                # this makes sense if we have to pause events, where a returned callback id will change
                # and we have to update it
                # the idea here is not to create new objects when readding/resuming an event
                # and just modify the existing object, otherwise we wouldn't be able to update the returned value
                # easily for a registered event
                if not isinstance(ids, list):
                    event_data["id_list"] = [ids]
                else:
                    event_data["id_list"] = ids
                self.data[event_name] = event_data
                LOG.info('Added event named %s' % event_name)
            except RuntimeError:
                LOG.error('Failed to register callback.', exc_info=True)

    def attach_remover(self, event_name, caller, callable_args=(), callable_kwargs={}):
        """ attaches a remover callable to an existing event

        Notes:
            This can be useful or even required if the remover needs access to data that was returned by the adder
            callable. When using add_event() the remover can't have access to that data when getting stored,
            this is why a remover can be attached later.
            The return value is stored inside the data attribute as "id_list".

        Args:
            event_name: registered event name
            caller: callable that will be used to remove the event callback
            callable_args: callable arguments tuple
            callable_kwargs: callabe keyword arguments dictionary

        Returns:

        """
        assert event_name in self.registered_events, "No event named '{0}' registered".format(event_name)

        data = self.data.copy()
        data[event_name]["remover"] = caller
        data[event_name]["remover_args"] = callable_args
        data[event_name]["remover_kwargs"] = callable_kwargs

        self.data = data

    def remove_event(self, event_name, restore_on_fail=False):
        """ base method to deregister an event

        Args:
            event_name (str): registered event name identifier
            restore_on_fail (bool): restores the given event if it can't ge removed (currently not implement)

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

    def pause_events(self, exclude=[]):
        """ pause all events

        Args:
            exclude (list): if set it will exclude given events from setting paused

        Returns:

        """
        for event_name, event_data in self.data.iteritems():
            if not event_data["paused"] and not event_name in exclude:
                self.pause_event(event_name)

    def resume_event(self, event_name):
        """ resumes a previous paused event

        Args:
            event_name (str): registered event name identified

        Returns:

        """
        event_data = self._get_event_data(event_name)
        if event_data:
            # we don't have to assert an adder callable because this is required when adding events
            adder, args, kwargs = event_data["adder"], event_data["adder_args"], event_data["adder_kwargs"]
            assert event_data["paused"], "Event '{0}' is not paused. Nothing to resume.".format(event_name)

            # execute callable and store the id in case the corresponding callback returns something
            # like a hash or object that will be needed to remove it later
            _id = adder(*args, **kwargs)
            self.data[event_name] = event_data
            self._replace_id_list(event_name, [_id])
            self._toggle_paused_state(event_name)
            LOG.info("Resumed event '{0}'".format(event_name))

    def resume_paused_events(self):
        """ resumes all paused events

        Returns:

        """
        for event_name, event_data in self.data.iteritems():
            if event_data["paused"]:
                self.resume_event(event_name)

    def _get_event_data(self, event_name):
        """ get the sub-dictionary for a specific event

        Args:
            event_name (str): registered event name identifier

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
        for _id in event_data["id_list"]:
            event_data["id_list"].remove(_id)
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


class SuppressEvents(object):
    """ Decorator that allows to suppress given event

    It will prevent the given event from running, call the function and resumes the event.
    Examples:
        @SuppressEvent("my_event")
        def do_something():
            print("Do something")

        @SuppressEvent("my_second_event")
        def do_something_else():
            print("Do something else")
    """
    events = Events()

    def __init__(self, event_name_or_names):
        """ needs a registered event name as argument

        Args:
            event_name_or_names: registered event name
        """
        self._event_name_or_names = event_name_or_names

    def __call__(self, func):
        def inner(*args, **kwargs):
            if isinstance(self._event_name_or_names, str):
                event_names = [self._event_name_or_names]
            else:
                event_names = self._event_name_or_names

            unknown = [event for event in event_names if event not in self.events.registered_events]

            assert not unknown, "Unknown events: " + " ".join(unknown) + ".Please ensure the event was registered."

            # pause events
            for event_name in event_names:
                self.events.pause_event(event_name)
            result = func(*args, **kwargs)
            # resume events
            for event_name in event_names:
                self.events.resume_event(event_name)
            return result
        return inner
