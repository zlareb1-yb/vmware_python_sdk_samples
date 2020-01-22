# -*- coding: utf-8 -*-
""" Common utils for vmware"""

from ..logger import CustomLogger
from pyVmomi import vim
from pyVmomi import vmodl

LOG = CustomLogger(__name__)


def wait_for_tasks(service_instance, tasks):
    """Given the service instance si and tasks, it returns after all the
       tasks are complete
    Args:
        service_instance (vim.ServiceInstance) : root object for vcenter
                    inventory traversal
        tasks (vim.Task) : (create/ update/ delete etc) tasks to wait for completion
    Returns:
    Raises:
   """
    property_collector = service_instance.content.propertyCollector
    task_list = [str(task) for task in tasks]

    # Create filter
    obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task) for task in tasks]
    property_spec = vmodl.query.PropertyCollector.PropertySpec(
        type=vim.Task, pathSet=[], all=True
    )
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_specs
    filter_spec.propSet = [property_spec]
    pcfilter = property_collector.CreateFilter(filter_spec, True)
    try:
        version, state = None, None

        # Loop looking for updates till the state moves to a completed state.
        while len(task_list):
            update = property_collector.WaitForUpdates(version)
            for filter_set in update.filterSet:
                for obj_set in filter_set.objectSet:
                    task = obj_set.obj
                    for change in obj_set.changeSet:
                        if change.name == "info":
                            state = change.val.state
                        elif change.name == "info.state":
                            state = change.val
                        else:
                            continue
                        if state == vim.TaskInfo.State.success:

                            # Remove task from taskList
                            task_list.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            LOG.info(task.info.error.msg)
                            raise task.info.error

            # Move to next version
            version = update.version
    finally:
        if pcfilter:
            pcfilter.Destroy()


def get_obj(content, vimtype, name, _in=None):
    """
    Return an object by name, if name is None the
    first found object is returned
    Args:
        content (vim.ServiceInstanceContent) : service content object
        vimtype (str) : type of managed object to be retrieved
        name (str) : name of the managed object to be retrieved
        _in (vim.ManagedEntity) : Instance where the object is to be searched
    Returns:
        if found, managed object of type vimtype is returned, else none
    """
    if not name:
        return None

    if not _in:
        _in = content.rootFolder

    container = content.viewManager.CreateContainerView(_in, vimtype, True)
    for c in container.view:
        if c.name == name:
            return c
    return None


def collect_properties(
    service_instance, view_ref, obj_type, path_set=None, include_mors=False
):
    """
    Collect properties for managed objects from a view ref
    Args:
        service_instance (vim.ServiceInstance): ServiceInstance connection
        view_ref (vim.view.*): Starting point of inventory navigation
        obj_type (vim.*): Type of managed object
        path_set (list): List of properties to retrieve
        include_mors (bool): If True include the managed objects
                                       refs in the result
    Returns:
        A list of properties for the managed objects
    """
    collector = service_instance.content.propertyCollector

    # Create object specification to define the starting point of
    # inventory navigation
    obj_spec = vmodl.query.PropertyCollector.ObjectSpec()
    obj_spec.obj = view_ref
    obj_spec.skip = True

    # Create a traversal specification to identify the path for collection
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec()
    traversal_spec.name = "traverseEntities"
    traversal_spec.path = "view"
    traversal_spec.skip = False
    traversal_spec.type = view_ref.__class__
    obj_spec.selectSet = [traversal_spec]

    # Identify the properties to the retrieved
    property_spec = vmodl.query.PropertyCollector.PropertySpec()
    property_spec.type = obj_type

    if not path_set:
        property_spec.all = True

    property_spec.pathSet = path_set

    # Add the object and property specification to the
    # property filter specification
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = [obj_spec]
    filter_spec.propSet = [property_spec]

    # Retrieve properties
    props = collector.RetrieveContents([filter_spec])

    data = []
    for obj in props:
        properties = {}
        for prop in obj.propSet:
            properties[prop.name] = prop.val

        if include_mors:
            properties["obj"] = obj.obj

        data.append(properties)
    return data


def get_container_view(service_instance, obj_type, container=None):
    """
    Get a vSphere Container View reference to all objects of type 'obj_type'
    It is up to the caller to take care of destroying the View when no longer
    needed.
    Args:
        service_instance (vim.ServiceInstance) : root object for invenory traversal
        obj_type (list): A list of managed object types
        container (vim.ManagedEntity) : The object that the view presents
    Returns:
        (vim.view.ContainerView) : A container view ref to the discovered managed objects
    """
    if not container:
        container = service_instance.content.rootFolder

    view_ref = service_instance.content.viewManager.CreateContainerView(
        container=container, type=obj_type, recursive=True
    )
    return view_ref


def get_objects_by_prop(service_instance, prop, obj_type, obj_value, container=None):
    """
    Get the vSphere object with the specified property
    Args:
        service_instance (vim.ServiceInstance) : root object for inventory traversal
        prop (str): name of the property
        obj_type (str): type of a managed object
        obj_value (str): value of a managed object that needs to be matched
        container (vim.ManagedEntity): The object that the view presents
    Returns:
        (vim.ManagedEntity) ; First Object that match the value
    """

    view = get_container_view(
        service_instance, obj_type=[obj_type], container=container
    )
    props = [prop]
    obj_details = collect_properties(
        service_instance,
        view_ref=view,
        obj_type=obj_type,
        path_set=props,
        include_mors=True,
    )
    try:
        obj = [ob.pop("obj") for ob in obj_details if ob.get(prop) == obj_value][0]
    except IndexError:
        raise Exception(
            "Failed to fetch VMware object: '{0}' with {1}: '{2}'".format(
                obj_type.__name__, prop, obj_value
            )
        )

    return obj
