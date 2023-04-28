# Goto paths

Plugin for Sublime Text 3+4.

## Features

### Clickable paths

* Highlights paths like
  * `backpack::crud.partials.xxx`
  * `EXT:my_extension/Resources/Private/Templates/MyTemplate.html`
* Provides a command to open such a file (can be triggered by click or shortcut)

## Key binding

```User/Default (Linux).sublime-keymap
{ "keys": ["ctrl+alt+enter"], "command": "open_path_under_cursor" }
```

## Mouse binding

```User/Default (Linux).sublime-mousemap
[
    {
        "button": "button1",
        "count": 1,
        "modifiers": ["ctrl"],
        "press_command": "drag_select",
        "command": "open_path_under_cursor"
    }
]
```
