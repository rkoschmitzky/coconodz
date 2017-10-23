# CocoNodz
A unified and configurable Nodegraph wrapper for Visual Effects Applications

<br>

## Project Gloals
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
| Tab              | opens the node creation widget
| F                | focus selected nodes
| Ctrl + S         | opens the node search widget
| L                | layouts selected nodes

---
<br>

## Available Host Integrations

CocoNodz offers integrations for the following Applications

- Autodesk Maya
- The Foundry Katana
 

<br>

### Standalone Nodzgraph


<br>

### Maya Nodzgraph Integration

#### How to install the CocoNodz Maya plugin

To use CocoNodz within Maya you simple have to add the following paths to your environment.

```
COCONODZ_STARTUP = <path to coconodz root>
MAYA_PLUG_IN_PATH = <path to coconodz root>\etc\maya\plugin
```

Launch Maya and load the coconodz.py plugin. After successful initizalization you should be able to see a CocoNodz menu in Maya's menubar.

### Katana Nodzgraph Integration

---
