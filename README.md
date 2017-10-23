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

- only use a single nodegraph between different applications, OSX, linux, Windows
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
| Ctrl + RMB       | opens the context-aware attribute tree widget, when executed over node
| Alt + RMB        | zooms in and out the nodegraph canvas
| Tab              | opens the node creation widget
| F                | focus selected nodes
| Ctrl + S         | opens the node search widget
| L                | layouts selected nodes

---
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

