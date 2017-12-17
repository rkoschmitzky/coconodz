# CocoNodz
A unified and configurable Nodegraph wrapper for Visual Effects Applications


## Table of Contents

- [Project Goals](#project-goals)
- [Documentation](#documentation)
   - [Environment Variables](#required-or-useful-environment-variables)
   - [Nodegraph Hotkeys](#nodegraph-hotkeys)
- [Integrations](#integrations)
   - [Standalone](#standalone)
   - [Autodesk Maya Integration](#autodesk-maya-integration)
   - [The Foundry Katana Integration](#the-foundry-katana-integration)

<br>

## Project Goals
CocoNodz aims to provide a simple framework to integrate a unified and flexible Nodegraph into applications that supports Python and PyQt/PySide.
Main Goals:

- use a single nodegraph between different applications and plattforms on OSX, linux, Windows
- customize and extend it where native applications nodegraph are lacking functionality or limiting customizability
- provide a simple system for users to extend it with custom code snippets
- load and share shading networks

<br>

### Documentation

<br>

#### Required or useful environment variables
| Environment variable    | Type  | Description
|:------------------------|:------|:------------
| COCONODZ_STARTUP        | str   | root path to coconodz, will be needed for any host integration
| COCONODZ_IGNORE_HOST    | bool  |coconodz is able to detect the host application, set this to 1 if you want to use it without any host integration
| QT_PREFERRED_BINDING    | str   | specifies the preferred Qt binding

#### Nodegraph hotkeys

| Default Shortcut | Description
|:-----------------|:------------
| RMB              | opens the context-aware graph widget
| Alt + RMB        | zooms in and out the nodegraph canvas
| Tab              | opens the node creation widget
| F                | focus selected nodes
| Ctrl + S         | opens the node search widget
| L                | layouts selected nodes

---
<br>

#### overall configuration

| Value                            |  Type  |Description
|:---------------------------------|:-------|:------------
| output_verbosity                 | string | logging verbosity, supported are "critical", "error", "warning", "info", "debug"
| scene_width                      | int    | default graph width
| scene_height                     | int    | default graph height
| grid_size                        | int    | default graph grid size
| antialiasing                     | bool   |
| antialiasing_boost               | bool   |
| smooth_pixmap                    | bool   |
| attribute_order                  | string | attribute creation order, supported are "top", "bottom", "alphabetical"
| available_node_types             | list   | the nodetypes that will be available in the creation field widget by default
| default_attribute_name           | string | name of the default attribute
| default_attribute_data_type      | string | datatype of the default attribute
| default_socket                   | bool   | if true it will add the attribute as socket
| default_plug                     | bool   | if true it will add the attribute as plug
| node_font                        | string | font used for all nodes
| node_font_size                   | int    | font size used for all nodes
| attr_font                        | string | font used for all attributes
| attr_font_size                   | int    | font size used for all attributes
| mouse_bounding_box               | int    |
| node_width                       | int    | default node width
| node_height                      | int    | default node height
| node_radius                      | int    | default node radius
| node_border                      | int    | default node border size
| node_attr_height                 | int    | default attribute height
| connection_width                 | int    | default connection pixel width
| alternate_value                  | int    | alternates background color on attributes
| grid_color                       | list   | color the canvas grid will use
| slot_border                      | list   |
| non_connectable_color            | list   | color the connection will use when attributes are not connectable, RGBA color list 0-255
| connection_highlight:color       | list   | color when hovering over a connection, RGBA color list 0-255
| connection_text_color            | list   | text color when hovering over a connection, RGBA color list 0-255
| connection_interpolation         | string | connection shape, "bezier", linear
| connection_inherit_datatype_color| bool   | if true connection will use the color specified for data type
| connection_color                 | list   | default color the connection when not inheriting the data type color, RGBA color list 0-255
| layout_margin_size               | int    |
| backdrop color                   | list   | default backdrop color, RGBA color list 0-255
| backdrop_border_color            | list   | default backdrop border color, RGBA color list 0-255
| backdrop_bounds                  | list   | default position and size of a backdrop, x, y, width, height
| backdrop_title_font_size         | int    | default font size for backdrop titles
| backdrop_description_font_size   | int    | default font size for backdrop descriptions
| backdrop_font                    | int    | default backdrop title and description font

<br>

#### node configuration

The configuration color configuration per node type, it needs to start with node_ followed by the nodetype and must include
specific values.

| Value                            |  Type  |Description
|:---------------------------------|:-------|:------------
| bg                               | list   | node color, RGBA color list 0-255
| border                           | list   | node border color when node is unselected, RGBA color list 0-255
| border_sel                       | list   | node border color when node is selected, RGBA color list 0-255
| text                             | list   | node text color, RGBA color list 0-255

**node_default** will be used for all unspecified node types

<br>

#### attribute configuration

Same as in the node configuration color configuration per attribute data type can be specified, it needs to start with attr_ followed by the nodetype and must include
specific values.

| Value                            |  Type  |Description
|:---------------------------------|:-------|:------------
| bg                               | list   | attribute background color, RGBA color list 0-255
| text                             | list   | attribute text color, RGBA color list 0-255
| plug                             | list   | attribute plug color, RGBA color list 0-255
| socket                           | list   | attribute slot color,  RGBA color list 0-255

<br>


### reserved node types

#### backdrop

CocoNodz is supporting backdrop nodes to help grouping nodes, similar to backdrops in The Foundry's Nuke.

#### dot

Dot nodes are planned...

<br>

## Integrations
CocoNodz offers integrations for the following Applications

- [Autodesk Maya Integration](#autodesk-maya-integration)
- [The Foundry Katana Integration](#the-foundry-katana-integration)
 

<br>

### Standalone


<br>

### Autodesk Maya Integration

#### How to install the CocoNodz Maya plugin

To use CocoNodz within Maya you have to add the following paths to your environment.

```
COCONODZ_STARTUP=<path to coconodz root>
MAYA_PLUG_IN_PATH=<path to coconodz root>\etc\maya\plugin
```

#### maya configuration

The Maya integration allows additional configurations

| Value                            |  Type  |Description
|:---------------------------------|:-------|:------------
| docked                           | bool   | specified if the window will be dockable or not
| dock_area                        | string | specifies the default dock area when the nodegraph will be docked
| allowed_dock_areas               | string | specifies if the dockable window can be docked left, right or everywhere, supported are "left", "right", "all"
| floating                         | bool   | specifies is the window will be docked or float
| width                            | int    | default width of the window
| height                           | int    | default height of the window
| available_node_categories        | list   | will add multiple node types based on the node type categories, e.g: "shader", "texture"


Launch Maya and load the coconodz.py plugin. After successful initizalization you should be able to see a CocoNodz menu in Maya's menubar.

### The Foundry Katana Integration

To use CocoNodz within Katana you have to add the following paths to your environment.

```
QT_PREFERRED_BINDING=PyQt4
QT_SIP_API_HINT=1
COCONODZ_STARTUP<path to coconodz root>\coconodz
KATANA_RESOURCES<path to coconodz root>\etc\katana
```

---

